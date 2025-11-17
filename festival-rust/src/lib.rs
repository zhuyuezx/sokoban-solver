// Festival-Rust: Advanced Sokoban Solver in Rust/WASM
// Inspired by Festival Solver architecture

use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};

mod board;
mod deadlock;
mod distance;
mod search;
mod heuristic;
mod pattern_db;
mod util;

use board::Board;
use search::SearchEngine;

#[wasm_bindgen]
pub struct FestivalSolver {
    engine: SearchEngine,
}

#[derive(Serialize, Deserialize)]
pub struct SolveResult {
    pub solved: bool,
    pub solution: Option<String>,
    pub moves: usize,
    pub pushes: usize,
    pub nodes_searched: usize,
    pub time_ms: u64,
    pub fail_reason: Option<String>,
}

#[wasm_bindgen]
impl FestivalSolver {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        console_error_panic_hook::set_once();
        Self {
            engine: SearchEngine::new(),
        }
    }

    #[wasm_bindgen]
    pub fn solve(&mut self, level: &str, time_limit_ms: u32, progress_callback: Option<js_sys::Function>) -> JsValue {
        let result = self.solve_internal(level, time_limit_ms as u64, progress_callback);
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    fn solve_internal(&mut self, level: &str, time_limit_ms: u64, progress_callback: Option<js_sys::Function>) -> SolveResult {
        let board = match Board::from_string(level) {
            Ok(b) => b,
            Err(e) => {
                return SolveResult {
                    solved: false,
                    solution: None,
                    moves: 0,
                    pushes: 0,
                    nodes_searched: 0,
                    time_ms: 0,
                    fail_reason: Some(e),
                }
            }
        };

        self.engine.solve(board, time_limit_ms, progress_callback)
    }
}
