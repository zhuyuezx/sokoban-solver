"""Auto-generated heuristic."""
# metadata: {"iteration": 8, "total_nodes": 109883, "solved": 49}
from sokoban_solver import Board, Pos

from __future__ import annotations
from collections import deque
from functools import lru_cache

# reuse the direction list from the main solver
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left


@lru_cache(maxsize=None)
def _push_distance_maps(
    walls: frozenset[Pos], goals: tuple[Pos, ...]
) -> tuple[frozenset[tuple[Pos, int]], ...]:
    """
    For each goal, return a frozenset of (Pos, distance) pairs where distance is
    the minimum number of pushes needed to move a box from that Pos to the goal,
    ignoring other boxes (only walls block).  Cached for speed.
    """
    maps: list[frozenset[tuple[Pos, int]]] = []
    for g in goals:
        dist: dict[Pos, int] = {}
        q: deque[tuple[Pos, int]] = deque([(g, 0)])
        visited: set[Pos] = set()
        while q:
            p, d = q.popleft()
            if p in visited:
                continue
            visited.add(p)
            dist[p] = d
            for dx, dy in DIRECTIONS:
                # reverse a push: previous box location and player standing cell
                prev = Pos(p.x - dx, p.y - dy)
                player = Pos(p.x - 2 * dx, p.y - 2 * dy)
                if prev in walls or player in walls:
                    continue
                if prev not in visited:
                    q.append((prev, d + 1))
        maps.append(frozenset(dist.items()))
    return tuple(maps)


def heuristic(board: Board, boxes: tuple[Pos, ...]) -> int:
    """
    Admissible heuristic:
      1. Simple corner deadlock detection (already in original solver).
      2. Push‑distance based optimal assignment:
         – pre‑compute, per goal, the minimum number of pushes from any square
           to that goal (ignoring other boxes);
         – build a distance matrix box→goal using those values;
         – solve the assignment optimally with DP over subsets.
    The result is a lower bound on the remaining pushes.
    """
    # ---- 1. Corner deadlock (same as earlier heuristic) -----------------
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
            return 10_000  # dead position – large admissible penalty

    # ---- 2. Push‑distance based assignment -------------------------------
    # retrieve (cached) distance maps for this board
    maps_frozen = _push_distance_maps(board.walls, board.goals)
    # turn each frozenset into a dict for fast lookup
    maps = [dict(m) for m in maps_frozen]

    n = len(boxes)
    m = len(board.goals)          # usually n == m
    INF = 10 ** 9

    # build distance matrix (push distance, not Manhattan)
    dist = [[INF] * m for _ in range(n)]
    for i, bx in enumerate(boxes):
        for j in range(m):
            d = maps[j].get(bx, INF)
            dist[i][j] = d

    # any box that cannot reach any goal -> deadlock
    for i in range(n):
        if all(dist[i][j] == INF for j in range(m)):
            return 10_000

    # optimal one‑to‑one assignment via DP over subsets (Hungarian not needed)
    @lru_cache(maxsize=None)
    def dp(i: int, mask: int) -> int:
        """minimum total push cost for boxes[i:] given used goals in mask."""
        if i == n:
            return 0
        best = INF
        for j in range(m):
            if mask & (1 << j):
                continue
            d = dist[i][j]
            if d == INF:
                continue  # skip impossible pair
            cand = d + dp(i + 1, mask | (1 << j))
            if cand < best:
                best = cand
        return best

    return dp(0, 0)
