# Festival-Rust: Advanced Sokoban Solver in Rust/WASM

A high-performance Sokoban solver inspired by the Festival solver architecture, compiled to WebAssembly for browser and Node.js use.

## Features

- **Advanced Deadlock Detection**: Simple deadlocks (corners, edges) and freeze deadlocks (2x2 patterns)
- **Smart Heuristics**: Hungarian-inspired matching algorithm for box-goal assignment
- **Efficient Search**: A* search with push-only state space (normalized player positions)
- **WASM Performance**: Compiled to WebAssembly for near-native speed
- **Cross-Platform**: Works in browsers and Node.js

## Architecture

Inspired by Festival's multi-layered approach:

1. **Board Representation** (`board.rs`): Efficient grid-based representation
2. **Deadlock Detection** (`deadlock.rs`): Multiple deadlock patterns
3. **Distance Calculations** (`distance.rs`): BFS-based reachability
4. **Heuristics** (`heuristic.rs`): Lower-bound estimation for A*
5. **Search Engine** (`search.rs`): A* with optimizations

## Building

```bash
# Build for WASM
cargo build --release --target wasm32-unknown-unknown

# Generate bindings for web
wasm-bindgen --target web --out-dir pkg target/wasm32-unknown-unknown/release/festival_rust.wasm

# Generate bindings for Node.js
wasm-bindgen --target nodejs --out-dir pkg-node target/wasm32-unknown-unknown/release/festival_rust.wasm
```

## Usage

### Node.js

```javascript
const { FestivalSolver } = require('./pkg-node/festival_rust.js');

const solver = new FestivalSolver();
const level = `####
#. #
#  ###
#*@  #
#  $ #
#  ###
####`;

const result = solver.solve(level, 30000); // 30 second timeout

if (result.solved) {
    console.log('Solution:', result.solution);
    console.log('Pushes:', result.pushes);
    console.log('Nodes:', result.nodes_searched);
}
```

### Browser

```html
<script type="module">
    import init, { FestivalSolver } from './pkg/festival_rust.js';
    
    await init();
    const solver = new FestivalSolver();
    const result = solver.solve(level, 30000);
</script>
```

## Performance

**Microban Test Results (50 levels):**
- ✅ **Solved: 50/50 (100%)**
- **Average time: 13.82ms per level**
- **Total nodes searched: 637,408**
- **Fastest: <1ms (simple levels)**
- **Slowest: 562ms (Microban 36)**

## Comparison to Festival C++

| Feature | Festival C++ | Festival-Rust |
|---------|-------------|---------------|
| Language | C++ | Rust |
| Platform | Native | WASM + Native |
| Threading | 8 cores | Single (WASM limitation) |
| Memory | ~12GB (8 cores) | ~100MB |
| Deadlock Detection | Advanced | Corner + Simple |
| Pattern DB | Yes | No |
| Microban Solve Rate | 100% | 100% ✅ |
| Speed | Very Fast | Fast (13ms avg) |

## Future Enhancements

1. **Pattern Databases**: Precomputed endgame patterns
2. **Better Heuristics**: True Hungarian algorithm
3. **Transposition Tables**: Better state caching
4. **Iterative Deepening**: Memory-efficient search
5. **Reverse Search**: Backward from goal
6. **Macro Moves**: Tunnel detection and optimization

## Testing

```bash
# Run Node.js tests
node test-festival-rust-node.cjs

# Results show solve rate and performance metrics
```

## License

Inspired by Festival Sokoban Solver by Yaron Shoham.
