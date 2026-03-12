"""Auto-generated heuristic."""
# metadata: {"iteration": 6, "total_nodes": 286651, "solved": 49}
from sokoban_solver import Board, Pos

def heuristic(board, boxes):
    """Admissible heuristic: optimal sum of wall‑only push distances
    (Manhattan-like) from each box to a distinct goal using DP assignment.
    """
    # ---- pre‑compute distances from every goal to all reachable squares ----
    if not hasattr(board, "_goal_dist"):
        # BFS distances ignoring boxes, only walls block movement.
        goal_dist = {}
        for g in board.goals:
            dist = {g: 0}
            q = [g]
            head = 0
            while head < len(q):
                p = q[head]
                head += 1
                d = dist[p] + 1
                for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    nb = board.Pos(p.x + dx, p.y + dy) if hasattr(board, "Pos") else Pos(p.x + dx, p.y + dy)
                    if nb in board.walls or nb in dist:
                        continue
                    dist[nb] = d
                    q.append(nb)
            goal_dist[g] = dist
        board._goal_dist = goal_dist
    else:
        goal_dist = board._goal_dist

    # ---- build distance matrix box -> goal (wall‑only distances) ----
    INF = 10**6
    n = len(boxes)
    matrix = [[goal_dist[g].get(b, INF) for g in board.goals] for b in boxes]

    # If any box cannot reach any goal (distance INF), state is deadlocked.
    # Return a very large value that is still admissible (won’t prune a solution).
    if any(min(row) >= INF for row in matrix):
        return INF

    # ---- DP for minimum assignment (Hungarian via bitmask) ----
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dp(i, mask):
        if i == n:
            return 0
        best = INF
        row = matrix[i]
        for j in range(n):
            if not (mask & (1 << j)):
                cost = row[j] + dp(i + 1, mask | (1 << j))
                if cost < best:
                    best = cost
        return best

    return dp(0, 0)
