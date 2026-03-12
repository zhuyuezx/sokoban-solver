"""
LLM-driven Sokoban A* heuristic optimizer.

Pipeline:
  1. Run baseline heuristic on a set of levels → record nodes explored
  2. Build LLM prompt with solver source + baseline trace data
  3. LLM generates an improved heuristic function
  4. Validate & test new heuristic on same levels
  5. Accept if total nodes explored decreases; reject otherwise
  6. Iterate

The metric is **total nodes explored** across the benchmark levels.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import textwrap
import time
import traceback
from pathlib import Path
from typing import Any

# Ensure sokoban_solver is importable
_SOLVER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SOLVER_DIR))

from sokoban_solver import (
    Board, Pos, HeuristicFn, SolveResult,
    solve, load_levels,
    naive_manhattan, greedy_matching, enhanced_heuristic,
)


# ── Benchmark runner ─────────────────────────────────────────────────

def benchmark(
    heuristic: HeuristicFn,
    levels: list[tuple[str, str]],
    time_limit_s: float = 10.0,
    max_nodes: int = 200_000,
) -> list[dict[str, Any]]:
    """Run heuristic on all levels, return per-level results."""
    results = []
    for name, grid in levels:
        board = Board.from_string(grid)
        r = solve(board, heuristic=heuristic, time_limit_s=time_limit_s,
                  max_nodes=max_nodes)
        results.append({
            "level": name,
            "solved": r.solved,
            "nodes": r.nodes_explored,
            "time_ms": round(r.time_ms, 1),
            "pushes": r.pushes,
            "solution": r.solution if r.solved else None,
            "fail_reason": r.fail_reason,
        })
    return results


def summarize(results: list[dict]) -> dict[str, Any]:
    solved = sum(1 for r in results if r["solved"])
    total_nodes = sum(r["nodes"] for r in results)
    total_time = sum(r["time_ms"] for r in results)
    return {
        "solved": solved,
        "total": len(results),
        "total_nodes": total_nodes,
        "total_time_ms": round(total_time, 1),
        "avg_nodes": round(total_nodes / len(results)) if results else 0,
    }


# ── LLM interaction ─────────────────────────────────────────────────

def _load_solver_source() -> str:
    """Load the solver source for inclusion in LLM prompts."""
    path = _SOLVER_DIR / "sokoban_solver.py"
    return path.read_text(encoding="utf-8")


def _build_prompt(
    current_source: str,
    baseline_results: list[dict],
    baseline_summary: dict,
    iteration: int,
    history: list[dict] | None = None,
) -> str:
    """Build the LLM prompt for heuristic improvement."""
    # Format per-level results as a compact table
    table_lines = []
    for r in baseline_results:
        status = "SOLVED" if r["solved"] else f"FAIL({r['fail_reason']})"
        table_lines.append(
            f"  {r['level']:30s} {status:20s} "
            f"nodes={r['nodes']:>8,}  time={r['time_ms']:>8.1f}ms"
        )
    table = "\n".join(table_lines)

    # History of previous attempts
    history_section = ""
    if history:
        hist_lines = []
        for h in history[-3:]:  # last 3 attempts
            accepted = "ACCEPTED" if h.get("accepted") else "REJECTED"
            hist_lines.append(
                f"  Iteration {h['iteration']}: {accepted}  "
                f"nodes={h['total_nodes']:,}  "
                f"solved={h['solved']}/{h['total']}"
            )
            if h.get("reasoning"):
                hist_lines.append(f"    Reasoning: {h['reasoning'][:200]}")
        history_section = (
            "\n--- PREVIOUS ATTEMPTS ---\n" + "\n".join(hist_lines) + "\n"
        )

    return textwrap.dedent(f"""\
You are an expert AI researcher optimizing the heuristic function for an
A* Sokoban solver.  Your goal: minimize the total number of nodes explored
while maintaining correctness (all previously solved levels must still solve).

--- SOLVER SOURCE ---
```python
{_load_solver_source()}
```

--- CURRENT HEURISTIC ---
```python
{current_source}
```

--- BASELINE PERFORMANCE (iteration {iteration}) ---
Summary: {baseline_summary['solved']}/{baseline_summary['total']} solved, \
{baseline_summary['total_nodes']:,} total nodes, \
{baseline_summary['total_time_ms']:.0f}ms total time

Per-level results:
{table}
{history_section}
--- TASK ---
Write an improved heuristic function with this EXACT signature:

```python
def heuristic(board: Board, boxes: tuple[Pos, ...]) -> int:
    ...
```

Rules:
1. The function receives a Board object and a tuple of current box positions.
2. Board has: .walls (frozenset[Pos]), .goals (tuple[Pos, ...]),
   .width, .height, .player (Pos — but DO NOT use player position in
   heuristic, it changes with each state).
3. Pos has: .x, .y, .manhattan(other) method.
4. The return value must be an integer >= 0 (estimated remaining pushes).
5. The heuristic MUST be admissible: h(s) <= h*(s) for A* to find
   optimal solutions. Never overestimate.
6. You may use: manhattan distance, matching algorithms,
   deadlock detection, penalty terms — as long as you don't overestimate.
7. Focus on levels with high node counts — those are where better
   heuristics make the biggest difference.
8. Do NOT import external packages. Only use builtins + the types above.

Return ONLY the Python function in a code block. No explanation needed.
""")


def _extract_function(response: str) -> str | None:
    """Extract the heuristic function source from LLM response."""
    # Find python code blocks
    pattern = r"```python\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    for match in matches:
        if "def heuristic(" in match:
            return match.strip()
    # Fallback: look for bare function definition
    if "def heuristic(" in response:
        lines = response.split("\n")
        start = None
        for i, line in enumerate(lines):
            if "def heuristic(" in line:
                start = i
                break
        if start is not None:
            func_lines = [lines[start]]
            for line in lines[start + 1:]:
                if line.strip() and not line[0].isspace() and not line.strip().startswith("#"):
                    break
                func_lines.append(line)
            return "\n".join(func_lines).strip()
    return None


def _compile_heuristic(source: str) -> HeuristicFn | None:
    """Compile heuristic source code into a callable."""
    # Build execution namespace with necessary types
    namespace: dict[str, Any] = {
        "Board": Board,
        "Pos": Pos,
    }
    try:
        exec(source, namespace)  # noqa: S102
        fn = namespace.get("heuristic")
        if fn is None or not callable(fn):
            return None
        return fn
    except Exception:
        return None


# ── Main optimizer loop ──────────────────────────────────────────────

class HeuristicOptimizer:
    """
    Iterative LLM-based heuristic optimizer for Sokoban A*.

    Parameters
    ----------
    levels : list[tuple[str, str]]
        (name, grid_text) pairs to benchmark on.
    num_iters : int
        Number of LLM improvement iterations.
    time_limit_s : float
        Per-level solve time limit.
    max_nodes : int
        Per-level node budget.
    verbose : bool
        Print progress.
    """

    def __init__(
        self,
        levels: list[tuple[str, str]],
        num_iters: int = 10,
        time_limit_s: float = 10.0,
        max_nodes: int = 200_000,
        verbose: bool = True,
    ):
        self.levels = levels
        self.num_iters = num_iters
        self.time_limit_s = time_limit_s
        self.max_nodes = max_nodes
        self.verbose = verbose

        self.history: list[dict] = []
        self.best_source: str = ""
        self.best_fn: HeuristicFn = enhanced_heuristic
        self.best_results: list[dict] = []
        self.best_summary: dict = {}

        # All results for webpage visualization
        self.all_iterations: list[dict] = []

    def _query_llm(self, prompt: str) -> str:
        """Query OpenAI-compatible LLM. Uses Tool_Creation's querier."""
        try:
            # Try to use the existing LLM querier infrastructure
            tc_dir = Path(__file__).resolve().parent.parent / "Tool_Creation"
            if str(tc_dir) not in sys.path:
                sys.path.insert(0, str(tc_dir))
            from LLM.llm_querier import LLMQuerier
            querier = LLMQuerier()
            result = querier.query(prompt, step_name="heuristic_optimization")
            return result.get("response", "")
        except Exception as e:
            if self.verbose:
                print(f"  LLM query failed: {e}")
            raise

    def run(self) -> dict[str, Any]:
        """Run the full optimization loop."""
        import inspect

        if self.verbose:
            print(f"=== Heuristic Optimizer: {self.num_iters} iterations, "
                  f"{len(self.levels)} levels ===\n")

        # Baseline: enhanced heuristic
        self.best_source = inspect.getsource(enhanced_heuristic)
        self.best_fn = enhanced_heuristic
        self.best_results = benchmark(
            self.best_fn, self.levels,
            self.time_limit_s, self.max_nodes,
        )
        self.best_summary = summarize(self.best_results)

        self.all_iterations.append({
            "iteration": 0,
            "name": "enhanced (baseline)",
            "source": self.best_source,
            "results": self.best_results,
            "summary": self.best_summary,
            "accepted": True,
        })

        if self.verbose:
            s = self.best_summary
            print(f"Baseline: {s['solved']}/{s['total']} solved, "
                  f"{s['total_nodes']:,} nodes\n")

        for i in range(1, self.num_iters + 1):
            if self.verbose:
                print(f"--- Iteration {i}/{self.num_iters} ---")

            # Build prompt
            prompt = _build_prompt(
                current_source=self.best_source,
                baseline_results=self.best_results,
                baseline_summary=self.best_summary,
                iteration=i,
                history=self.history,
            )

            # Query LLM
            try:
                response = self._query_llm(prompt)
            except Exception:
                self.history.append({
                    "iteration": i, "accepted": False,
                    "total_nodes": -1, "solved": 0, "total": len(self.levels),
                    "reasoning": "LLM query failed",
                })
                continue

            # Extract function
            fn_source = _extract_function(response)
            if fn_source is None:
                if self.verbose:
                    print("  Could not extract function from response")
                self.history.append({
                    "iteration": i, "accepted": False,
                    "total_nodes": -1, "solved": 0, "total": len(self.levels),
                    "reasoning": "Could not extract function",
                })
                continue

            # Compile
            fn = _compile_heuristic(fn_source)
            if fn is None:
                if self.verbose:
                    print("  Function failed to compile")
                self.history.append({
                    "iteration": i, "accepted": False,
                    "total_nodes": -1, "solved": 0, "total": len(self.levels),
                    "reasoning": "Compile error",
                })
                continue

            # Benchmark
            try:
                new_results = benchmark(
                    fn, self.levels,
                    self.time_limit_s, self.max_nodes,
                )
            except Exception as e:
                if self.verbose:
                    print(f"  Benchmark error: {e}")
                self.history.append({
                    "iteration": i, "accepted": False,
                    "total_nodes": -1, "solved": 0, "total": len(self.levels),
                    "reasoning": f"Runtime error: {e}",
                })
                continue

            new_summary = summarize(new_results)

            # Accept/reject: must solve at least as many AND fewer total nodes
            best_solved = self.best_summary["solved"]
            new_solved = new_summary["solved"]
            accepted = (
                new_solved >= best_solved
                and new_summary["total_nodes"] < self.best_summary["total_nodes"]
            )

            iter_record = {
                "iteration": i,
                "name": f"llm_iter_{i}",
                "source": fn_source,
                "results": new_results,
                "summary": new_summary,
                "accepted": accepted,
            }
            self.all_iterations.append(iter_record)

            self.history.append({
                "iteration": i,
                "accepted": accepted,
                "total_nodes": new_summary["total_nodes"],
                "solved": new_solved,
                "total": new_summary["total"],
                "reasoning": (
                    f"nodes {self.best_summary['total_nodes']:,} → "
                    f"{new_summary['total_nodes']:,}"
                ),
            })

            if self.verbose:
                mark = "ACCEPT" if accepted else "REJECT"
                print(
                    f"  [{mark}] solved={new_solved}/{new_summary['total']} "
                    f"nodes={new_summary['total_nodes']:,} "
                    f"(was {self.best_summary['total_nodes']:,})"
                )

            if accepted:
                self.best_source = fn_source
                self.best_fn = fn
                self.best_results = new_results
                self.best_summary = new_summary

        if self.verbose:
            print(f"\n=== Done. Best: {self.best_summary} ===")

        return {
            "best_source": self.best_source,
            "best_summary": self.best_summary,
            "best_results": self.best_results,
            "all_iterations": self.all_iterations,
            "history": self.history,
        }

    def save_results(self, path: str | Path = "optimization_results.json"):
        """Save all results to JSON for the comparison webpage."""
        # Also run baselines for comparison
        baselines: dict[str, list[dict]] = {}
        for name, fn in [
            ("naive_manhattan", naive_manhattan),
            ("greedy_matching", greedy_matching),
            ("enhanced", enhanced_heuristic),
        ]:
            baselines[name] = benchmark(
                fn, self.levels, self.time_limit_s, self.max_nodes,
            )

        data = {
            "levels": [name for name, _ in self.levels],
            "baselines": {
                name: {"results": res, "summary": summarize(res)}
                for name, res in baselines.items()
            },
            "iterations": [
                {
                    "iteration": it["iteration"],
                    "name": it["name"],
                    "source": it["source"],
                    "results": it["results"],
                    "summary": it["summary"],
                    "accepted": it["accepted"],
                }
                for it in self.all_iterations
            ],
            "best": {
                "source": self.best_source,
                "summary": self.best_summary,
            },
        }

        Path(path).write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
        if self.verbose:
            print(f"Results saved to {path}")


# ── CLI ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    levels = load_levels(_SOLVER_DIR / "grids" / "Microban.txt")
    # Use first 20 levels for faster iteration
    levels = levels[:20]

    optimizer = HeuristicOptimizer(levels=levels, num_iters=10)
    result = optimizer.run()
    optimizer.save_results("optimization_results.json")
