/* ALPHAMILL UI 设计稿 — 交互与假数据渲染
   全部数字为占位假数据；生产实现中以下每个渲染函数对应一个只读 API 端点（ADR-0005）。 */

"use strict";

/* ── 工具 ─────────────────────────────── */
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function series(seed, n, drift, vol, base) {
  const rnd = mulberry32(seed);
  const out = [];
  let v = base;
  for (let i = 0; i < n; i++) {
    v += drift + (rnd() - 0.5) * vol;
    out.push(v);
  }
  return out;
}

function linePath(data, w, h, pad) {
  const min = Math.min.apply(null, data), max = Math.max.apply(null, data);
  const span = max - min || 1;
  return data.map(function (v, i) {
    const x = pad + (i / (data.length - 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / span) * (h - pad * 2);
    return x.toFixed(1) + "," + y.toFixed(1);
  }).join(" ");
}

function svgChart(w, h, content) {
  return '<svg width="100%" height="' + h + '" viewBox="0 0 ' + w + " " + h + '" preserveAspectRatio="none">' +
    '<line x1="0" y1="' + h / 2 + '" x2="' + w + '" y2="' + h / 2 + '" stroke="#222" stroke-width="1"/>' +
    content + "</svg>";
}

function fmtPct(v, digits) {
  return (v >= 0 ? "+" : "") + v.toFixed(digits === undefined ? 2 : digits) + "%";
}

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

/* ── 假数据 ─────────────────────────────── */
var FACTORS = [
  { id: "alphagen_gen042_f003", hyp: "H-042 日内动量衰减", gen: "alphagen", scope: "XS", ric: 0.043, icir: 0.61, pos: 57, net: 8.4, cost: "cost_ok", verdict: "promising", dv: "v2026.09.12", seed: 11, turnover: "3.2x/周", hold: "p50 6.5h · p90 14h", ntr: 412, taker: "0.05%", slip: "0.03%", funding: "-1.2%/年" },
  { id: "manual_funding_carry", hyp: "H-031 资金费率套利", gen: "manual", scope: "TS", ric: 0.031, icir: 0.88, pos: 63, net: 5.1, cost: "cost_ok", verdict: "promising", dv: "v2026.09.12", seed: 22, turnover: "0.4x/周", hold: "p50 3.1d · p90 5d", ntr: 58, taker: "0.02%", slip: "0.01%", funding: "+6.8%/年(收益)" },
  { id: "kronos_rev_v3", hyp: "H-019 Kronos 60m 反转", gen: "kronos", scope: "XS", ric: 0.037, icir: 0.44, pos: 54, net: 3.9, cost: "cost_ok", verdict: "promising", dv: "v2026.09.12", seed: 33, turnover: "5.1x/周", hold: "p50 4h · p90 9h", ntr: 733, taker: "0.05%", slip: "0.04%", funding: "-2.1%/年" },
  { id: "alphagen_gen042_f001", hyp: "H-042 日内动量衰减", gen: "alphagen", scope: "XS", ric: 0.021, icir: 0.29, pos: 52, net: 1.2, cost: "cost_ok", verdict: "weak", dv: "v2026.09.12", seed: 44, turnover: "4.0x/周", hold: "p50 5h · p90 11h", ntr: 388, taker: "0.05%", slip: "0.03%", funding: "-1.8%/年" },
  { id: "gp_alpha_017", hyp: "H-051 波动率挤压", gen: "genetic", scope: "TS", ric: 0.018, icir: 0.22, pos: 51, net: 0.7, cost: "cost_ok", verdict: "weak", dv: "v2026.09.12", seed: 55, turnover: "2.2x/周", hold: "p50 9h · p90 20h", ntr: 190, taker: "0.05%", slip: "0.02%", funding: "-0.9%/年" },
  { id: "expr_mom_break_v2", hyp: "H-044 动量破位", gen: "expression", scope: "TS", ric: 0.052, icir: 0.71, pos: 59, net: -2.3, cost: "cost_negative", verdict: "dead", dv: "v2026.09.12", seed: 66, turnover: "11.7x/周", hold: "p50 2h · p90 5h", ntr: 1204, taker: "0.05%", slip: "0.06%", funding: "-4.4%/年" },
  { id: "alphagen_gen041_f009", hyp: "H-038 期限结构", gen: "alphagen", scope: "XS", ric: 0.046, icir: 0.66, pos: 58, net: -0.8, cost: "cost_negative", verdict: "dead", dv: "v2026.09.05", seed: 77, turnover: "8.9x/周", hold: "p50 3h · p90 7h", ntr: 902, taker: "0.05%", slip: "0.05%", funding: "-3.7%/年" },
  { id: "kronos_rev_v2", hyp: "H-019 Kronos 60m 反转", gen: "kronos", scope: "XS", ric: 0.029, icir: 0.31, pos: 53, net: -0.4, cost: "cost_ok", verdict: "decayed", dv: "v2026.09.05", seed: 88, turnover: "4.8x/周", hold: "p50 4h · p90 8h", ntr: 691, taker: "0.05%", slip: "0.04%", funding: "-2.0%/年" },
  { id: "gp_alpha_009", hyp: "H-029 均值回复", gen: "genetic", scope: "TS", ric: -0.004, icir: -0.11, pos: 47, net: -1.1, cost: "cost_negative", verdict: "dead", dv: "v2026.09.05", seed: 99, turnover: "6.6x/周", hold: "p50 3h · p90 6h", ntr: 540, taker: "0.05%", slip: "0.05%", funding: "-2.8%/年" },
  { id: "manual_oi_diverge", hyp: "H-047 OI 背离", gen: "manual", scope: "XS", ric: 0.026, icir: 0.35, pos: 55, net: 2.2, cost: "cost_ok", verdict: "weak", dv: "v2026.09.12", seed: 12, turnover: "1.8x/周", hold: "p50 11h · p90 22h", ntr: 141, taker: "0.05%", slip: "0.02%", funding: "-0.7%/年" }
];

var BATCHES = [
  { id: "B-20260912", dv: "v2026.09.12", n: 124, prom: 9, weak: 51, dead: 64, cn: 17 },
  { id: "B-20260911", dv: "v2026.09.12", n: 117, prom: 7, weak: 48, dead: 62, cn: 15 },
  { id: "B-20260910", dv: "v2026.09.05", n: 96, prom: 6, weak: 41, dead: 49, cn: 11 },
  { id: "B-20260909", dv: "v2026.09.05", n: 88, prom: 8, weak: 37, dead: 43, cn: 9 }
];

var STAGES = [
  { name: "proposed", v: 214, cls: "" },
  { name: "evaluating", v: 89, cls: "" },
  { name: "selection", v: 47, cls: "" },
  { name: "holdout", v: 12, cls: "hot" },
  { name: "final confirm", v: 5, cls: "hot" },
  { name: "champion", v: 2, cls: "ok" },
  { name: "challenger", v: 3, cls: "ok" },
  { name: "monitoring", v: 18, cls: "" },
  { name: "decayed", v: 41, cls: "" },
  { name: "disabled", v: 96, cls: "" }
];

var LEDGER = [
  { t: "2026-09-12 14:02", type: "deploy_approve", obj: "PM-007 → dry-run", who: "georg", rule: "ADR-0003 v1", ev: "M-8842" },
  { t: "2026-09-12 09:41", type: "holdout_access", obj: "PM-007 · 90d 留出", who: "system", rule: "FR3.4", ev: "M-8817" },
  { t: "2026-09-10 21:15", type: "lifecycle", obj: "kronos_rev_v2 → decayed", who: "georg", rule: "FR6.2 阈值", ev: "M-8701" },
  { t: "2026-09-08 11:20", type: "hypothesis_review", obj: "H-042 · 4 候选入队", who: "georg", rule: "FR6.5", ev: "M-8612" },
  { t: "2026-09-02 16:55", type: "portfolio_freeze", obj: "PM-007 · Top-K=3", who: "system", rule: "ADR-0004", ev: "M-8440" }
];

var POSITIONS = [
  { pair: "BTC-USDT-SWAP", dir: "LONG", entry: "84,120.5", now: "84,301.0", pnl: "+0.23%", pv: "PM-007@r3" },
  { pair: "ETH-USDT-SWAP", dir: "SHORT", entry: "3,084.2", now: "3,102.7", pnl: "-0.60%", pv: "PM-007@r3" },
  { pair: "SOL-USDT-SWAP", dir: "LONG", entry: "182.44", now: "183.19", pnl: "+0.41%", pv: "PM-007@r3" },
  { pair: "DOGE-USDT-SWAP", dir: "SHORT", entry: "0.22180", now: "0.22105", pnl: "+0.34%", pv: "PM-009@r1" }
];

var TRADES = [
  { pair: "ETH-USDT-SWAP", dir: "LONG", pnl: "+1.12%", why: "roi/stop_loss反义", dur: "6h 12m" },
  { pair: "BTC-USDT-SWAP", dir: "LONG", pnl: "+0.87%", why: "exit_signal", dur: "4h 51m" },
  { pair: "BNB-USDT-SWAP", dir: "SHORT", pnl: "-0.44%", why: "stop_loss", dur: "2h 05m" },
  { pair: "SOL-USDT-SWAP", dir: "LONG", pnl: "+0.63%", why: "exit_signal", dur: "8h 40m" },
  { pair: "XRP-USDT-SWAP", dir: "SHORT", pnl: "+0.29%", why: "roi", dur: "5h 18m" }
];

var SERVICES = [
  { name: "quant-data-collector", st: "RUNNING", cls: "pos", lat: "0.8s", note: "CCXT · 50 pairs · ws+rest" },
  { name: "quant-timescaledb", st: "RUNNING", cls: "pos", lat: "3ms", note: "PG16 · 连续聚合正常" },
  { name: "quant-kronos-signal", st: "REAL·HEALTHY", cls: "pos", lat: "1.76s/次", note: "CPU 回退 · /health model_enabled" },
  { name: "quant-freqtrade", st: "RUNNING", cls: "pos", lat: "-", note: "dry-run · 风控三件套挂载" },
  { name: "quant-grafana", st: "RUNNING", cls: "pos", lat: "-", note: "退守平台观测+告警（ADR-0005）" },
  { name: "alphamill-api", st: "PLANNED", cls: "dim", lat: "-", note: "F005 · 统一只读 API" }
];

var AUDIT = [
  { t: "2026-09-10 21:15", act: "lifecycle.downweight", obj: "kronos_rev_v2", who: "georg", ev: "M-8701 · IC 阈值证据" },
  { t: "2026-09-06 03:10", act: "ops.forceexit", obj: "AVAX-USDT-SWAP", who: "georg", ev: "M-8288 · 手动平仓" },
  { t: "2026-09-01 12:00", act: "ops.forceenter", obj: "BTC-USDT-SWAP", who: "georg", ev: "T017 双路径实测" }
];

/* ── 视图切换 ─────────────────────────────── */
var navEl = document.getElementById("nav");
navEl.addEventListener("click", function (e) {
  var item = e.target.closest(".nav-item");
  if (!item) return;
  var views = document.querySelectorAll(".nav-item");
  for (var i = 0; i < views.length; i++) views[i].classList.remove("active");
  item.classList.add("active");
  var secs = document.querySelectorAll(".view");
  for (var j = 0; j < secs.length; j++) secs[j].classList.remove("active");
  document.getElementById("view-" + item.getAttribute("data-view")).classList.add("active");
  document.querySelector("main").scrollTop = 0;
  history.replaceState(null, "", "#" + item.getAttribute("data-view"));
});

document.addEventListener("click", function (e) {
  var g = e.target.closest("[data-goto]");
  if (!g) return;
  var target = document.querySelector('.nav-item[data-view="' + g.getAttribute("data-goto") + '"]');
  if (target) target.click();
});

/* 时钟（UTC） */
function tick() {
  var d = new Date();
  var p = function (x) { return (x < 10 ? "0" : "") + x; };
  document.getElementById("clock").textContent =
    p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + ":" + p(d.getUTCSeconds());
}
setInterval(tick, 1000); tick();

/* ── 漏斗 ─────────────────────────────── */
function renderStages(elId, stages) {
  var max = Math.max.apply(null, stages.map(function (s) { return s.v; }));
  document.getElementById(elId).innerHTML = stages.map(function (s) {
    var w = Math.max(2, (s.v / max) * 100);
    return '<div class="fstage"><div class="name">' + s.name.replace(" ", "_") + '</div>' +
      '<div class="bar"><i class="' + s.cls + '" style="width:' + w + '%"></i></div>' +
      '<div class="val">' + s.v + "</div></div>";
  }).join("");
}

function renderBatches(elId) {
  document.getElementById(elId).innerHTML = "<table><thead><tr>" +
    "<th>BATCH</th><th>DATA_VER</th><th class=\"num\">N</th><th class=\"num\">PROMISING</th><th class=\"num\">DEAD</th><th class=\"num\">COST_NEG</th></tr></thead><tbody>" +
    BATCHES.map(function (b) {
      return "<tr><td><b>" + b.id + "</b></td><td class=\"muted\">" + b.dv + "</td><td class=\"num\">" + b.n +
        "</td><td class=\"num pos\">" + b.prom + '</td><td class="num">' + b.dead +
        '</td><td class="num neg">' + b.cn + "</td></tr>";
    }).join("") + "</tbody></table>";
}

/* ── 因子库 ─────────────────────────────── */
var selectedFactor = FACTORS[0].id;
var compareSet = {};
[FACTORS[0].id, FACTORS[2].id].forEach(function (id) { compareSet[id] = true; });

function verdictBadge(v) {
  var cls = v === "promising" ? "green" : v === "dead" ? "red" : v === "decayed" ? "red" : "dim";
  return '<span class="badge ' + cls + '">' + v + "</span>";
}

function renderFactorTable() {
  var fv = document.getElementById("f-verdict").value;
  var fg = document.getElementById("f-gen").value;
  var fd = document.getElementById("f-dv").value;
  var q = document.getElementById("f-q").value.toLowerCase();
  var rows = FACTORS.filter(function (f) {
    return (!fv || f.verdict === fv) && (!fg || f.gen === fg) && (!fd || f.dv === fd) &&
      (!q || f.id.toLowerCase().indexOf(q) >= 0 || f.hyp.toLowerCase().indexOf(q) >= 0);
  });
  document.getElementById("factor-rows").innerHTML = rows.map(function (f) {
    var sel = f.id === selectedFactor ? " sel" : "";
    return '<tr class="click' + sel + '" data-fid="' + f.id + '">' +
      '<td><input type="checkbox" data-cmp="' + f.id + '"' + (compareSet[f.id] ? " checked" : "") + "></td>" +
      "<td><b>" + f.id + "</b></td><td class=\"muted\">" + esc(f.hyp) + "</td><td>" + f.gen + "</td><td>" + f.scope +
      '</td><td class="num">' + f.ric.toFixed(3) + '</td><td class="num">' + f.icir.toFixed(2) +
      '</td><td class="num">' + f.pos + "</td><td>" +
      (f.cost === "cost_ok" ? '<span class="badge dim">cost_ok</span>' : '<span class="badge red">cost_negative</span>') +
      "</td><td>" + verdictBadge(f.verdict) + '</td><td class="muted">' + f.dv + "</td></tr>";
  }).join("") || '<tr><td colspan="11" class="muted">无匹配候选 — 检查过滤器</td></tr>';
}

document.getElementById("factor-table").addEventListener("click", function (e) {
  var cb = e.target.closest("input[data-cmp]");
  if (cb) {
    var id = cb.getAttribute("data-cmp");
    if (cb.checked) {
      if (Object.keys(compareSet).length >= 4) { cb.checked = false; return; }
      compareSet[id] = true;
    } else { delete compareSet[id]; }
    renderCompare();
    return;
  }
  var tr = e.target.closest("tr.click");
  if (!tr) return;
  selectedFactor = tr.getAttribute("data-fid");
  renderFactorTable();
  renderDetail();
  document.querySelector('.nav-item[data-view="detail"]').click();
});

["f-verdict", "f-gen", "f-dv"].forEach(function (id) {
  document.getElementById(id).addEventListener("change", renderFactorTable);
});
document.getElementById("f-q").addEventListener("input", renderFactorTable);

/* ── 因子详情 ─────────────────────────────── */
function renderDetail() {
  var f = FACTORS.find(function (x) { return x.id === selectedFactor; }) || FACTORS[0];
  document.getElementById("d-id").textContent = f.id.toUpperCase();
  var vb = document.getElementById("d-verdict");
  vb.textContent = f.verdict + " · " + f.hyp;
  vb.className = "badge " + (f.verdict === "promising" ? "green" : f.verdict === "weak" ? "" : "red");
  document.getElementById("d-ric").textContent = f.ric.toFixed(3);
  document.getElementById("d-ric-sub").textContent = "std 0.0" + (10 + f.seed % 40) + " · " + f.dv;
  document.getElementById("d-icir").textContent = f.icir.toFixed(2);
  document.getElementById("d-icir-sub").textContent = "选择期 180d";
  document.getElementById("d-pos").textContent = f.pos + "%";
  var netEl = document.getElementById("d-net");
  netEl.textContent = fmtPct(f.net);
  netEl.className = "big " + (f.net >= 0 ? "pos" : "neg");
  document.getElementById("d-to").textContent = f.turnover;
  document.getElementById("d-hold").textContent = "持有 " + f.hold;
  document.getElementById("d-ntr").textContent = f.ntr;
  document.getElementById("d-pow").textContent =
    f.ntr < 30 ? "UNDERPOWERED · FR3.5" : f.ntr < 70 ? "30~69 临时 PASS" : "≥69 可信判定";

  var eq = series(f.seed, 160, f.net / 900, 0.6, 0);
  var w = 560, h = 170;
  var main = '<polyline points="' + linePath(eq, w, h, 8) + '" fill="none" stroke="' +
    (f.net >= 0 ? "#4af626" : "#ff2a2a") + '" stroke-width="1.4"/>';
  var dd = eq.map(function (v) { return v * 0.35 - 6; });
  main += '<polyline points="' + linePath(dd, w, h, 8) + '" fill="none" stroke="#ff2a2a" stroke-width="1" stroke-dasharray="3 3" opacity="0.7"/>';
  document.getElementById("d-equity").innerHTML = svgChart(w, h, main);
  document.getElementById("d-eq-range").textContent = "2026-03-16 → 2026-09-12 · 选择期";

  var rnd = mulberry32(f.seed + 1);
  var hz = [1, 2, 4, 12, 24];
  document.getElementById("d-icbars").innerHTML = svgChart(560, 110, hz.map(function (hzv, i) {
    var val = Math.max(0.002, f.ric * Math.exp(-0.28 * Math.sqrt(hzv))) * (0.8 + rnd() * 0.4);
    var bh = (val / 0.055) * 80;
    return '<rect x="' + (40 + i * 100) + '" y="' + (95 - bh) + '" width="56" height="' + bh +
      '" fill="#eaeaea" opacity="' + (0.9 - i * 0.13) + '"/>' +
      '<text x="' + (68 + i * 100) + '" y="107" fill="#888" font-size="9" text-anchor="middle">' + hzv + "h</text>";
  }).join(""));

  document.getElementById("d-qbars").innerHTML = svgChart(560, 110, [1, 2, 3, 4, 5].map(function (q, i) {
    var val = (q - 3) * (f.ric * 9) + (f.net >= 0 ? 0.2 : -0.2);
    var bh = Math.abs(val) / 1.2 * 70 + 4;
    var up = val >= 0;
    return '<rect x="' + (40 + i * 100) + '" y="' + (up ? 92 - bh : 92) + '" width="56" height="' + bh +
      '" fill="' + (up ? "#4af626" : "#ff2a2a") + '" opacity="0.85"/>' +
      '<text x="' + (68 + i * 100) + '" y="107" fill="#888" font-size="9" text-anchor="middle">Q' + q + "</text>";
  }).join(""));

  document.getElementById("d-cost").innerHTML =
    "<dt>TAKER 费</dt><dd>" + f.taker + ' <span class="muted">· 硬过滤字段</span></dd>' +
    "<dt>滑点</dt><dd>" + f.slip + ' <span class="muted">· dry-run 成交校准</span></dd>' +
    "<dt>资金费拖累</dt><dd>" + f.funding + ' <span class="muted">· 8h 结算年化</span></dd>' +
    "<dt>成本裁决</dt><dd>" + (f.cost === "cost_ok" ? '<span class="pos">cost_ok</span>' : '<span class="neg">cost_negative → 一律 dead（FR3.2）</span>') + "</dd>";

  document.getElementById("d-manifest").innerHTML =
    "<dt>REPORT</dt><dd>reports/bench/" + f.id + "/" + f.dv + "/report.json</dd>" +
    "<dt>MANIFEST</dt><dd class=\"muted\">M-" + (7000 + f.seed) + " · sha256:9f" + (f.seed * 137) + "e…</dd>" +
    "<dt>窗口</dt><dd>选择期 2026-03-16 → 2026-09-12 · 留出未访问</dd>" +
    "<dt>关联</dt><dd>" + esc(f.hyp) + " · PM-007 成员候选</dd>" +
    "<dt>COST_MODEL</dt><dd class=\"muted\">cm-v1 · 与 data_version 并列入 manifest</dd>";
}

/* ── 对比 ─────────────────────────────── */
var CMP_COLORS = ["#4af626", "#ff2a2a", "#eaeaea", "#8a8a8a"];

function renderCompare() {
  var ids = Object.keys(compareSet);
  var chips = FACTORS.map(function (f) {
    return '<span class="chip' + (compareSet[f.id] ? " on" : "") + '" data-cmpc="' + f.id + '">' + f.id + "</span>";
  });
  document.getElementById("cmp-chips").innerHTML = chips.join("");

  var w = 900, h = 240;
  var content = "";
  var sets = [];
  ids.forEach(function (id, i) {
    var f = FACTORS.find(function (x) { return x.id === id; });
    var eq = series(f.seed, 160, f.net / 900, 0.6, 0);
    sets.push({ f: f, eq: eq });
    content += '<polyline points="' + linePath(eq, w, h, 10) + '" fill="none" stroke="' +
      CMP_COLORS[i % 4] + '" stroke-width="1.3"/>';
  });
  document.getElementById("cmp-chart").innerHTML = svgChart(w, h, content);
  document.getElementById("cmp-count").textContent = ids.length + " SELECTED";
  document.getElementById("cmp-legend").innerHTML = sets.map(function (s, i) {
    return '<span><i style="background:' + CMP_COLORS[i % 4] + '"></i>' + s.f.id + "</span>";
  }).join("");

  for (var i = 0; i < 4; i++) {
    document.getElementById("cmp-h" + i).textContent = sets[i] ? sets[i].f.id : "—";
  }
  var metrics = [
    { name: "RANK_IC", get: function (f) { return f.ric.toFixed(3); }, best: "max" },
    { name: "ICIR", get: function (f) { return f.icir.toFixed(2); }, best: "max" },
    { name: "COST后收益%", get: function (f) { return fmtPct(f.net); }, best: "max" },
    { name: "换手", get: function (f) { return f.turnover; }, best: "min" },
    { name: "毛交易样本", get: function (f) { return f.ntr; }, best: "max" },
    { name: "VERDICT", get: function (f) { return f.verdict; }, best: null }
  ];
  document.getElementById("cmp-rows").innerHTML = metrics.map(function (m) {
    var tds = sets.map(function (s) {
      var v = m.get(s.f);
      var cls = "";
      if (m.best) {
        var vals = sets.map(function (x) { return m.get(x.f); });
        var bestV = m.best === "max" ? Math.max.apply(null, vals.map(parseFloat).filter(function (x) { return !isNaN(x); })) : Math.min.apply(null, vals.map(parseFloat).filter(function (x) { return !isNaN(x); }));
        if (!isNaN(bestV) && parseFloat(v) === bestV && sets.length > 1) cls = ' class="pos"';
      }
      return "<td" + cls + ">" + v + "</td>";
    }).join("");
    return '<tr><td class="muted">' + m.name + "</td>" + tds + "</tr>";
  }).join("");
}

document.getElementById("cmp-chips").addEventListener("click", function (e) {
  var chip = e.target.closest("[data-cmpc]");
  if (!chip) return;
  var id = chip.getAttribute("data-cmpc");
  if (compareSet[id]) { delete compareSet[id]; }
  else if (Object.keys(compareSet).length < 4) { compareSet[id] = true; }
  renderCompare();
  renderFactorTable();
});

/* ── 运营 / 信号 / 平台 / 审计 ─────────────────────── */
function renderOpsPages() {
  var w = 880, h = 200;
  var pnl = series(7, 16, 0.42, 0.9, 0);
  document.getElementById("st-equity").innerHTML = svgChart(w, h,
    '<polyline points="' + linePath(pnl, w, h, 10) + '" fill="none" stroke="#4af626" stroke-width="1.5"/>');

  document.getElementById("pos-rows").innerHTML = POSITIONS.map(function (p) {
    return "<tr><td><b>" + p.pair + "</b></td><td>" + (p.dir === "LONG" ? '<span class="pos">LONG</span>' : '<span class="neg">SHORT</span>') +
      '</td><td class="num">' + p.entry + '</td><td class="num">' + p.now + '</td><td class="num ' +
      (p.pnl[0] === "+" ? "pos" : "neg") + '">' + p.pnl + '</td><td class="muted">' + p.pv + "</td></tr>";
  }).join("");

  document.getElementById("trade-rows").innerHTML = TRADES.map(function (t) {
    return "<tr><td>" + t.pair + "</td><td>" + (t.dir === "LONG" ? '<span class="pos">LONG</span>' : '<span class="neg">SHORT</span>') +
      '</td><td class="num ' + (t.pnl[0] === "+" ? "pos" : "neg") + '">' + t.pnl +
      '</td><td class="muted">' + t.why + '</td><td class="num">' + t.dur + "</td></tr>";
  }).join("");

  var ic = series(15, 30, 0.002, 0.014, 0.03);
  var thY = 170 - (0.015 / 0.06) * 150 - 10;
  document.getElementById("sg-ic").innerHTML = svgChart(560, 170,
    '<line x1="0" y1="' + thY + '" x2="560" y2="' + thY +
    '" stroke="#ff2a2a" stroke-width="1" stroke-dasharray="4 4" opacity="0.7"/>' +
    '<polyline points="' + linePath(ic, 560, 170, 10) + '" fill="none" stroke="#eaeaea" stroke-width="1.4"/>');

  var rnd = mulberry32(42);
  var dots = "";
  for (var i = 0; i < 140; i++) {
    var x = 20 + rnd() * 520, y = 150 - rnd() * rnd() * 130;
    dots += '<rect x="' + x.toFixed(0) + '" y="' + y.toFixed(0) + '" width="3" height="3" fill="#eaeaea" opacity="0.8"/>';
  }
  document.getElementById("sg-scatter").innerHTML = svgChart(560, 170, dots);

  document.getElementById("svc-rows").innerHTML = SERVICES.map(function (s) {
    return "<tr><td><b>" + s.name + "</b></td><td>" + (s.cls === "dim" ? '<span class="badge dim">PLANNED</span>' : '<span class="' + s.cls + '">' + s.st + "</span>") +
      '</td><td class="num">' + s.lat + '</td><td class="muted">' + s.note + "</td></tr>";
  }).join("");

  document.getElementById("audit-rows").innerHTML = AUDIT.map(function (a) {
    return "<tr><td>" + a.t + '</td><td><span class="badge fg">' + a.act + "</span></td><td>" + a.obj +
      '</td><td>' + a.who + '</td><td class="muted">' + a.ev + "</td></tr>";
  }).join("");
}

/* ── 初始化 ─────────────────────────────── */
renderStages("ov-funnel", STAGES.slice(0, 7));
renderBatches("ov-batches");
renderStages("funnel-stages", STAGES);
renderBatches("funnel-batches");
renderFactorTable();
renderDetail();
renderCompare();
renderOpsPages();

/* hash 深链：#factors / #detail / #strategy … */
(function () {
  var h = location.hash.replace("#", "");
  if (h && document.getElementById("view-" + h)) {
    document.querySelector('.nav-item[data-view="' + h + '"]').click();
  }
})();
