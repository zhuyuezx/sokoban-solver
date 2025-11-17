// Deadlock detection - critical for pruning

use crate::board::{Board, Position};
use crate::util::{DIRECTIONS, add_pos};

// Simple deadlock patterns
pub struct DeadlockDetector {
    simple_deadlocks: Vec<Vec<bool>>,
}

impl DeadlockDetector {
    pub fn new(board: &Board) -> Self {
        let mut detector = Self {
            simple_deadlocks: vec![vec![false; board.width]; board.height],
        };
        detector.compute_simple_deadlocks(board);
        detector
    }

    // Compute simple deadlocks (corners only for now - edge detection is complex)
    fn compute_simple_deadlocks(&mut self, board: &Board) {
        for y in 0..board.height {
            for x in 0..board.width {
                let pos = Position::new(x as i8, y as i8);
                
                if board.is_wall(&pos) || board.is_goal(&pos) {
                    continue;
                }

                // Check if this is a corner deadlock
                if self.is_corner_deadlock(board, &pos) {
                    self.simple_deadlocks[y][x] = true;
                }

                // Edge deadlock detection disabled - too complex and error-prone
                // TODO: Implement proper edge deadlock detection
            }
        }
    }

    fn is_corner_deadlock(&self, board: &Board, pos: &Position) -> bool {
        if board.is_goal(pos) {
            return false;
        }

        let up = add_pos(pos, DIRECTIONS[0]);
        let right = add_pos(pos, DIRECTIONS[1]);
        let down = add_pos(pos, DIRECTIONS[2]);
        let left = add_pos(pos, DIRECTIONS[3]);

        let up_blocked = board.is_wall(&up);
        let right_blocked = board.is_wall(&right);
        let down_blocked = board.is_wall(&down);
        let left_blocked = board.is_wall(&left);

        // Corner patterns
        (up_blocked && right_blocked) ||
        (right_blocked && down_blocked) ||
        (down_blocked && left_blocked) ||
        (left_blocked && up_blocked)
    }

    fn is_edge_deadlock(&self, board: &Board, pos: &Position) -> bool {
        if board.is_goal(pos) {
            return false;
        }

        // Check horizontal edge
        let up = add_pos(pos, DIRECTIONS[0]);
        let down = add_pos(pos, DIRECTIONS[2]);
        
        if board.is_wall(&up) || board.is_wall(&down) {
            // On horizontal edge, check if any goal is reachable horizontally
            let mut has_goal_on_edge = false;
            
            // Check left
            let mut check_pos = *pos;
            loop {
                check_pos = add_pos(&check_pos, DIRECTIONS[3]);
                if board.is_wall(&check_pos) {
                    break;
                }
                let check_up = add_pos(&check_pos, DIRECTIONS[0]);
                let check_down = add_pos(&check_pos, DIRECTIONS[2]);
                if !board.is_wall(&check_up) && !board.is_wall(&check_down) {
                    break; // Can escape edge
                }
                if board.is_goal(&check_pos) {
                    has_goal_on_edge = true;
                    break;
                }
            }

            if !has_goal_on_edge {
                // Check right
                let mut check_pos = *pos;
                loop {
                    check_pos = add_pos(&check_pos, DIRECTIONS[1]);
                    if board.is_wall(&check_pos) {
                        break;
                    }
                    let check_up = add_pos(&check_pos, DIRECTIONS[0]);
                    let check_down = add_pos(&check_pos, DIRECTIONS[2]);
                    if !board.is_wall(&check_up) && !board.is_wall(&check_down) {
                        break;
                    }
                    if board.is_goal(&check_pos) {
                        has_goal_on_edge = true;
                        break;
                    }
                }
            }

            if !has_goal_on_edge {
                return true;
            }
        }

        // Check vertical edge
        let left = add_pos(pos, DIRECTIONS[3]);
        let right = add_pos(pos, DIRECTIONS[1]);
        
        if board.is_wall(&left) || board.is_wall(&right) {
            let mut has_goal_on_edge = false;
            
            // Check up
            let mut check_pos = *pos;
            loop {
                check_pos = add_pos(&check_pos, DIRECTIONS[0]);
                if board.is_wall(&check_pos) {
                    break;
                }
                let check_left = add_pos(&check_pos, DIRECTIONS[3]);
                let check_right = add_pos(&check_pos, DIRECTIONS[1]);
                if !board.is_wall(&check_left) && !board.is_wall(&check_right) {
                    break;
                }
                if board.is_goal(&check_pos) {
                    has_goal_on_edge = true;
                    break;
                }
            }

            if !has_goal_on_edge {
                // Check down
                let mut check_pos = *pos;
                loop {
                    check_pos = add_pos(&check_pos, DIRECTIONS[2]);
                    if board.is_wall(&check_pos) {
                        break;
                    }
                    let check_left = add_pos(&check_pos, DIRECTIONS[3]);
                    let check_right = add_pos(&check_pos, DIRECTIONS[1]);
                    if !board.is_wall(&check_left) && !board.is_wall(&check_right) {
                        break;
                    }
                    if board.is_goal(&check_pos) {
                        has_goal_on_edge = true;
                        break;
                    }
                }
            }

            if !has_goal_on_edge {
                return true;
            }
        }

        false
    }

    pub fn is_simple_deadlock(&self, pos: &Position) -> bool {
        if pos.x < 0 || pos.y < 0 {
            return false;
        }
        let x = pos.x as usize;
        let y = pos.y as usize;
        if x >= self.simple_deadlocks[0].len() || y >= self.simple_deadlocks.len() {
            return false;
        }
        self.simple_deadlocks[y][x]
    }

    // Check for freeze deadlock (2x2 box configuration)
    pub fn is_freeze_deadlock(&self, board: &Board, boxes: &[Position]) -> bool {
        for box_pos in boxes {
            if board.is_goal(box_pos) {
                continue;
            }

            // Check 2x2 patterns
            for dy in 0..=1 {
                for dx in 0..=1 {
                    let pos1 = *box_pos;
                    let pos2 = Position::new(box_pos.x + 1 - dx, box_pos.y + dy);
                    let pos3 = Position::new(box_pos.x + dx, box_pos.y + 1 - dy);
                    let pos4 = Position::new(box_pos.x + 1 - dx, box_pos.y + 1 - dy);

                    let has_box_2 = boxes.iter().any(|b| b == &pos2) || board.is_wall(&pos2);
                    let has_box_3 = boxes.iter().any(|b| b == &pos3) || board.is_wall(&pos3);
                    let has_box_4 = boxes.iter().any(|b| b == &pos4) || board.is_wall(&pos4);

                    if has_box_2 && has_box_3 && has_box_4 {
                        // Check if any of these positions is not a goal
                        if !board.is_goal(&pos1) || !board.is_goal(&pos2) || 
                           !board.is_goal(&pos3) || !board.is_goal(&pos4) {
                            return true;
                        }
                    }
                }
            }
        }
        false
    }
}
