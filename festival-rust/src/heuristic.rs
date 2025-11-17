// Heuristic functions for A* search

use crate::board::{Board, Position};

// Hungarian algorithm for minimum cost bipartite matching
pub fn hungarian_lower_bound(board: &Board, boxes: &[Position]) -> u32 {
    let n = boxes.len();
    if n == 0 {
        return 0;
    }

    // Simple greedy matching as approximation (true Hungarian is complex)
    // For each box, find closest unmatched goal
    let mut used_goals = vec![false; board.goals.len()];
    let mut total_cost = 0;

    for box_pos in boxes {
        let mut min_dist = u32::MAX;
        let mut best_goal = 0;

        for (i, goal) in board.goals.iter().enumerate() {
            if used_goals[i] {
                continue;
            }
            let dist = box_pos.manhattan_distance(goal);
            if dist < min_dist {
                min_dist = dist;
                best_goal = i;
            }
        }

        if min_dist < u32::MAX {
            used_goals[best_goal] = true;
            total_cost += min_dist;
        }
    }

    total_cost
}

// Minimum matching heuristic (greedy approximation)
pub fn min_matching_heuristic(board: &Board, boxes: &[Position]) -> u32 {
    hungarian_lower_bound(board, boxes)
}

// Enhanced heuristic considering box mobility
pub fn enhanced_heuristic(board: &Board, boxes: &[Position]) -> u32 {
    let base = min_matching_heuristic(board, boxes);
    
    // Add penalty for boxes in bad positions
    let mut penalty = 0;
    for box_pos in boxes {
        if board.is_goal(box_pos) {
            continue;
        }

        // Count blocked directions
        let mut blocked = 0;
        for &(dx, dy) in &[(0, -1), (1, 0), (0, 1), (-1, 0)] {
            let next = Position::new(box_pos.x + dx, box_pos.y + dy);
            if board.is_wall(&next) || boxes.iter().any(|b| b == &next) {
                blocked += 1;
            }
        }

        // Boxes with 3+ blocked sides are problematic
        if blocked >= 3 {
            penalty += 10;
        } else if blocked == 2 {
            penalty += 2;
        }
    }

    base + penalty
}
