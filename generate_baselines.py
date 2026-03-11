"""
Generate baseline benchmark results for the comparison webpage.
Runs all 3 built-in heuristics on Microban levels and saves JSON.
"""

from pathlib import Path
from sokoban_solver import (
    Board, load_levels, solve,
    naive_manhattan, greedy_matching, enhanced_heuristic,
)
from heuristic_optimizer import benchmark, summarize
import json, inspect, time

GRID_FILE = Path(__file__).parent / "grids" / "Microban.txt"
OUT_FILE = Path(__file__).parent / "optimization_results.json"
NUM_LEVELS = 30  # first N levels


def main():
    levels = load_levels(GRID_FILE)[:NUM_LEVELS]
    print(f"Benchmarking {len(levels)} levels...\n")

    baselines = {}
    for name, fn in [
        ("naive_manhattan", naive_manhattan),
        ("greedy_matching", greedy_matching),
        ("enhanced", enhanced_heuristic),
    ]:
        t0 = time.perf_counter()
        results = benchmark(fn, levels, time_limit_s=15.0, max_nodes=300_000)
        dt = time.perf_counter() - t0
        s = summarize(results)
        baselines[name] = {"results": results, "summary": s}
        print(f"  {name:25s}: {s['solved']}/{s['total']} solved  "
              f"nodes={s['total_nodes']:>10,}  time={dt:.1f}s")

    # Use enhanced as "iteration 0" baseline
    data = {
        "levels": [name for name, _ in levels],
        "baselines": baselines,
        "iterations": [
            {
                "iteration": 0,
                "name": "enhanced (baseline)",
                "source": inspect.getsource(enhanced_heuristic),
                "results": baselines["enhanced"]["results"],
                "summary": baselines["enhanced"]["summary"],
                "accepted": True,
            }
        ],
        "best": {
            "source": inspect.getsource(enhanced_heuristic),
            "summary": baselines["enhanced"]["summary"],
        },
    }

    OUT_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(f"\nSaved to {OUT_FILE}")


if __name__ == "__main__":
    main()
