"""
Python Sokoban A* Solver with pluggable heuristic.

Mirrors the Rust festival-rust solver logic but allows swapping
the heuristic function at runtime — enabling LLM-driven optimization.

The key metric is **nodes_explored**: fewer nodes = better heuristic.
"""

from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ── Data types ────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True, order=True)
class Pos:
    x: int
    y: int

    def manhattan(self, other: Pos) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
DIR_CHARS_LOWER = "urdl"
DIR_CHARS_UPPER = "URDL"


@dataclass
class Board:
    width: int
    height: int
    walls: frozenset[Pos]
    goals: tuple[Pos, ...]
    player: Pos
    boxes: tuple[Pos, ...]

    @classmethod
    def from_string(cls, text: str) -> "Board":
        lines = [l.rstrip() for l in text.splitlines() if l.strip()]
        height = len(lines)
        width = max(len(l) for l in lines) if lines else 0

        walls: set[Pos] = set()
        goals: list[Pos] = []
        boxes: list[Pos] = []
        player: Pos | None = None

        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                p = Pos(x, y)
                if ch == "#":
                    walls.add(p)
                elif ch == ".":
                    goals.append(p)
                elif ch == "@":
                    player = p
                elif ch == "+":
                    goals.append(p)
                    player = p
                elif ch == "$":
                    boxes.append(p)
                elif ch == "*":
                    goals.append(p)
                    boxes.append(p)

        if player is None:
            raise ValueError("No player (@) found")
        if not boxes:
            raise ValueError("No boxes ($) found")
        if len(boxes) != len(goals):
            raise ValueError(
                f"Box/goal mismatch: {len(boxes)} boxes, {len(goals)} goals"
            )

        return cls(
            width=width,
            height=height,
            walls=frozenset(walls),
            goals=tuple(goals),
            player=player,
            boxes=tuple(boxes),
        )


# ── State for A* ─────────────────────────────────────────────────────

@dataclass
class Move:
    box_index: int
    box_from: Pos
    box_to: Pos
    player_path: list[int]  # direction indices for player walk
    direction: int           # push direction index


@dataclass(order=False)
class State:
    f: int                   # g + h  (for heap ordering)
    h: int
    g: int
    player: Pos
    boxes: tuple[Pos, ...]
    moves: tuple[Move, ...]

    def __lt__(self, other: "State") -> bool:
        if self.f != other.f:
            return self.f < other.f
        return self.h < other.h

    def hash_key(self) -> tuple:
        return (self.player, tuple(sorted(self.boxes)))


# ── BFS reachability (player pathfinding around boxes) ────────────────

def _bfs_path(
    walls: frozenset[Pos],
    box_set: frozenset[Pos],
    start: Pos,
    goal: Pos,
    width: int,
    height: int,
) -> list[int] | None:
    """BFS for player path from *start* to *goal*, avoiding walls & boxes."""
    if start == goal:
        return []
    visited = {start}
    queue: deque[tuple[Pos, list[int]]] = deque([(start, [])])
    while queue:
        pos, path = queue.popleft()
        for di, (dx, dy) in enumerate(DIRECTIONS):
            np = Pos(pos.x + dx, pos.y + dy)
            if np in visited or np in walls or np in box_set:
                continue
            if np.x < 0 or np.y < 0 or np.x >= width or np.y >= height:
                continue
            if np == goal:
                return path + [di]
            visited.add(np)
            queue.append((np, path + [di]))
    return None


# ── Simple deadlock: corner detection ────────────────────────────────

def _precompute_corner_deadlocks(board: Board) -> frozenset[Pos]:
    """Positions that are corners (two adjacent walls) and NOT goals."""
    goal_set = frozenset(board.goals)
    dead: set[Pos] = set()
    for y in range(board.height):
        for x in range(board.width):
            p = Pos(x, y)
            if p in board.walls or p in goal_set:
                continue
            up = Pos(x, y - 1) in board.walls
            dn = Pos(x, y + 1) in board.walls
            lt = Pos(x - 1, y) in board.walls
            rt = Pos(x + 1, y) in board.walls
            if (up and lt) or (up and rt) or (dn and lt) or (dn and rt):
                dead.add(p)
    return frozenset(dead)


# ── Heuristic type alias ─────────────────────────────────────────────

HeuristicFn = Callable[[Board, tuple[Pos, ...]], int]


# ── Built-in heuristics ──────────────────────────────────────────────

def naive_manhattan(board: Board, boxes: tuple[Pos, ...]) -> int:
    """Sum of Manhattan distances from each box to nearest goal (with reuse)."""
    total = 0
    for bx in boxes:
        total += min(bx.manhattan(g) for g in board.goals)
    return total


def greedy_matching(board: Board, boxes: tuple[Pos, ...]) -> int:
    """Greedy min-cost matching: assign each box to closest unused goal."""
    used = [False] * len(board.goals)
    total = 0
    for bx in boxes:
        best_dist = 10**9
        best_idx = 0
        for i, g in enumerate(board.goals):
            if used[i]:
                continue
            d = bx.manhattan(g)
            if d < best_dist:
                best_dist = d
                best_idx = i
        used[best_idx] = True
        total += best_dist
    return total


def enhanced_heuristic(board: Board, boxes: tuple[Pos, ...]) -> int:
    """Greedy matching + mobility penalty (mirrors Rust enhanced_heuristic)."""
    base = greedy_matching(board, boxes)
    goal_set = frozenset(board.goals)
    box_set = frozenset(boxes)
    penalty = 0
    for bx in boxes:
        if bx in goal_set:
            continue
        blocked = 0
        for dx, dy in DIRECTIONS:
            nb = Pos(bx.x + dx, bx.y + dy)
            if nb in board.walls or nb in box_set:
                blocked += 1
        if blocked >= 3:
            penalty += 10
        elif blocked == 2:
            penalty += 2
    return base + penalty


# ── A* solver ────────────────────────────────────────────────────────

@dataclass
class SolveResult:
    solved: bool
    solution: str
    moves: int
    pushes: int
    nodes_explored: int
    time_ms: float
    fail_reason: str | None = None


def solve(
    board: Board,
    heuristic: HeuristicFn = enhanced_heuristic,
    time_limit_s: float = 30.0,
    max_nodes: int = 500_000,
) -> SolveResult:
    """Run A* on *board* using *heuristic*.  Returns SolveResult."""
    t0 = time.perf_counter()
    corner_dead = _precompute_corner_deadlocks(board)
    goal_set = frozenset(board.goals)

    h0 = heuristic(board, board.boxes)
    init = State(
        f=h0, h=h0, g=0,
        player=board.player,
        boxes=board.boxes,
        moves=(),
    )

    open_heap: list[State] = [init]
    closed: set[tuple] = set()
    nodes = 0

    while open_heap:
        cur = heapq.heappop(open_heap)
        nodes += 1

        if nodes % 5000 == 0:
            elapsed = time.perf_counter() - t0
            if elapsed > time_limit_s:
                return SolveResult(
                    solved=False, solution="", moves=0, pushes=0,
                    nodes_explored=nodes,
                    time_ms=elapsed * 1000,
                    fail_reason="Time limit exceeded",
                )
        if nodes > max_nodes:
            elapsed = time.perf_counter() - t0
            return SolveResult(
                solved=False, solution="", moves=0, pushes=0,
                nodes_explored=nodes,
                time_ms=elapsed * 1000,
                fail_reason="Node limit exceeded",
            )

        # Goal check
        if all(b in goal_set for b in cur.boxes):
            elapsed = time.perf_counter() - t0
            sol = _reconstruct(cur.moves)
            pushes = sum(1 for c in sol if c.isupper())
            return SolveResult(
                solved=True,
                solution=sol,
                moves=len(sol),
                pushes=pushes,
                nodes_explored=nodes,
                time_ms=elapsed * 1000,
            )

        key = cur.hash_key()
        if key in closed:
            continue
        closed.add(key)

        box_set = frozenset(cur.boxes)

        # Generate moves (push each box in each direction)
        for bi, bpos in enumerate(cur.boxes):
            for di, (dx, dy) in enumerate(DIRECTIONS):
                new_bpos = Pos(bpos.x + dx, bpos.y + dy)

                # Validate new box position
                if new_bpos in board.walls or new_bpos in box_set:
                    continue

                # Corner deadlock
                if new_bpos in corner_dead:
                    continue

                # Player must stand on opposite side of push
                push_from = Pos(bpos.x - dx, bpos.y - dy)
                if push_from in board.walls:
                    continue

                # BFS: can player reach push_from?
                path = _bfs_path(
                    board.walls, box_set, cur.player, push_from,
                    board.width, board.height,
                )
                if path is None:
                    continue

                # Build new box tuple
                new_boxes = list(cur.boxes)
                new_boxes[bi] = new_bpos
                new_boxes_t = tuple(new_boxes)

                mv = Move(bi, bpos, new_bpos, path, di)
                new_g = cur.g + 1
                new_h = heuristic(board, new_boxes_t)
                new_state = State(
                    f=new_g + new_h,
                    h=new_h,
                    g=new_g,
                    player=bpos,  # player ends where box was
                    boxes=new_boxes_t,
                    moves=cur.moves + (mv,),
                )
                heapq.heappush(open_heap, new_state)

    elapsed = time.perf_counter() - t0
    return SolveResult(
        solved=False, solution="", moves=0, pushes=0,
        nodes_explored=nodes,
        time_ms=elapsed * 1000,
        fail_reason="No solution found",
    )


def _reconstruct(moves: tuple[Move, ...]) -> str:
    parts: list[str] = []
    for mv in moves:
        for di in mv.player_path:
            parts.append(DIR_CHARS_LOWER[di])
        parts.append(DIR_CHARS_UPPER[mv.direction])
    return "".join(parts)


# ── Level loading ────────────────────────────────────────────────────

def load_levels(path: str | Path) -> list[tuple[str, str]]:
    """Load levels from an XSB file. Returns list of (name, grid_text)."""
    text = Path(path).read_text(encoding="utf-8")
    levels: list[tuple[str, str]] = []
    current_name = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("Level:"):
            if current_lines:
                grid = "\n".join(current_lines)
                if grid.strip():
                    levels.append((current_name, grid))
            # Parse name (strip cached solution after |)
            name = line[len("Level:"):].strip()
            if "|" in name:
                name = name.split("|")[0].strip()
            current_name = name
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        grid = "\n".join(current_lines)
        if grid.strip():
            levels.append((current_name, grid))

    return levels


# ── CLI / quick test ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    grid_file = sys.argv[1] if len(sys.argv) > 1 else "grids/Microban.txt"
    levels = load_levels(grid_file)

    heuristics: dict[str, HeuristicFn] = {
        "naive_manhattan": naive_manhattan,
        "greedy_matching": greedy_matching,
        "enhanced": enhanced_heuristic,
    }

    print(f"Loaded {len(levels)} levels from {grid_file}\n")
    for name, grid in levels[:10]:
        board = Board.from_string(grid)
        print(f"--- {name} ({len(board.boxes)} boxes) ---")
        for hname, hfn in heuristics.items():
            r = solve(board, heuristic=hfn, time_limit_s=10.0)
            status = "SOLVED" if r.solved else f"FAIL({r.fail_reason})"
            print(
                f"  {hname:25s}: {status}  "
                f"nodes={r.nodes_explored:>8,}  "
                f"time={r.time_ms:>8.1f}ms  "
                f"pushes={r.pushes}"
            )
        print()
