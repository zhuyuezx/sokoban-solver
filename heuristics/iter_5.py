"""Auto-generated heuristic."""
# metadata: {"iteration": 5, "total_nodes": 297962, "solved": 49}
from sokoban_solver import Board, Pos

def heuristic(board, boxes):
    """
    Admissible heuristic: optimal one‑to‑one assignment (minimum total
    Manhattan distance) plus a large penalty for obvious static deadlocks
    (box in a corner that is not a goal).  Returns a non‑negative int.
    """
    # ----- static deadlock detection (corner not a goal) -----
    goal_set = frozenset(board.goals)
    # cache wall look‑ups for speed
    walls = board.walls
    for bx in boxes:
        if bx in goal_set:
            continue
        # check four corner patterns
        up = Pos(bx.x, bx.y - 1) in walls
        down = Pos(bx.x, bx.y + 1) in walls
        left = Pos(bx.x - 1, bx.y) in walls
        right = Pos(bx.x + 1, bx.y) in walls
        if (up and left) or (up and right) or (down and left) or (down and right):
            # unsolvable state – return a very large but finite value
            return 10_000

    # ----- optimal assignment (minimum total Manhattan distance) -----
    n = len(boxes)
    m = len(board.goals)
    # distance matrix box i -> goal j
    dist = [[boxes[i].manhattan(board.goals[j]) for j in range(m)] for i in range(n)]

    # DP over subsets of goals (bitmask). n == m for classic Sokoban levels.
    INF = 10 ** 9
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dp(i, mask):
        """minimum cost to assign boxes[i:] given already used goals in mask."""
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
