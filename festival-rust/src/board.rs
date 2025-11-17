// Board representation and operations

use std::fmt;

pub const MAX_SIZE: usize = 64;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Position {
    pub x: i8,
    pub y: i8,
}

impl Position {
    pub fn new(x: i8, y: i8) -> Self {
        Self { x, y }
    }

    pub fn manhattan_distance(&self, other: &Position) -> u32 {
        ((self.x - other.x).abs() + (self.y - other.y).abs()) as u32
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Cell {
    Wall,
    Floor,
    Goal,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Board {
    pub width: usize,
    pub height: usize,
    pub cells: Vec<Vec<Cell>>,
    pub player: Position,
    pub boxes: Vec<Position>,
    pub goals: Vec<Position>,
}

impl Board {
    pub fn from_string(s: &str) -> Result<Self, String> {
        let lines: Vec<&str> = s.lines()
            .map(|l| l.trim_end())
            .filter(|l| !l.is_empty())
            .collect();

        if lines.is_empty() {
            return Err("Empty level".to_string());
        }

        let height = lines.len();
        let width = lines.iter().map(|l| l.len()).max().unwrap_or(0);

        if width > MAX_SIZE || height > MAX_SIZE {
            return Err(format!("Level too large: {}x{}", width, height));
        }

        let mut cells = vec![vec![Cell::Floor; width]; height];
        let mut player = None;
        let mut boxes = Vec::new();
        let mut goals = Vec::new();

        for (y, line) in lines.iter().enumerate() {
            for (x, ch) in line.chars().enumerate() {
                let pos = Position::new(x as i8, y as i8);
                
                match ch {
                    '#' => cells[y][x] = Cell::Wall,
                    ' ' | '-' | '_' => cells[y][x] = Cell::Floor,
                    '.' => {
                        cells[y][x] = Cell::Goal;
                        goals.push(pos);
                    }
                    '@' => {
                        player = Some(pos);
                    }
                    '+' => {
                        cells[y][x] = Cell::Goal;
                        goals.push(pos);
                        player = Some(pos);
                    }
                    '$' => {
                        boxes.push(pos);
                    }
                    '*' => {
                        cells[y][x] = Cell::Goal;
                        goals.push(pos);
                        boxes.push(pos);
                    }
                    _ => {}
                }
            }
        }

        let player = player.ok_or("No player found")?;

        if boxes.is_empty() {
            return Err("No boxes found".to_string());
        }

        if goals.is_empty() {
            return Err("No goals found".to_string());
        }

        if boxes.len() != goals.len() {
            return Err(format!("Box/goal mismatch: {} boxes, {} goals", boxes.len(), goals.len()));
        }

        Ok(Self {
            width,
            height,
            cells,
            player,
            boxes,
            goals,
        })
    }

    pub fn is_valid_pos(&self, pos: &Position) -> bool {
        pos.x >= 0 && pos.y >= 0 
            && (pos.x as usize) < self.width 
            && (pos.y as usize) < self.height
    }

    pub fn get_cell(&self, pos: &Position) -> Cell {
        if !self.is_valid_pos(pos) {
            return Cell::Wall;
        }
        self.cells[pos.y as usize][pos.x as usize]
    }

    pub fn is_wall(&self, pos: &Position) -> bool {
        self.get_cell(pos) == Cell::Wall
    }

    pub fn has_box(&self, pos: &Position) -> bool {
        self.boxes.iter().any(|b| b == pos)
    }

    pub fn is_goal(&self, pos: &Position) -> bool {
        self.goals.iter().any(|g| g == pos)
    }

    pub fn is_solved(&self) -> bool {
        self.boxes.iter().all(|b| self.is_goal(b))
    }

    pub fn box_index(&self, pos: &Position) -> Option<usize> {
        self.boxes.iter().position(|b| b == pos)
    }
}

impl fmt::Display for Board {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for y in 0..self.height {
            for x in 0..self.width {
                let pos = Position::new(x as i8, y as i8);
                let ch = if pos == self.player {
                    if self.is_goal(&pos) { '+' } else { '@' }
                } else if self.has_box(&pos) {
                    if self.is_goal(&pos) { '*' } else { '$' }
                } else {
                    match self.get_cell(&pos) {
                        Cell::Wall => '#',
                        Cell::Goal => '.',
                        Cell::Floor => ' ',
                    }
                };
                write!(f, "{}", ch)?;
            }
            writeln!(f)?;
        }
        Ok(())
    }
}
