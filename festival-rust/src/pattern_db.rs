// Pattern database (placeholder for future enhancement)

use crate::board::{Board, Position};

pub struct PatternDatabase {
    // Future: store precomputed patterns
}

impl PatternDatabase {
    pub fn new() -> Self {
        Self {}
    }

    pub fn lookup(&self, _board: &Board, _boxes: &[Position]) -> Option<u32> {
        // Future: implement pattern database lookup
        None
    }
}
