# Solver Comparison

## Overall Summary

| Solver | Solved | Timed Out | Failed | Success Rate |
|--------|--------|-----------|--------|-------------|
| Baseline | 118 | 35 | 2 | 76.1% |
| Improved | 105 | 24 | 26 | 67.7% |
| Rust | 129 | 26 | 0 | 83.2% |

## Performance Comparison (Solved Levels Only)

### Speed

| Solver | Avg Time (ms) | Min Time (ms) | Max Time (ms) |
|--------|---------------|---------------|---------------|
| Baseline | 1112 | 0 | 8653 |
| Improved | 1185 | 0 | 11610 |
| Rust | 438 | 13 | 9566 |

### Solution Quality (Moves)

| Solver | Avg Moves | Min Moves | Max Moves |
|--------|-----------|-----------|----------|
| Baseline | 95.2 | 1 | 443 |
| Improved | 84.2 | 1 | 429 |
| Rust | 211.3 | 1 | 2164 |

## Level-by-Level Comparison

| Level | Baseline Time | Improved Time | Rust Time | Speed Winner | Baseline Moves | Improved Moves | Rust Moves | Moves Winner |
|-------|---------------|---------------|-----------|--------------|----------------|----------------|------------|-------------|
| Microban 1 | 5ms | 13ms | 449ms | Baseline | 39 | 33 | 33 | Improved |
| Microban 2 | 104ms | 153ms | 15ms | Rust | 22 | 22 | 16 | Rust |
| Microban 3 | 6ms | 10ms | 13ms | Baseline | 41 | 59 | 43 | Baseline |
| Microban 4 | 108ms | 175ms | 107ms | Rust | 41 | 39 | 81 | Improved |
| Microban 5 | 2344ms | ⏱ | 6191ms | Baseline | 27 | - | 29 | Baseline |
| Microban 6 | 366ms | 436ms | 114ms | Rust | 109 | 139 | 209 | Baseline |
| Microban 7 | 3848ms | 10000ms | 152ms | Rust | 26 | 13 | 40 | Improved |
| Microban 8 | 19ms | 15ms | 31ms | Improved | 97 | 121 | 101 | Baseline |
| Microban 9 | 0ms | 1ms | 21ms | Baseline | 30 | 30 | 30 | Baseline |
| Microban 10 | 39ms | 26ms | 50ms | Improved | 93 | 91 | 121 | Improved |
| Microban 11 | 27ms | 25ms | 31ms | Improved | 80 | 90 | 78 | Rust |
| Microban 12 | 8ms | 10ms | 25ms | Baseline | 49 | 56 | 49 | Baseline |
| Microban 13 | 37ms | 44ms | 31ms | Rust | 52 | 52 | 79 | Baseline |
| Microban 14 | 3ms | 4ms | 21ms | Baseline | 51 | 55 | 51 | Baseline |
| Microban 15 | 5ms | 5ms | 24ms | Baseline | 37 | 45 | 43 | Baseline |
| Microban 16 | 685ms | 713ms | 121ms | Rust | 100 | 128 | 214 | Baseline |
| Microban 17 | 9ms | 17ms | 31ms | Baseline | 31 | 31 | 30 | Rust |
| Microban 18 | 22ms | 21ms | 25ms | Improved | 71 | 71 | 75 | Baseline |
| Microban 19 | 6ms | 7ms | 22ms | Baseline | 59 | 55 | 58 | Improved |
| Microban 20 | 19ms | 19ms | 24ms | Baseline | 50 | 56 | 60 | Baseline |
| Microban 21 | 3ms | 2ms | 19ms | Improved | 17 | 17 | 17 | Baseline |
| Microban 22 | 31ms | 24ms | 13ms | Rust | 49 | 47 | 63 | Improved |
| Microban 23 | 2ms | 3ms | 21ms | Baseline | 56 | 58 | 72 | Baseline |
| Microban 24 | 6ms | 7ms | 20ms | Baseline | 35 | 35 | 47 | Baseline |
| Microban 25 | 6ms | 12ms | 24ms | Baseline | 35 | 35 | 41 | Baseline |
| Microban 26 | 17ms | 23ms | 23ms | Baseline | 41 | 42 | 45 | Baseline |
| Microban 27 | 4ms | 5ms | 24ms | Baseline | 50 | 53 | 50 | Baseline |
| Microban 28 | 5ms | 6ms | 27ms | Baseline | 33 | 33 | 33 | Baseline |
| Microban 29 | 28ms | 31ms | 64ms | Baseline | 104 | 126 | 210 | Baseline |
| Microban 30 | 5ms | 10ms | 29ms | Baseline | 21 | 21 | 21 | Baseline |
| Microban 31 | 2ms | 6ms | 22ms | Baseline | 27 | 27 | 17 | Rust |
| Microban 32 | 6ms | 8ms | 20ms | Baseline | 37 | 37 | 35 | Rust |
| Microban 33 | 75ms | 124ms | 28ms | Rust | 41 | 41 | 53 | Baseline |
| Microban 34 | 443ms | 828ms | 140ms | Rust | 36 | 36 | 62 | Baseline |
| Microban 35 | 1495ms | 1055ms | 54ms | Rust | 79 | 139 | 95 | Baseline |
| Microban 36 | ⏱ | ⏱ | 1194ms | Rust | - | - | 460 | Rust |
| Microban 37 | 82ms | 78ms | 32ms | Rust | 77 | 79 | 87 | Baseline |
| Microban 38 | 6ms | 110ms | 25ms | Baseline | 37 | 43 | 61 | Baseline |
| Microban 39 | 22ms | 26ms | 32ms | Baseline | 85 | 85 | 93 | Baseline |
| Microban 40 | ✗ | ✗ | 21ms | Rust | - | - | 21 | Rust |
| Microban 41 | 51ms | 71ms | 23ms | Rust | 50 | 50 | 67 | Baseline |
| Microban 42 | 38ms | 45ms | 29ms | Rust | 65 | 47 | 49 | Improved |
| Microban 43 | 88ms | 127ms | 38ms | Rust | 61 | 65 | 98 | Baseline |
| Microban 44 | 0ms | 0ms | 20ms | Baseline | 1 | 1 | 1 | Baseline |
| Microban 45 | 13ms | 26ms | 21ms | Baseline | 45 | 49 | 57 | Baseline |
| Microban 46 | 2ms | 3ms | 20ms | Baseline | 47 | 47 | 47 | Baseline |
| Microban 47 | 40ms | 12ms | 41ms | Improved | 85 | 127 | 125 | Baseline |
| Microban 48 | 213ms | 246ms | 63ms | Rust | 64 | 73 | 137 | Baseline |
| Microban 49 | 336ms | 413ms | 80ms | Rust | 82 | 82 | 230 | Baseline |
| Microban 50 | 12ms | 13ms | 51ms | Baseline | 76 | 80 | 80 | Baseline |
| Microban 51 | 5ms | 5ms | 30ms | Baseline | 34 | 34 | 54 | Baseline |
| Microban 52 | 37ms | 166ms | 28ms | Rust | 32 | 35 | 34 | Baseline |
| Microban 53 | 12ms | 36ms | 22ms | Baseline | 37 | 45 | 55 | Baseline |
| Microban 54 | 4235ms | ⏱ | 307ms | Rust | 82 | - | 176 | Baseline |
| Microban 55 | 12ms | 13ms | 33ms | Baseline | 68 | 72 | 90 | Baseline |
| Microban 56 | 1ms | 1ms | 22ms | Baseline | 23 | 23 | 23 | Baseline |
| Microban 57 | 15ms | 15ms | 27ms | Baseline | 62 | 66 | 76 | Baseline |
| Microban 58 | 11ms | 17ms | 34ms | Baseline | 44 | 45 | 45 | Baseline |
| Microban 59 | 1826ms | 2591ms | 442ms | Rust | 196 | 226 | 369 | Baseline |
| Microban 60 | 1357ms | 1404ms | 100ms | Rust | 221 | 197 | 379 | Improved |
| Microban 61 | 93ms | 70ms | 32ms | Rust | 100 | 132 | 126 | Baseline |
| Microban 62 | 138ms | 868ms | 371ms | Baseline | 64 | 76 | 156 | Baseline |
| Microban 63 | 32ms | 26ms | 39ms | Improved | 101 | 105 | 115 | Baseline |
| Microban 64 | 241ms | 373ms | 112ms | Rust | 95 | 103 | 107 | Baseline |
| Microban 65 | 3804ms | 5597ms | 255ms | Rust | 140 | 50 | 264 | Improved |
| Microban 66 | 471ms | 1093ms | 424ms | Rust | 71 | 71 | 269 | Baseline |
| Microban 67 | 4ms | 8ms | 27ms | Baseline | 37 | 37 | 53 | Baseline |
| Microban 68 | 76ms | 99ms | 44ms | Rust | 98 | 108 | 192 | Baseline |
| Microban 69 | 2047ms | ✗ | 639ms | Rust | 127 | - | 245 | Baseline |
| Microban 70 | 1140ms | 2811ms | 63ms | Rust | 78 | 93 | 104 | Baseline |
| Microban 71 | 163ms | 167ms | 95ms | Rust | 140 | 130 | 274 | Improved |
| Microban 72 | 753ms | 943ms | 113ms | Rust | 105 | 107 | 151 | Baseline |
| Microban 73 | 263ms | 711ms | 106ms | Rust | 102 | 106 | 256 | Baseline |
| Microban 74 | 1082ms | 792ms | 254ms | Rust | 125 | 163 | 233 | Baseline |
| Microban 75 | 935ms | 951ms | 72ms | Rust | 92 | 94 | 234 | Baseline |
| Microban 76 | 964ms | ✗ | 157ms | Rust | 211 | - | 413 | Baseline |
| Microban 77 | 1586ms | ✗ | 221ms | Rust | 189 | - | 401 | Baseline |
| Microban 78 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 79 | 42ms | 179ms | 36ms | Rust | 48 | 56 | 52 | Baseline |
| Microban 80 | 2516ms | 1521ms | 383ms | Rust | 131 | 141 | 581 | Baseline |
| Microban 81 | 62ms | 72ms | 33ms | Rust | 48 | 50 | 78 | Baseline |
| Microban 82 | 12ms | 18ms | 23ms | Baseline | 52 | 52 | 70 | Baseline |
| Microban 83 | 6988ms | ⏱ | 1639ms | Rust | 170 | - | 313 | Baseline |
| Microban 84 | 2673ms | ✗ | 630ms | Rust | 247 | - | 589 | Baseline |
| Microban 85 | 4466ms | 2584ms | 331ms | Rust | 175 | 167 | 593 | Improved |
| Microban 86 | 771ms | 811ms | 67ms | Rust | 105 | 127 | 131 | Baseline |
| Microban 87 | 7641ms | 2536ms | ⏱ | Improved | 151 | 161 | - | Baseline |
| Microban 88 | 1969ms | ✗ | 549ms | Rust | 197 | - | 519 | Baseline |
| Microban 89 | 2355ms | 2510ms | 653ms | Rust | 156 | 278 | 440 | Baseline |
| Microban 90 | 2732ms | 10825ms | 96ms | Rust | 64 | 8 | 141 | Improved |
| Microban 91 | 80ms | 124ms | 41ms | Rust | 45 | 47 | 70 | Baseline |
| Microban 92 | 890ms | 660ms | 156ms | Rust | 126 | 156 | 221 | Baseline |
| Microban 93 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 94 | 242ms | 288ms | 40ms | Rust | 83 | 91 | 97 | Baseline |
| Microban 95 | 2486ms | 10000ms | ⏱ | Baseline | 25 | 20 | - | Improved |
| Microban 96 | 564ms | 755ms | 192ms | Rust | 94 | 94 | 392 | Baseline |
| Microban 97 | 8617ms | 10000ms | ⏱ | Baseline | 274 | 19 | - | Improved |
| Microban 98 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 99 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 100 | 1151ms | 1241ms | 207ms | Rust | 173 | 189 | 459 | Baseline |
| Microban 101 | ✗ | ✗ | 93ms | Rust | - | - | 313 | Rust |
| Microban 102 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 103 | 33ms | 54ms | 40ms | Baseline | 35 | 35 | 37 | Baseline |
| Microban 104 | 232ms | ✗ | 145ms | Rust | 81 | - | 201 | Baseline |
| Microban 105 | ⏱ | ✗ | 36ms | Rust | - | - | 83 | Rust |
| Microban 106 | ⏱ | ⏱ | 1123ms | Rust | - | - | 479 | Rust |
| Microban 107 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 108 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 109 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 110 | 181ms | 376ms | 33ms | Rust | 55 | 61 | 63 | Baseline |
| Microban 111 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 112 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 113 | ⏱ | ✗ | 963ms | Rust | - | - | 280 | Rust |
| Microban 114 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 115 | ⏱ | ⏱ | 365ms | Rust | - | - | 285 | Rust |
| Microban 116 | 756ms | 1371ms | 53ms | Rust | 63 | 63 | 74 | Baseline |
| Microban 117 | ⏱ | ⏱ | 9566ms | Rust | - | - | 824 | Rust |
| Microban 118 | 6863ms | ✗ | 2124ms | Rust | 234 | - | 2164 | Baseline |
| Microban 119 | 316ms | 460ms | 193ms | Rust | 133 | 157 | 209 | Baseline |
| Microban 120 | 1555ms | 1427ms | 119ms | Rust | 207 | 205 | 369 | Improved |
| Microban 121 | ⏱ | ⏱ | 1153ms | Rust | - | - | 349 | Rust |
| Microban 122 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 123 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 124 | 3422ms | 11610ms | 838ms | Rust | 247 | 8 | 437 | Improved |
| Microban 125 | 3647ms | ⏱ | 3773ms | Baseline | 127 | - | 194 | Baseline |
| Microban 126 | ⏱ | 3994ms | 102ms | Rust | - | 51 | 125 | Improved |
| Microban 127 | 950ms | 2400ms | 253ms | Rust | 106 | 150 | 196 | Baseline |
| Microban 128 | 467ms | 1121ms | 52ms | Rust | 88 | 98 | 98 | Baseline |
| Microban 129 | 3730ms | ✗ | 167ms | Rust | 99 | - | 200 | Baseline |
| Microban 130 | 8653ms | 8205ms | 955ms | Rust | 104 | 18 | 168 | Improved |
| Microban 131 | 2882ms | 1643ms | 159ms | Rust | 78 | 156 | 166 | Baseline |
| Microban 132 | 593ms | 725ms | 193ms | Rust | 227 | 195 | 287 | Improved |
| Microban 133 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 134 | ⏱ | ✗ | 1189ms | Rust | - | - | 900 | Rust |
| Microban 135 | 3632ms | 4974ms | 623ms | Rust | 141 | 16 | 207 | Improved |
| Microban 136 | 633ms | 1111ms | 517ms | Rust | 174 | 166 | 346 | Improved |
| Microban 137 | ⏱ | ⏱ | 1705ms | Rust | - | - | 519 | Rust |
| Microban 138 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 139 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 140 | ⏱ | ✗ | 8070ms | Rust | - | - | 758 | Rust |
| Microban 141 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 142 | 866ms | 1337ms | 1076ms | Baseline | 80 | 84 | 582 | Baseline |
| Microban 143 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 144 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 145 | ⏱ | ⏱ | 66ms | Rust | - | - | 83 | Rust |
| Microban 146 | ⏱ | ⏱ | ⏱ | - | - | - | - | - |
| Microban 147 | 1754ms | ✗ | 698ms | Rust | 178 | - | 403 | Baseline |
| Microban 148 | ⏱ | ⏱ | 396ms | Rust | - | - | 472 | Rust |
| Microban 149 | 440ms | 663ms | 39ms | Rust | 94 | 108 | 94 | Baseline |
| Microban 150 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 151 | 7582ms | ⏱ | ⏱ | Baseline | 127 | - | - | Baseline |
| Microban 152 | 3196ms | 4666ms | 603ms | Rust | 247 | 13 | 1020 | Improved |
| Microban 153 | ⏱ | ✗ | ⏱ | - | - | - | - | - |
| Microban 154 | 31ms | 7ms | 29ms | Improved | 443 | 429 | 429 | Improved |
| Microban 155 | 579ms | 417ms | 98ms | Rust | 282 | 288 | 288 | Baseline |
