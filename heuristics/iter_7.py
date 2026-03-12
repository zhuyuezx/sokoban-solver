"""Auto-generated heuristic."""
# metadata: {"iteration": 7, "total_nodes": 243355, "solved": 49}
from sokoban_solver import Board, Pos

from __future__ import annotations
from collections import deque
from functools import lru_cache

# ---------- helper: reachable squares for a box (reverse push BFS) ----------
@lru_cache(maxsize=None)
def _push_reachable(walls: frozenset[Pos], goals: tuple[Pos, ...]) -> frozenset[Pos]:
    """Squares from which a box can be pushed to a goal, ignoring other boxes."""
    DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    reachable: set[Pos] = set()
    q = deque(goals)               # start from goal squares (box already solved)

    while q:
        p = q.popleft()
        if p in reachable:
            continue
        reachable.add(p)

        for dx, dy in DIRS:
            # reverse a push: box was at `prev`, player stood at `player`
            prev = Pos(p.x - dx, p.y - dy)
            player = Pos(p.x - 2 * dx, p.y - 2 * dy)

            # both squares must be free of walls for the reverse move to be legal
            if prev in walls or player in walls:
                continue
            if prev not in reachable:
                q.append(prev)

    return frozenset(reachable)


# -------------------------------------------------------------------------
def heuristic(board: Board, boxes: tuple[Pos, ...]) -> int:
    """
    Admissible heuristic:
      1. Detect undeniable deadlocks (corner & frozen dead squares).
      2. Compute the optimal one‑to‑one assignment cost (minimum total
         Manhattan distance) using DP over subsets.
    Returns a lower bound on the remaining number of pushes.
    """
    # ---- 1. Static corner deadlock (already in original) -----------------
    goal_set = frozenset(board.goals)
    walls = board.walls
    for bx in boxes:
        if bx in goal_set:
            continue
        up = Pos(bx.x, bx.y - 1) in walls
        down = Pos(bx.x, bx.y + 1) in walls
        left = Pos(bx.x - 1, bx.y) in walls
        right = Pos(bx.x + 1, bx.y) in walls
        if (up and left) or (up and right) or (down and left) or (down and right):
            return 10_000                     # large but finite penalty

    # ---- 2. Frozen‑square deadlock detection -----------------------------
    reachable = _push_reachable(board.walls, board.goals)
    for bx in boxes:
        if bx not in goal_set and bx not in reachable:
            return 10_000                     # box can never reach any goal

    # ---- 3. Optimal assignment (minimum total Manhattan distance) -------
    n = len(boxes)
    m = len(board.goals)                       # typically n == m
    # distance matrix box i -> goal j
    dist = [[boxes[i].manhattan(board.goals[j]) for j in range(m)] for i in range(n)]

    INF = 10 ** 9

    @lru_cache(maxsize=None)
    def dp(i: int, mask: int) -> int:
        """Minimum cost to assign boxes[i:] given used goals in `mask`."""
        if i == n:
            return 0
        best = INF
        for j in range(m):
            if not (mask & (1 << j)):
                cand = dist[i][j] + dp(i + 1, mask | (1 << j))
                if cand < best:
                    best = cand
        return best

    return dp(0, 0)
