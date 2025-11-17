// Distance calculations and reachability

use crate::board::{Board, Position};
use crate::util::{DIRECTIONS, add_pos};
use std::collections::VecDeque;

pub struct DistanceMap {
    distances: Vec<Vec<Option<u32>>>,
    width: usize,
    height: usize,
}

impl DistanceMap {
    pub fn new(width: usize, height: usize) -> Self {
        Self {
            distances: vec![vec![None; width]; height],
            width,
            height,
        }
    }

    pub fn get(&self, pos: &Position) -> Option<u32> {
        if pos.x < 0 || pos.y < 0 {
            return None;
        }
        let x = pos.x as usize;
        let y = pos.y as usize;
        if x >= self.width || y >= self.height {
            return None;
        }
        self.distances[y][x]
    }

    pub fn set(&mut self, pos: &Position, dist: u32) {
        if pos.x < 0 || pos.y < 0 {
            return;
        }
        let x = pos.x as usize;
        let y = pos.y as usize;
        if x >= self.width || y >= self.height {
            return;
        }
        self.distances[y][x] = Some(dist);
    }
}

// Calculate distances from a position to all reachable cells
pub fn calculate_distances(board: &Board, start: &Position, boxes: &[Position]) -> DistanceMap {
    let mut dist_map = DistanceMap::new(board.width, board.height);
    let mut queue = VecDeque::new();
    
    queue.push_back((*start, 0u32));
    dist_map.set(start, 0);

    while let Some((pos, dist)) = queue.pop_front() {
        for &dir in &DIRECTIONS {
            let next = add_pos(&pos, dir);
            
            if board.is_wall(&next) {
                continue;
            }

            if boxes.iter().any(|b| b == &next) {
                continue;
            }

            if dist_map.get(&next).is_some() {
                continue;
            }

            dist_map.set(&next, dist + 1);
            queue.push_back((next, dist + 1));
        }
    }

    dist_map
}

// Check if player can reach a position
pub fn can_reach(board: &Board, from: &Position, to: &Position, boxes: &[Position]) -> bool {
    if from == to {
        return true;
    }

    let mut visited = vec![vec![false; board.width]; board.height];
    let mut queue = VecDeque::new();
    
    queue.push_back(*from);
    visited[from.y as usize][from.x as usize] = true;

    while let Some(pos) = queue.pop_front() {
        for &dir in &DIRECTIONS {
            let next = add_pos(&pos, dir);
            
            if next == *to {
                return true;
            }

            if board.is_wall(&next) {
                continue;
            }

            if boxes.iter().any(|b| b == &next) {
                continue;
            }

            let nx = next.x as usize;
            let ny = next.y as usize;
            if visited[ny][nx] {
                continue;
            }

            visited[ny][nx] = true;
            queue.push_back(next);
        }
    }

    false
}

// Get the path from one position to another (returns direction indices)
pub fn get_path(board: &Board, from: &Position, to: &Position, boxes: &[Position]) -> Option<Vec<usize>> {
    if from == to {
        return Some(Vec::new());
    }

    let mut visited = vec![vec![false; board.width]; board.height];
    let mut parent = vec![vec![None; board.width]; board.height];
    let mut queue = VecDeque::new();
    
    queue.push_back(*from);
    visited[from.y as usize][from.x as usize] = true;

    while let Some(pos) = queue.pop_front() {
        for (dir_idx, &dir) in DIRECTIONS.iter().enumerate() {
            let next = add_pos(&pos, dir);
            
            if board.is_wall(&next) {
                continue;
            }

            if boxes.iter().any(|b| b == &next) {
                continue;
            }

            let nx = next.x as usize;
            let ny = next.y as usize;
            
            if visited[ny][nx] {
                continue;
            }

            visited[ny][nx] = true;
            parent[ny][nx] = Some((pos, dir_idx));
            
            if next == *to {
                // Reconstruct path
                let mut path = Vec::new();
                let mut current = next;
                
                while let Some((prev_pos, dir)) = parent[current.y as usize][current.x as usize] {
                    path.push(dir);
                    current = prev_pos;
                }
                
                path.reverse();
                return Some(path);
            }
            
            queue.push_back(next);
        }
    }

    None
}
