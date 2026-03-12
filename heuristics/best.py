"""Auto-generated heuristic."""
# metadata: {"total_nodes": 104221, "solved": 49}
from __future__ import annotations
from sokoban_solver import Board, Pos

from collections import deque
from functools import lru_cache
from typing import Tuple, FrozenSet

# reuse the direction list from the main solver
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left


@lru_cache(maxsize=None)
def _push_distance_maps(
    walls: FrozenSet["Pos"], goals: Tuple["Pos", ...]
) -> Tuple[FrozenSet[Tuple["Pos", int]], ...]:
    """
    For each goal, return a frozenset of (Pos, distance) pairs where distance is
    the minimum number of pushes needed to move a box from that Pos to the goal,
    ignoring other boxes (only walls block). Cached for speed.
    """
    maps: list[FrozenSet[Tuple[Pos, int]]] = []
    for g in goals:
        dist: dict[Pos, int] = {}
        q: deque[Tuple[Pos, int]] = deque([(g, 0)])
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


def heuristic(board: "Board", boxes: Tuple["Pos", ...]) -> int:
    """
    Admissible heuristic combining:
      1. Corner deadlock detection (large penalty for dead states).
      2. Optimal push‑distance assignment (pre‑computed per‑goal maps + DP).
      3. Simple line‑conflict penalty: each unordered pair of boxes that lie
         on the same row/column with no goal between them adds 1/2 extra push
         (rounded down) to the lower bound.
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
            return 10_000   # dead position – large admissible penalty

    # ---- 2. Push‑distance based optimal assignment -----------------------
    maps_frozen = _push_distance_maps(board.walls, board.goals)
    maps = [dict(m) for m in maps_frozen]        # list of dict Pos->dist

    n = len(boxes)
    m = len(board.goals)                         # usually n == m
    INF = 10 ** 9

    # distance matrix (push distance, ignoring other boxes)
    dist = [[INF] * m for _ in range(n)]
    for i, bx in enumerate(boxes):
        for j in range(m):
            d = maps[j].get(bx, INF)
            dist[i][j] = d

    # any box that cannot reach any goal -> deadlock (large penalty)
    for i in range(n):
        if all(dist[i][j] == INF for j in range(m)):
            return 10_000

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
                continue
            cand = d + dp(i + 1, mask | (1 << j))
            if cand < best:
                best = cand
        return best

    base_cost = dp(0, 0)

    # ---- 3. Simple line‑conflict penalty ---------------------------------
    # count unordered box pairs that share a row or column with no goal between them
    conflict = 0
    # pre‑compute goal positions per row/col for fast lookup
    goals_by_row = {}
    goals_by_col = {}
    for g in board.goals:
        goals_by_row.setdefault(g.y, []).append(g.x)
        goals_by_col.setdefault(g.x, []).append(g.y)

    for i in range(n):
        bi = boxes[i]
        if bi in goal_set:
            continue
        for j in range(i + 1, n):
            bj = boxes[j]
            if bj in goal_set:
                continue
            # same row
            if bi.y == bj.y:
                minx, maxx = sorted((bi.x, bj.x))
                # any goal strictly between them?
                has_between = any(
                    minx < gx < maxx for gx in goals_by_row.get(bi.y, [])
                )
                if not has_between:
                    conflict += 1
            # same column
            if bi.x == bj.x:
                miny, maxy = sorted((bi.y, bj.y))
                has_between = any(
                    miny < gy < maxy for gy in goals_by_col.get(bi.x, [])
                )
                if not has_between:
                    conflict += 1

    # each conflict pair needs at least one extra push; divide by 2 to stay safe
    conflict_penalty = conflict // 2

    return base_cost + conflict_penalty
