/* 无头数值自检：把两个工具发布的 <script> 抠出来，用最小 DOM 桩跑起来，
   验证「半径邻域计数」与「扩散粒化」两个算子算得对。
   用法： node 4_selftest.js                                                   */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const HERE = __dirname;
const ROOT = path.dirname(HERE);
const TOOLS = {
  count:     path.join(ROOT, '2-tool', 'granulation_radius_tool.html'),
  diffusion: path.join(ROOT, '2-tool', 'diffusion_granulation_tool.html'),
};

/* ---------- 最小 DOM 桩 ---------- */
function ctxStub() {
  const noop = () => {};
  return {
    setTransform: noop, clearRect: noop, fillRect: noop, beginPath: noop, arc: noop,
    fill: noop, stroke: noop, moveTo: noop, lineTo: noop, fillText: noop, save: noop,
    restore: noop, translate: noop, rotate: noop, setLineDash: noop, closePath: noop,
    strokeText: noop, measureText: () => ({ width: 10 })
  };
}
class El {
  constructor(tag) {
    this.tagName = tag || 'div'; this.style = {}; this.dataset = {};
    this.className = ''; this.textContent = ''; this.value = 0; this.checked = false;
    this.innerHTML = '';
    this.width = 900; this.height = 600; this.clientWidth = 900; this.clientHeight = 600;
    this.scrollTop = 0;
    this.classList = { toggle: () => {}, add: () => {}, remove: () => {}, contains: () => false };
    // children 做成按需生成：真实浏览器里 innerHTML 会建出子元素，
    // 桩里没法解析 HTML，于是访问 children[k] 时临时补一个元素出来，
    // 保证 tr.children[3] 这类写法不会拿到 undefined。
    const arr = [];
    this.children = new Proxy(arr, {
      get(t, k) {
        if (typeof k === 'string' && /^\d+$/.test(k)) {
          const n = +k;
          while (t.length <= n) t.push(new El('td'));
          return t[n];
        }
        const v = t[k];
        return typeof v === 'function' ? v.bind(t) : v;
      },
      set(t, k, v) { t[k] = v; return true; }
    });
  }
  addEventListener() {} setAttribute() {} removeAttribute() {}
  appendChild(c) { this.children.push(c); return c; }
  querySelector() { return new El(); }
  closest() { return null; }
  getContext() { return ctxStub(); }
  getBoundingClientRect() { return { left: 0, top: 0, right: 900, bottom: 600 }; }
  get lastChild() { return this.children[this.children.length - 1] || new El(); }
  get parentElement() { return this.__p || (this.__p = new El()); }
}

/* 在一个隔离上下文里跑目标工具，并取回它 console.log 的内容 */
function runTool(htmlPath, testCode) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const m = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!m) throw new Error('no <script> in ' + htmlPath);
  const logs = [];
  const els = {};
  const sandbox = {
    document: {
      getElementById(id) { return els[id] || (els[id] = new El()); },
      createElement(t) { return new El(t); },
      createDocumentFragment() { return new El('frag'); },
      addEventListener() {}
    },
    window: { addEventListener() {}, devicePixelRatio: 1 },
    console: { log: (...a) => logs.push(a.join(' ')) },
    requestAnimationFrame: () => {},
    navigator: { clipboard: { writeText: async () => {} } },
    Blob: function () {}, URL: { createObjectURL: () => '', revokeObjectURL: () => {} },
    setTimeout, Set, Map, Math, JSON, Array, Object, Number, String, Int32Array, Float64Array, Uint8Array
  };
  vm.runInNewContext(m[1] + testCode, sandbox, { filename: path.basename(htmlPath) });
  return logs.join('\n');
}

/* =================== 一、半径邻域计数 =================== */
const countTest = `
(function(){
  const rows = [];
  for (const ds of [0,1,2,3,4,5,6,7]) {
    S.r = 0.12; loadDS(ds);
    let s = 0; for (let i = 0; i < N; i++) s += c[i];
    rows.push({ ds: ds, n: N, mean: +(s / N).toFixed(4), min: cmin, max: cmax,
                sample: [c[0], c[1], c[10], c[N-1]] });
  }
  let mismatch = 0, checked = 0;
  for (const r of [0.05, 0.1, 0.12, 0.25]) {
    for (const ds of [0,2,3,7]) {
      S.r = r; loadDS(ds);
      for (let i = 0; i < N; i++) {
        let k = 1;
        for (let j = 0; j < N; j++) { if (j === i) continue;
          if (Math.hypot(X[i]-X[j], Y[i]-Y[j]) <= r) k++; }
        checked++;
        if (k !== c[i]) { mismatch++; if (mismatch < 4) console.log('MISMATCH ds='+ds+' r='+r+' i='+i); }
      }
    }
  }
  const CURVE_DS = 0;
  S.r = 0.12; loadDS(CURVE_DS);
  let monoMean = true, monoComp = true;
  for (let k = 1; k < curve.length; k++) {
    if (curve[k].mean < curve[k-1].mean - 1e-9) monoMean = false;
    if (curve[k].ncomp > curve[k-1].ncomp) monoComp = false;
  }
  const singletonCount = () => { let k = 0; for (let i = 0; i < N; i++) if (c[i] === 1) k++; return k; };
  const sdCount = () => {
    let s = 0; for (let i = 0; i < N; i++) s += c[i];
    const mu = s / N; let v = 0;
    for (let i = 0; i < N; i++) v += (c[i] - mu) * (c[i] - mu);
    return Math.sqrt(v / N);
  };
  const table = [];
  for (const ds of [0,1,2,3,4,5,6,7]) {
    for (const r of [0.05, 0.12, 0.30]) {
      S.r = r; loadDS(ds);
      let s = 0; for (let i = 0; i < N; i++) s += c[i];
      const mu = s / N, sd = sdCount();
      table.push(ds + ' r=' + r.toFixed(2) + ' mean=' + mu.toFixed(6) +
                 ' sd=' + sd.toFixed(6) + ' cv=' + (mu ? sd / mu : 0).toFixed(6) +
                 ' min=' + cmin + ' max=' + cmax + ' singleton=' + singletonCount());
    }
  }
  S.r = 0.12; loadDS(CURVE_DS);
  console.log(JSON.stringify({
    datasets: rows, checkedPairs: checked, mismatch: mismatch,
    curveDataset: 'points_' + ('0' + CURVE_DS).slice(-2),
    curvePoints: curve.length,
    curveAt_r0: curve[0], curveAt_rMax: curve[curve.length-1],
    monoMeanRising: monoMean, monoCompFalling: monoComp, table: table
  }, null, 1));
})();
`;

/* =================== 二、扩散粒化 =================== */
const diffusionTest = `
(function(){
  const out = { cases: [], table: [], kl: [] };

  function dist(a, b) { return Math.hypot(X[a]-X[b], Y[a]-Y[b]); }

  function check(ds, r) {
    S.r = r; loadDS(ds);
    const own = Array.from(owner), hp = Array.from(hop), pr = Array.from(par);
    const res = { ds: ds, r: r, n: N, ng: granules.length,
                  bd: own.filter(v => v === -1).length,
                  maxHop: granules.length ? Math.max(...granules.map(g => g.maxHop)) : 0,
                  errs: [] };
    const E = (m) => { if (res.errs.length < 5) res.errs.push(m); };
    const D2 = [];
    for (let i = 0; i < N; i++) { D2.push([]); for (let j = 0; j < N; j++) D2[i].push(dist(i,j)); }

    // 1) 划分完整：每点恰好属于一个粒或边界
    if (own.length !== N) E('owner 长度不对');
    if (granules.reduce((a,g)=>a+g.members.length,0) + res.bd !== N) E('粒大小之和 + 边界 ≠ n');

    // 2) 每个粒 ≥2 个点，且种子是其成员
    for (const g of granules) {
      if (g.members.length < 2) E('粒 '+g.seed+' 只有 '+g.members.length+' 个点');
      if (g.members.indexOf(g.seed) < 0) E('种子 '+g.seed+' 不在自己的粒里');
      if (hp[g.seed] !== 0) E('种子跳数不为 0');
    }

    // 3) 种子序：c 单调不增（种子必须是"当时未分配点里 c 最大的"）
    for (let k = 1; k < granules.length; k++) {
      if (c[granules[k].seed] > c[granules[k-1].seed]) E('种子序违反了 c 降序');
    }

    // 4) 跳数与父节点自洽：父节点跳数 = 自己-1，且距离 ≤ r
    for (let i = 0; i < N; i++) {
      if (own[i] < 0) continue;
      if (hp[i] < 0) { E('粒内点的跳数为负'); continue; }
      if (hp[i] === 0) { if (pr[i] !== -1) E('种子不该有父节点'); continue; }
      if (pr[i] < 0 || own[pr[i]] !== own[i]) E('父节点不属于同一个粒');
      else {
        if (hp[pr[i]] !== hp[i] - 1) E('父节点跳数不是 h-1');
        if (dist(i, pr[i]) > r + 1e-9) E('父子距离超过 r');
      }
    }

    // 5) 【独立实现】对每个粒，用「矩阵 + 层层扩张」的另一种写法重算成员集合，应当完全一致
    for (let gi = 0; gi < granules.length; gi++) {
      const g = granules[gi];
      const inG = new Set(g.members);
      const seen = new Set([g.seed]);
      let front = [g.seed];
      while (front.length) {
        const nxt = [];
        for (const u of front) {
          for (let v = 0; v < N; v++) {
            if (seen.has(v) || !inG.has(v)) continue;
            if (D2[u][v] <= r) { seen.add(v); nxt.push(v); }
          }
        }
        front = nxt;
      }
      if (seen.size !== g.members.length) E('粒'+gi+' 闭包重算得到 '+seen.size+' 个点，实际 '+g.members.length);
    }

    // 6) 【关键不变量】任意两个边界点之间的距离必须 > r
    //    否则 c 较大的那个在轮到它时会把另一个（当时仍未分配）吸进来，不可能两个都留在边界
    const bd = []; for (let i = 0; i < N; i++) if (own[i] === -1) bd.push(i);
    let bad = 0;
    for (let a = 0; a < bd.length; a++)
      for (let b = a+1; b < bd.length; b++)
        if (D2[bd[a]][bd[b]] <= r) bad++;
    if (bad) E('有 '+bad+' 对边界点的距离 ≤ r');

    // 7) 边界点的邻居（若有）必须都已被分配
    let badNb = 0;
    const ownSet = own.filter(v => v >= 0);
    for (const b of bd)
      for (let j = 0; j < N; j++) if (j !== b && D2[b][j] <= r && own[j] === -1) badNb++;
    if (badNb) E('边界点之间仍然相邻（'+badNb+' 处）');

    // 8) 扩散事件数 = 非边界点数，且每条事件只出现一次
    if (events.length !== N - res.bd) E('事件数 ≠ 非边界点数');

    // 9) 【独立表征】用并查集另算一遍连通分量。
    //    不限跳数时，扩散到不动 = 连通分量划分，故应有：
    //      粒数 = 点数≥2 的分量个数 ；边界数 = 单点分量个数
    if (S.maxK === 99) {
      const par = Array.from({length: N}, (_, i) => i);
      const find = a => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a]; } return a; };
      for (let i = 0; i < N; i++)
        for (let j = i+1; j < N; j++)
          if (D2[i][j] <= r) { const x = find(i), y = find(j); if (x !== y) par[x] = y; }
      const cnt = {};
      for (let i = 0; i < N; i++) { const rt = find(i); cnt[rt] = (cnt[rt] || 0) + 1; }
      const comps = Object.keys(cnt).map(k => cnt[k]);
      const singles = comps.filter(v => v === 1).length;
      const multi = comps.length - singles;
      if (res.ng !== multi) E('粒数 ' + res.ng + ' ≠ 多点多分量数 ' + multi);
      if (res.bd !== singles) E('边界数 ' + res.bd + ' ≠ 单点分量数 ' + singles);
    }
    res.errs = res.errs.slice(0, 3);
    return res;
  }

  for (const ds of [0,1,2,3,4,5,7]) {
    for (const r of [0.04, 0.06, 0.12, 0.30]) out.cases.push(check(ds, r));
  }
  // 与 Python 版对齐用的表
  for (const ds of [0,1,2,3,4,5,6,7]) {
    for (const r of [0.06, 0.12, 0.30]) {
      S.r = r; loadDS(ds);
      let nh = 0, mx = 0;
      for (let i = 0; i < N; i++) if (hop[i] > mx) mx = hop[i];
      for (const g of granules) if (g.members.length > nh) nh = g.members.length;
      out.table.push('ds=' + ds + ' r=' + r.toFixed(2) +
                     ' ng=' + granules.length +
                     ' bd=' + owner.filter(v => v === -1).length +
                     ' biggest=' + nh + ' maxhop=' + mx);
      // 限住跳数会怎样（默认不限；这里给 1/2/3 跳作对照）
      const kl = [];
      for (const k of [1,2,3]) {
        S.maxK = k; loadDS(ds); S.r = r; loadDS(ds);
        kl.push('k' + k + ':ng=' + granules.length + ',bd=' + owner.filter(v => v === -1).length);
      }
      S.maxK = 99;
      out.kl.push('ds=' + ds + ' r=' + r.toFixed(2) + '  ' + kl.join('  '));
    }
  }
  console.log(JSON.stringify(out, null, 1));
})();
`;

/* =================== 跑 =================== */
const count = JSON.parse(runTool(TOOLS.count, countTest));
const diffusion = JSON.parse(runTool(TOOLS.diffusion, diffusionTest));
console.log(JSON.stringify({ count: count, diffusion: diffusion }, null, 1));
