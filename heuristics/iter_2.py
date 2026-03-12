"""Auto-generated heuristic."""
# metadata: {"iteration": 2, "total_nodes": 22000, "solved": 20}
from sokoban_solver import Board, Pos

def heuristic(board, boxes):
    """
    Admissible heuristic: optimal assignment of boxes to goals using
    push‑distance that respects walls (ignores other boxes).  Pre‑computes,
    per board, the shortest push‑distance from every cell to each goal
    (walls only) and then solves the exact minimum‑cost matching via DP.
    """
    # ----- cache of per‑board distance maps (wall‑only) -----------------
    # key is immutable representation of walls and goals
    _cache = heuristic._cache if hasattr(heuristic, "_cache") else {}
    if not _cache:
        heuristic._cache = _cache  # store for future calls

    key = (board.walls, board.goals)
    if key not in _cache:
        # compute a distance map for each goal (walls only)
        goal_maps = []
        for g in board.goals:
            dist = {}
            dq = [g]
            dist[g] = 0
            head = 0
            while head < len(dq):
                p = dq[head]
                head += 1
                d = dist[p]
                for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    np = Pos(p.x + dx, p.y + dy)
                    if np in board.walls or np in dist:
                        continue
                    dist[np] = d + 1
                    dq.append(np)
            goal_maps.append(dist)
        _cache[key] = goal_maps
    else:
        goal_maps = _cache[key]

    n = len(boxes)
    INF = 10 ** 9

    # build cost matrix: cost[i][j] = distance from box i to goal j
    cost = [[goal_maps[j].get(boxes[i], INF) for j in range(n)] for i in range(n)]

    # DP over subsets of goals (exact min‑cost bipartite matching)
    size = 1 << n
    dp = [INF] * size
    dp[0] = 0
    for mask in range(size):
        k = mask.bit_count()            # number of boxes already assigned
        if k >= n:
            continue
        base = dp[mask]
        if base == INF:
            continue
        for j in range(n):
            if (mask >> j) & 1:
                continue                # goal j already used
            nd = base + cost[k][j]
            new_mask = mask | (1 << j)
            if nd < dp[new_mask]:
                dp[new_mask] = nd

    return dp[-1]
