# Festival-Rust Implementation Plan

## Goal
Implement Festival C++ solver architecture in Rust/WASM to solve all 50 Microban levels.

## Current Status
- ✓ Basic board representation
- ✓ Simple corner deadlock detection  
- ✓ Proper move generation (Festival-style)
- ✓ Player reachability checking
- ✓ A* search with heuristic
- **Result: 50/50 Microban solved (100%)** ✅

## Phase 1.1 Complete!
- Implemented proper move generation following Festival's approach
- Fixed state representation to include player position
- Disabled overly aggressive freeze deadlock detection
- **Achievement: All 50 Microban levels solved in average 13.82ms per level**

## Festival C++ Architecture Analysis

### Core Components

1. **Board Representation**
   - Uses byte arrays for compact storage
   - Tracks: walls, boxes, goals, player, inner area
   - Sokoban cloud (reachable positions)
   - Index system for fast position lookup

2. **Move Generation** (`moves.cpp`)
   - `find_possible_moves()` - generates all legal moves
   - `find_box_moves()` - for each box, find where it can be pushed
   - Corral detection (boxes that can't help yet)
   - Fixed boxes (boxes that can't move)
   - Kill moves (forced moves)

3. **Deadlock Detection** (Multiple levels)
   - Simple: corners, edges
   - Freeze: 2x2 patterns
   - Corral: boxes blocking other boxes
   - Cycle: detecting loops
   - Advanced: biconnected components, rooms
   - Pattern-based: precomputed deadlock patterns

4. **Search Engine** (`engine.cpp`)
   - FESS (Forward Expanding Search Strategy)
   - Tree-based search (not simple A*)
   - Request system (prioritizes which positions to expand)
   - Label system (categorizes positions)
   - Perimeter tracking (goal positions)
   - Multiple search modes (NORMAL, REV_SEARCH, GIRL_SEARCH, etc.)

5. **Heuristics** (`heuristics.cpp`)
   - Match distance (Hungarian algorithm)
   - Scored distance
   - Out-of-plan detection
   - Advisors (guide search)

6. **Tree Structure** (`tree.cpp`)
   - Nodes: unique board positions
   - Expansions: nodes with generated moves
   - Move hashes: links between positions
   - Subtree management
   - Best move tracking

## Implementation Phases

### Phase 1: Fix Basic Search ✅ COMPLETE
**Status: ACHIEVED 50/50 (100%)**

Tasks:
- [x] 1.1: Implement proper move generation
  - Generate moves for each box in each direction
  - Check player reachability for each push
  - Include move direction and type
- [x] 1.2: Fix state representation
  - Include player position in state
  - Proper state hashing with player + boxes
- [x] 1.3: Disable aggressive freeze deadlock
  - Freeze deadlock was filtering valid moves
  - Disabled for now (can be improved later)
- [x] 1.4: Test and verify
  - **Result: 50/50 Microban solved!**
  - Average: 13.82ms per level
  - Total nodes: 637,408

### Phase 2: Advanced Deadlock Detection (Target: 40/50)
**Priority: HIGH**

Tasks:
- [ ] 2.1: Implement corral detection
  - Detect boxes that block access to goals
  - Skip moves that don't help corral
- [ ] 2.2: Implement fixed box detection
  - Boxes that can never move
  - Turn them into walls for search
- [ ] 2.3: Implement cycle detection
  - Detect when search returns to same state
  - Mark as deadlock
- [ ] 2.4: Test and verify
  - Should solve ~40/50 Microban

### Phase 3: Better Heuristics (Target: 45/50)
**Priority: MEDIUM**

Tasks:
- [ ] 3.1: Implement Hungarian algorithm
  - True minimum cost matching
  - Better than greedy matching
- [ ] 3.2: Implement scored distance
  - Distance considering obstacles
  - Not just Manhattan distance
- [ ] 3.3: Implement out-of-plan detection
  - Boxes not on path to goals
  - Penalty in heuristic
- [ ] 3.4: Test and verify
  - Should solve ~45/50 Microban

### Phase 4: Tree-Based Search (Target: 50/50)
**Priority: MEDIUM**

Tasks:
- [ ] 4.1: Implement tree structure
  - Nodes, expansions, move hashes
  - Proper memory management
- [ ] 4.2: Implement request system
  - Prioritize positions to expand
  - Label system
- [ ] 4.3: Implement perimeter tracking
  - Track positions near goal
  - Focus search on promising areas
- [ ] 4.4: Test and verify
  - Should solve 50/50 Microban

### Phase 5: Optimization (Target: Fast solving)
**Priority: LOW**

Tasks:
- [ ] 5.1: Pattern database
  - Precompute endgame patterns
- [ ] 5.2: Transposition tables
  - Better state caching
- [ ] 5.3: Macro moves
  - Tunnel detection
  - Multi-push sequences

## Testing Strategy

After each phase:
1. Run full Microban test suite (50 levels)
2. Document solve rate and performance
3. Identify which levels still fail
4. Analyze failure patterns
5. Proceed to next phase

## Current Focus: Phase 1.1

Implement proper move generation following Festival's approach:
- For each box on the board
- For each direction (up, down, left, right)
- Check if box can be pushed in that direction
- Check if player can reach the push position
- Generate the move with proper attributes

