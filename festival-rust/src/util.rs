// Utility functions

use crate::board::Position;

pub const DIRECTIONS: [(i8, i8); 4] = [
    (0, -1),  // Up
    (1, 0),   // Right
    (0, 1),   // Down
    (-1, 0),  // Left
];

pub const DIR_CHARS: [char; 4] = ['u', 'r', 'd', 'l'];
pub const DIR_CHARS_PUSH: [char; 4] = ['U', 'R', 'D', 'L'];

pub fn add_pos(pos: &Position, dir: (i8, i8)) -> Position {
    Position::new(pos.x + dir.0, pos.y + dir.1)
}

pub fn dir_to_char(dir_idx: usize, is_push: bool) -> char {
    if is_push {
        DIR_CHARS_PUSH[dir_idx]
    } else {
        DIR_CHARS[dir_idx]
    }
}
