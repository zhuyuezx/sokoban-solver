"""Auto-generated heuristic."""
# metadata: {"iteration": 1, "total_nodes": 31233, "solved": 20}
from sokoban_solver import Board, Pos

def heuristic(board: Board, boxes: tuple[Pos, ...]) -> int:
    """
    Admissible lower‑bound heuristic based on optimal assignment
    (minimum‑cost bipartite matching) of boxes to goals using Manhattan
    distances.  The DP over subsets computes the exact minimal sum,
    which never overestimates the true number of pushes.
    """
    n = len(boxes)
    goals = board.goals

    # Cost matrix: Manhattan distance from each box to each goal
    cost = [[box.manhattan(goal) for goal in goals] for box in boxes]

    # DP over subsets of goals: dp[mask] = minimal total cost for assigning
    # the first k = popcount(mask) boxes to the selected goals in mask.
    size = 1 << n
    INF = 10**9
    dp = [INF] * size
    dp[0] = 0

    for mask in range(size):
        k = mask.bit_count()  # number of boxes already assigned
        if k >= n:
            continue
        base = dp[mask]
        if base == INF:
            continue
        for j in range(n):
            if not (mask >> j) & 1:               # goal j not yet used
                new_mask = mask | (1 << j)
                new_cost = base + cost[k][j]
                if new_cost < dp[new_mask]:
                    dp[new_mask] = new_cost

    return dp[-1]
