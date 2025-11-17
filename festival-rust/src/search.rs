// Search engine - Festival-style A* search
// Phase 1.1: Proper move generation following Festival C++ architecture

use crate::board::{Board, Position};
use crate::deadlock::DeadlockDetector;
use crate::distance::{can_reach, get_path};
use crate::heuristic::enhanced_heuristic;
use crate::util::{DIRECTIONS, add_pos, dir_to_char};
use crate::SolveResult;
use rustc_hash::FxHashSet;
use std::collections::BinaryHeap;
use std::cmp::Ordering;
use web_time::Instant;
use wasm_bindgen::prelude::*;

// Move structure following Festival's design
#[derive(Clone, Debug, PartialEq, Eq)]
struct Move {
    box_index: usize,      // Which box in the boxes array
    box_from: Position,
    box_to: Position,
    player_path: Vec<usize>, // Directions player takes to reach push position
    direction: usize,       // 0=up, 1=right, 2=down, 3=left (the push)
}

#[derive(Clone, Eq, PartialEq)]
struct State {
    player: Position,
    boxes: Vec<Position>,
    g_cost: u32,
    h_cost: u32,
    moves: Vec<Move>, // Store actual moves, not just directions
}

impl State {
    fn f_cost(&self) -> u32 {
        self.g_cost + self.h_cost
    }

    fn hash_key(&self) -> u64 {
        // Include both player and boxes for complete state
        let mut hash = 0u64;
        hash = hash.wrapping_mul(31).wrapping_add(self.player.x as u64);
        hash = hash.wrapping_mul(31).wrapping_add(self.player.y as u64);
        
        let mut sorted_boxes = self.boxes.clone();
        sorted_boxes.sort_by_key(|p| (p.y, p.x));
        
        for b in &sorted_boxes {
            hash = hash.wrapping_mul(31).wrapping_add(b.x as u64);
            hash = hash.wrapping_mul(31).wrapping_add(b.y as u64);
        }
        hash
    }
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.f_cost().cmp(&self.f_cost())
            .then_with(|| other.h_cost.cmp(&self.h_cost))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub struct SearchEngine {
    deadlock_detector: Option<DeadlockDetector>,
}

impl SearchEngine {
    pub fn new() -> Self {
        Self {
            deadlock_detector: None,
        }
    }

    // Find all possible moves for current position (Festival approach)
    fn find_possible_moves(&self, board: &Board, player: &Position, boxes: &[Position]) -> Vec<Move> {
        let mut moves = Vec::new();

        // For each box, try to push it in each direction
        for (box_idx, box_pos) in boxes.iter().enumerate() {
            for (dir_idx, &dir) in DIRECTIONS.iter().enumerate() {
                // Where the box would move to
                let new_box_pos = add_pos(box_pos, dir);

                // Check if new box position is valid
                if board.is_wall(&new_box_pos) {
                    continue;
                }

                // Check if another box is there
                if boxes.iter().any(|b| b == &new_box_pos) {
                    continue;
                }

                // Where player must be to push (opposite side of box)
                let player_push_pos = add_pos(box_pos, (-dir.0, -dir.1));

                // Check if player position is valid
                if board.is_wall(&player_push_pos) {
                    continue;
                }

                // Get path from current player position to push position
                let player_path = match get_path(board, player, &player_push_pos, boxes) {
                    Some(path) => path,
                    None => continue, // Can't reach push position
                };

                // Check simple deadlock on new position
                if let Some(ref detector) = self.deadlock_detector {
                    if detector.is_simple_deadlock(&new_box_pos) {
                        continue;
                    }
                }

                // Valid move found - store the complete player path
                moves.push(Move {
                    box_index: box_idx,
                    box_from: *box_pos,
                    box_to: new_box_pos,
                    player_path,
                    direction: dir_idx,
                });
            }
        }

        moves
    }

    // Apply a move to get new state
    fn apply_move(&self, board: &Board, state: &State, mv: &Move) -> Option<State> {
        // Verify the box is still in the expected position
        if state.boxes[mv.box_index] != mv.box_from {
            return None;
        }

        // Create new box configuration
        let mut new_boxes = state.boxes.clone();
        new_boxes[mv.box_index] = mv.box_to;

        // Calculate new costs
        let new_h = enhanced_heuristic(board, &new_boxes);
        
        // Store the full move
        let mut new_moves = state.moves.clone();
        new_moves.push(mv.clone());

        Some(State {
            player: mv.box_from, // Player ends up where box was after push
            boxes: new_boxes,
            g_cost: state.g_cost + 1,
            h_cost: new_h,
            moves: new_moves,
        })
    }
    
    // Reconstruct solution from moves with stored player paths
    fn reconstruct_solution(&self, _board: &Board, moves: &[Move]) -> String {
        let mut solution = String::new();
        
        for mv in moves {
            // Add player movements (lowercase) - these were computed during search
            for &dir_idx in &mv.player_path {
                solution.push(dir_to_char(dir_idx, false));
            }
            
            // Add the push move (uppercase)
            solution.push(dir_to_char(mv.direction, true));
        }
        
        solution
    }
    
    // Old expand function - keeping for reference
    fn expand_solution_old(&self, board: &Board, push_solution: &str) -> String {
        let mut full_solution = String::new();
        let mut current_player = board.player;
        let mut current_boxes = board.boxes.clone();
        
        for push_char in push_solution.chars() {
            let dir_idx = match push_char {
                'U' => 0,
                'R' => 1,
                'D' => 2,
                'L' => 3,
                _ => continue,
            };
            
            let dir = DIRECTIONS[dir_idx];
            
            // Find which box to push
            let mut box_to_push = None;
            for (idx, box_pos) in current_boxes.iter().enumerate() {
                let push_from = add_pos(box_pos, (-dir.0, -dir.1));
                if get_path(board, &current_player, &push_from, &current_boxes).is_some() {
                    // Check if this box can actually be pushed in this direction
                    let new_box_pos = add_pos(box_pos, dir);
                    if !board.is_wall(&new_box_pos) && !current_boxes.iter().any(|b| b == &new_box_pos) {
                        box_to_push = Some((idx, *box_pos, push_from));
                        break;
                    }
                }
            }
            
            if let Some((box_idx, box_pos, push_from)) = box_to_push {
                // Get path to push position
                if let Some(player_path) = get_path(board, &current_player, &push_from, &current_boxes) {
                    // Add player movements
                    for path_dir_idx in player_path {
                        full_solution.push(dir_to_char(path_dir_idx, false));
                        current_player = add_pos(&current_player, DIRECTIONS[path_dir_idx]);
                    }
                }
                
                // Add push move
                full_solution.push(push_char);
                
                // Update state
                let new_box_pos = add_pos(&box_pos, dir);
                current_boxes[box_idx] = new_box_pos;
                current_player = box_pos;
            }
        }
        
        full_solution
    }

    pub fn solve(&mut self, board: Board, time_limit_ms: u64, progress_callback: Option<js_sys::Function>) -> SolveResult {
        let start_time = Instant::now();
        
        // Initialize deadlock detector
        self.deadlock_detector = Some(DeadlockDetector::new(&board));

        let initial_h = enhanced_heuristic(&board, &board.boxes);
        let initial_state = State {
            player: board.player,
            boxes: board.boxes.clone(),
            g_cost: 0,
            h_cost: initial_h,
            moves: Vec::new(),
        };

        let mut open_set = BinaryHeap::new();
        let mut closed_set = FxHashSet::default();
        
        open_set.push(initial_state);
        let mut nodes_searched = 0;

        while let Some(current) = open_set.pop() {
            nodes_searched += 1;

            // Check time limit and report progress
            if nodes_searched % 1000 == 0 {
                let elapsed = start_time.elapsed().as_millis() as u64;
                
                // Call progress callback if provided
                if let Some(ref callback) = progress_callback {
                    let progress = js_sys::Object::new();
                    js_sys::Reflect::set(&progress, &"explored".into(), &nodes_searched.into()).ok();
                    js_sys::Reflect::set(&progress, &"frontier".into(), &open_set.len().into()).ok();
                    js_sys::Reflect::set(&progress, &"iterations".into(), &nodes_searched.into()).ok();
                    js_sys::Reflect::set(&progress, &"timeElapsed".into(), &((elapsed / 1000) as u32).into()).ok();
                    
                    let this = JsValue::null();
                    callback.call1(&this, &progress).ok();
                }
                
                if elapsed > time_limit_ms {
                    return SolveResult {
                        solved: false,
                        solution: None,
                        moves: 0,
                        pushes: 0,
                        nodes_searched,
                        time_ms: elapsed,
                        fail_reason: Some("Time limit exceeded".to_string()),
                    };
                }
            }

            // Check if solved
            if current.boxes.iter().all(|b| board.goals.iter().any(|g| g == b)) {
                let elapsed = start_time.elapsed().as_millis() as u64;
                
                // Reconstruct full solution with player movements (like Festival C++)
                let solution = self.reconstruct_solution(&board, &current.moves);
                let pushes = solution.chars().filter(|c| c.is_uppercase()).count();
                
                return SolveResult {
                    solved: true,
                    solution: Some(solution.clone()),
                    moves: solution.len(),
                    pushes,
                    nodes_searched,
                    time_ms: elapsed,
                    fail_reason: None,
                };
            }

            let state_hash = current.hash_key();
            if closed_set.contains(&state_hash) {
                continue;
            }
            closed_set.insert(state_hash);

            // Phase 1.1: Generate all possible moves using Festival's approach
            let possible_moves = self.find_possible_moves(&board, &current.player, &current.boxes);

            // Try each move
            for mv in possible_moves {
                if let Some(new_state) = self.apply_move(&board, &current, &mv) {
                    open_set.push(new_state);
                }
            }
        }

        let elapsed = start_time.elapsed().as_millis() as u64;
        SolveResult {
            solved: false,
            solution: None,
            moves: 0,
            pushes: 0,
            nodes_searched,
            time_ms: elapsed,
            fail_reason: Some("No solution found".to_string()),
        }
    }
}
