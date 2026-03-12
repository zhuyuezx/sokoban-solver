'use strict';
// ── Sokoban A* Solver — Web Worker ───────────────────────────────────
// Pure-JS A* for play.html.  Supports: naive_manhattan, greedy_matching, enhanced.

const DIRS = [[0,-1],[1,0],[0,1],[-1,0]]; // up right down left
const LC   = 'urdl';
const UC   = 'URDL';

// ── Board parsing ────────────────────────────────────────────────────

function parseBoard(text) {
  const lines = text.split('\n').map(l => l.trimEnd()).filter(l => l.length > 0);
  if (!lines.length) throw new Error('Empty level');
  const height = lines.length;
  const width  = Math.max(...lines.map(l => l.length), 1);

  const walls   = new Set();
  const goals   = [];
  const goalSet = new Set();
  const boxes   = [];
  let player    = null;

  for (let y = 0; y < lines.length; y++) {
    for (let x = 0; x < lines[y].length; x++) {
      const k = y * width + x;
      switch (lines[y][x]) {
        case '#': walls.add(k);  break;
        case '.': goals.push([x,y]); goalSet.add(k); break;
        case '@': player = [x,y]; break;
        case '+': goals.push([x,y]); goalSet.add(k); player = [x,y]; break;
        case '$': boxes.push([x,y]); break;
        case '*': goals.push([x,y]); goalSet.add(k); boxes.push([x,y]); break;
      }
    }
  }
  if (!player) throw new Error('No player (@) in level');
  if (!boxes.length) throw new Error('No boxes ($) in level');
  if (boxes.length !== goals.length)
    throw new Error('Box/goal mismatch: ' + boxes.length + ' boxes, ' + goals.length + ' goals');
  return { walls, goals, goalSet, boxes, player, width, height };
}

// ── Corner deadlock detection ────────────────────────────────────────

function cornersDeadlock(board) {
  const { walls, goalSet, width, height } = board;
  const dead = new Set();
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const k = y * width + x;
      if (walls.has(k) || goalSet.has(k)) continue;
      const up = walls.has((y-1)*width + x);
      const dn = walls.has((y+1)*width + x);
      const lt = walls.has( y   *width + (x-1));
      const rt = walls.has( y   *width + (x+1));
      if ((up&&lt)||(up&&rt)||(dn&&lt)||(dn&&rt)) dead.add(k);
    }
  }
  return dead;
}

// ── BFS player pathfinding ───────────────────────────────────────────

function bfsPath(board, boxSet, sx, sy, tx, ty) {
  if (sx === tx && sy === ty) return [];
  const { walls, width, height } = board;
  const n   = width * height;
  const prv = new Int32Array(n).fill(-1);
  const dir = new Int8Array(n).fill(-1);
  const start  = sy * width + sx;
  const target = ty * width + tx;
  prv[start] = start;
  const q = [start];
  let head = 0;
  while (head < q.length) {
    const cur = q[head++];
    const cy  = (cur / width) | 0;
    const cx  = cur % width;
    for (let di = 0; di < 4; di++) {
      const nx = cx + DIRS[di][0];
      const ny = cy + DIRS[di][1];
      if (nx < 0 || ny < 0 || nx >= width || ny >= height) continue;
      const nk = ny * width + nx;
      if (prv[nk] >= 0 || walls.has(nk) || boxSet.has(nk)) continue;
      prv[nk] = cur;
      dir[nk] = di;
      if (nk === target) {
        const path = [];
        let c = target;
        while (c !== start) { path.push(dir[c]); c = prv[c]; }
        return path.reverse();
      }
      q.push(nk);
    }
  }
  return null;
}

// ── Heuristics ───────────────────────────────────────────────────────

function manhattan([ax,ay], [bx,by]) {
  return Math.abs(ax-bx) + Math.abs(ay-by);
}

function h_naive(board, boxes) {
  return boxes.reduce((s, b) =>
    s + Math.min(...board.goals.map(g => manhattan(b, g))), 0);
}

function h_greedy(board, boxes) {
  const used = new Uint8Array(board.goals.length);
  let total = 0;
  for (const b of boxes) {
    let best = Infinity, bi = 0;
    for (let i = 0; i < board.goals.length; i++) {
      if (used[i]) continue;
      const d = manhattan(b, board.goals[i]);
      if (d < best) { best = d; bi = i; }
    }
    used[bi] = 1;
    total += best;
  }
  return total;
}

function h_enhanced(board, boxes) {
  const base = h_greedy(board, boxes);
  const { walls, goalSet, width } = board;
  const bSet = new Set(boxes.map(([x,y]) => y*width+x));
  let penalty = 0;
  for (const [bx,by] of boxes) {
    if (goalSet.has(by*width+bx)) continue;
    let blocked = 0;
    for (const [dx,dy] of DIRS) {
      const nk = (by+dy)*width+(bx+dx);
      if (walls.has(nk) || bSet.has(nk)) blocked++;
    }
    if (blocked >= 3) penalty += 10;
    else if (blocked === 2) penalty += 2;
  }
  return base + penalty;
}

const HEURISTICS = {
  naive_manhattan: h_naive,
  greedy_matching: h_greedy,
  enhanced:        h_enhanced,
};

// ── State key ────────────────────────────────────────────────────────

function stateKey(px, py, boxes) {
  const sb = [...boxes].sort((a,b) => a[1]-b[1] || a[0]-b[0]);
  return px+','+py+'|'+sb.map(([x,y]) => x+','+y).join(';');
}

// ── Min-heap ─────────────────────────────────────────────────────────

class MinHeap {
  constructor() { this.d = []; }
  get size() { return this.d.length; }
  push(x) { this.d.push(x); this._up(this.d.length - 1); }
  pop() {
    const top = this.d[0];
    const last = this.d.pop();
    if (this.d.length) { this.d[0] = last; this._dn(0); }
    return top;
  }
  _up(i) {
    while (i > 0) {
      const p = (i-1) >> 1;
      if (this.d[p].f <= this.d[i].f) break;
      [this.d[p], this.d[i]] = [this.d[i], this.d[p]];
      i = p;
    }
  }
  _dn(i) {
    const n = this.d.length;
    for (;;) {
      let m = i, l = 2*i+1, r = l+1;
      if (l < n && this.d[l].f < this.d[m].f) m = l;
      if (r < n && this.d[r].f < this.d[m].f) m = r;
      if (m === i) break;
      [this.d[m], this.d[i]] = [this.d[i], this.d[m]];
      i = m;
    }
  }
}

// ── A* solver ────────────────────────────────────────────────────────

function solve(board, hName, limitMs, maxNodes) {
  limitMs  = limitMs  || 30000;
  maxNodes = maxNodes || 500000;

  const hFn  = HEURISTICS[hName] || h_enhanced;
  const dead = cornersDeadlock(board);
  const W    = board.width;
  const closed = new Map();
  const initKey = stateKey(board.player[0], board.player[1], board.boxes);
  const heap = new MinHeap();
  const h0   = hFn(board, board.boxes);
  heap.push({ f: h0, g: 0, px: board.player[0], py: board.player[1],
              boxes: board.boxes, key: initKey, parentKey: null, move: null });

  let nodes = 0;
  const t0  = performance.now();

  while (heap.size > 0) {
    const cur = heap.pop();
    nodes++;
    if (closed.has(cur.key)) continue;
    closed.set(cur.key, { parentKey: cur.parentKey, move: cur.move });

    if (nodes % 1000 === 0) {
      const elapsed = performance.now() - t0;
      self.postMessage({ type: 'progress', heuristic: hName, nodes, elapsed });
      if (elapsed > limitMs) return { solved: false, nodes, time: elapsed, fail: 'timeout' };
      if (nodes > maxNodes)  return { solved: false, nodes, time: elapsed, fail: 'node limit' };
    }

    if (cur.boxes.every(([x,y]) => board.goalSet.has(y*W+x))) {
      const elapsed  = performance.now() - t0;
      const solution = reconstructSolution(cur.key, closed);
      const pushes   = [...solution].filter(c => c >= 'A' && c <= 'Z').length;
      return { solved: true, nodes, time: elapsed, solution, pushes };
    }

    const boxSet = new Set(cur.boxes.map(([x,y]) => y*W+x));

    for (let bi = 0; bi < cur.boxes.length; bi++) {
      const [bx, by] = cur.boxes[bi];
      for (let di = 0; di < 4; di++) {
        const [dx, dy] = DIRS[di];
        const nbx = bx+dx, nby = by+dy;
        if (nbx < 0 || nby < 0 || nbx >= W || nby >= board.height) continue;
        const nbk = nby*W+nbx;
        if (board.walls.has(nbk) || boxSet.has(nbk) || dead.has(nbk)) continue;

        const ppx = bx-dx, ppy = by-dy;
        if (ppx < 0 || ppy < 0 || ppx >= W || ppy >= board.height) continue;
        if (board.walls.has(ppy*W+ppx)) continue;

        const path = bfsPath(board, boxSet, cur.px, cur.py, ppx, ppy);
        if (path === null) continue;

        const newBoxes = cur.boxes.map((b,i) => i===bi ? [nbx,nby] : b);
        const newG   = cur.g + 1;
        const newH   = hFn(board, newBoxes);
        const newKey = stateKey(bx, by, newBoxes);
        if (closed.has(newKey)) continue;

        heap.push({ f: newG+newH, g: newG, px: bx, py: by,
                    boxes: newBoxes, key: newKey, parentKey: cur.key,
                    move: { bi, path, dir: di } });
      }
    }
  }
  return { solved: false, nodes, time: performance.now()-t0, fail: 'no solution' };
}

function reconstructSolution(finalKey, closed) {
  const moves = [];
  let k = finalKey;
  while (k !== null) {
    const rec = closed.get(k);
    if (!rec || !rec.move) break;
    moves.push(rec.move);
    k = rec.parentKey;
  }
  moves.reverse();
  let sol = '';
  for (const mv of moves) {
    for (const di of mv.path) sol += LC[di];
    sol += UC[mv.dir];
  }
  return sol;
}

// ── Worker message handler ───────────────────────────────────────────

self.onmessage = (e) => {
  const { type, id, grid, heuristic, heuristics, timeLimitMs, maxNodes } = e.data;
  let board;
  try { board = parseBoard(grid); }
  catch (err) { self.postMessage({ type: 'error', id, error: err.toString() }); return; }

  if (type === 'solve') {
    const result = solve(board, heuristic, timeLimitMs, maxNodes);
    self.postMessage({ type: 'result', id, heuristic, result });
  } else if (type === 'compare') {
    const hs = heuristics || ['naive_manhattan', 'greedy_matching', 'enhanced'];
    for (const h of hs) {
      const freshBoard = parseBoard(grid);
      const result = solve(freshBoard, h, timeLimitMs, maxNodes);
      self.postMessage({ type: 'compare_result', id, heuristic: h, result });
    }
    self.postMessage({ type: 'compare_done', id });
  }
};
