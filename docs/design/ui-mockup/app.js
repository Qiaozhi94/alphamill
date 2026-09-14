/* AlphaMill Console 设计稿 — 交互与假数据渲染
   全部数字为占位假数据；生产实现中每个渲染函数对应一个只读 API 端点（ADR-0005）。 */

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
    '<line x1="0" y1="' + h / 2 + '" x2="' + w + '" y2="' + h / 2 + '" stroke="#eef0f2" stroke-width="1"/>' +
    content + "</svg>";
}

function fmtPct(v, digits) {
  return (v >= 0 ? "+" : "") + v.toFixed(digits === undefined ? 2 : digits) + "%";
}

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

/* ── 假数据 ─────────────────────────────── */
/* flow: reached=已走到的最远环节; rejected=被拒绝的环节(-1 无); cur=进行中环节(-1 无);
   pm/w=所属组合与权重(入选才有); note10=挂载运行备注 */
var FACTORS = [
  { id: "alphagen_gen042_f003", hid: "H-042", hyp: "日内动量衰减", genNote: "RL 协同池 · g042", genDate: "2026-08-30",
    gen: "alphagen", scope: "XS", ric: 0.043, icir: 0.61, pos: 57, net: 8.4, cost: "cost_ok", verdict: "promising",
    dv: "v2026.09.12", seed: 11, turnover: "3.2x/周", hold: "p50 6.5h · p90 14h", ntr: 412,
    taker: "0.05%", slip: "0.03%", funding: "-1.2%/年",
    flow: { reached: 3, rejected: -1, cur: 3, pm: "PM-007", w: "0.34", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "manual_funding_carry", hid: "H-031", hyp: "资金费率套利", genNote: "人工 · 论文因子", genDate: "2026-07-02",
    gen: "manual", scope: "TS", ric: 0.031, icir: 0.88, pos: 63, net: 5.1, cost: "cost_ok", verdict: "promising",
    dv: "v2026.09.12", seed: 22, turnover: "0.4x/周", hold: "p50 3.1d · p90 5d", ntr: 58,
    taker: "0.02%", slip: "0.01%", funding: "+6.8%/年(收益)",
    flow: { reached: 3, rejected: -1, cur: 3, pm: "PM-009", w: "单成员", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "kronos_rev_v3", hid: "H-019", hyp: "Kronos 60m 反转", genNote: "Kronos 基础模型", genDate: "2026-07-18",
    gen: "kronos", scope: "XS", ric: 0.037, icir: 0.44, pos: 54, net: 3.9, cost: "cost_ok", verdict: "promising",
    dv: "v2026.09.12", seed: 33, turnover: "5.1x/周", hold: "p50 4h · p90 9h", ntr: 733,
    taker: "0.05%", slip: "0.04%", funding: "-2.1%/年",
    flow: { reached: 3, rejected: -1, cur: 3, pm: "PM-007", w: "0.41", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "alphagen_gen042_f001", hid: "H-042", hyp: "日内动量衰减", genNote: "RL 协同池 · g042", genDate: "2026-08-30",
    gen: "alphagen", scope: "XS", ric: 0.021, icir: 0.29, pos: 52, net: 1.2, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 44, turnover: "4.0x/周", hold: "p50 5h · p90 11h", ntr: 388,
    taker: "0.05%", slip: "0.03%", funding: "-1.8%/年",
    flow: { reached: 0, rejected: -1, cur: 0, pm: null } },

  { id: "gp_alpha_017", hid: "H-051", hyp: "波动率挤压", genNote: "遗传规划", genDate: "2026-08-22",
    gen: "genetic", scope: "TS", ric: 0.018, icir: 0.22, pos: 51, net: 0.7, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 55, turnover: "2.2x/周", hold: "p50 9h · p90 20h", ntr: 190,
    taker: "0.05%", slip: "0.02%", funding: "-0.9%/年",
    flow: { reached: 0, rejected: -1, cur: 0, pm: null } },

  { id: "expr_mom_break_v2", hid: "H-044", hyp: "动量破位", genNote: "表达式枚举", genDate: "2026-08-25",
    gen: "expression", scope: "TS", ric: 0.052, icir: 0.71, pos: 59, net: -2.3, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.12", seed: 66, turnover: "11.7x/周", hold: "p50 2h · p90 5h", ntr: 1204,
    taker: "0.05%", slip: "0.06%", funding: "-4.4%/年",
    flow: { reached: 0, rejected: 0, cur: -1, pm: null } },

  { id: "alphagen_gen041_f009", hid: "H-038", hyp: "期限结构", genNote: "RL 协同池 · g041", genDate: "2026-08-20",
    gen: "alphagen", scope: "XS", ric: 0.046, icir: 0.66, pos: 58, net: -0.8, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.05", seed: 77, turnover: "8.9x/周", hold: "p50 3h · p90 7h", ntr: 902,
    taker: "0.05%", slip: "0.05%", funding: "-3.7%/年",
    flow: { reached: 0, rejected: 0, cur: -1, pm: null } },

  { id: "kronos_rev_v2", hid: "H-019", hyp: "Kronos 60m 反转", genNote: "Kronos 基础模型", genDate: "2026-06-10",
    gen: "kronos", scope: "XS", ric: 0.029, icir: 0.31, pos: 53, net: -0.4, cost: "cost_ok", verdict: "decayed",
    dv: "v2026.09.05", seed: 88, turnover: "4.8x/周", hold: "p50 4h · p90 8h", ntr: 691,
    taker: "0.05%", slip: "0.04%", funding: "-2.0%/年",
    flow: { reached: 3, rejected: -1, cur: 3, pm: "PM-005", w: "0.52", note10: "dry-run · 2026-06-14 起", note11: "已降权 · 2026-09-02 · 归因复盘完成，新假设已入队" } },

  { id: "gp_alpha_009", hid: "H-029", hyp: "均值回复", genNote: "遗传规划", genDate: "2026-07-30",
    gen: "genetic", scope: "TS", ric: -0.004, icir: -0.11, pos: 47, net: -1.1, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.05", seed: 99, turnover: "6.6x/周", hold: "p50 3h · p90 6h", ntr: 540,
    taker: "0.05%", slip: "0.05%", funding: "-2.8%/年",
    flow: { reached: 0, rejected: 0, cur: -1, pm: null } },

  { id: "manual_oi_diverge", hid: "H-047", hyp: "OI 背离", genNote: "人工 · 假设清单", genDate: "2026-09-01",
    gen: "manual", scope: "XS", ric: 0.026, icir: 0.35, pos: 55, net: 2.2, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 12, turnover: "1.8x/周", hold: "p50 11h · p90 22h", ntr: 141,
    taker: "0.05%", slip: "0.02%", funding: "-0.7%/年",
    flow: { reached: 0, rejected: -1, cur: 0, pm: null } }
];

var BATCHES = [
  { id: "B-20260912", dv: "v2026.09.12", n: 124, prom: 9, weak: 51, dead: 64, cn: 17 },
  { id: "B-20260911", dv: "v2026.09.12", n: 117, prom: 7, weak: 48, dead: 62, cn: 15 },
  { id: "B-20260910", dv: "v2026.09.05", n: 96, prom: 6, weak: 41, dead: 49, cn: 11 },
  { id: "B-20260909", dv: "v2026.09.05", n: 88, prom: 8, weak: 37, dead: 43, cn: 9 }
];

var STAGES = [
  { name: "提案", v: 214, cls: "" },
  { name: "评测中", v: 89, cls: "" },
  { name: "选择期", v: 47, cls: "" },
  { name: "组合门", v: 5, cls: "hot" },
  { name: "留出验证", v: 9, cls: "hot" },
  { name: "最终确认", v: 3, cls: "hot" },
  { name: "在跑·Champion", v: 2, cls: "ok" },
  { name: "在跑·Challenger", v: 3, cls: "ok" },
  { name: "衰减", v: 3, cls: "" },
  { name: "停用", v: 2, cls: "" }
];

/* 服务矩阵 */
var SERVICES = [
  { name: "freqtrade 引擎", st: "运行中 · dry-run", ok: true, metric: "今日 -0.31% · 持仓 4 · 同步滞后 42s",
    ops: ["启动", "停止", "重载配置"], danger: ["强制开仓", "强制平仓"] },
  { name: "kronos-signal", st: "真实推理 · 健康", ok: true, metric: "1.76s/次 · 滚动 IC 0.038",
    ops: ["重启"], danger: [] },
  { name: "data-collector", st: "运行中", ok: true, metric: "K 线延迟 0.8s · 缺失 K 线 0",
    ops: ["重启"], danger: [] },
  { name: "timescaledb", st: "运行中", ok: true, metric: "连接 3ms · 连续聚合正常",
    ops: [], danger: [] },
  { name: "grafana", st: "运行中", ok: true, metric: "平台观测与告警 2 看板",
    ops: ["打开"], danger: [] },
  { name: "verify 门禁", st: "通过 · 26 项", ok: true, metric: "2026-09-12 18:04 UTC",
    ops: ["立即运行"], danger: [] }
];

/* 业务参数：全部取自仓库真实配置与代码默认值（最终交付稿，非 mock）
   type: num=数值+单位后缀 / enum=枚举下拉 / dual=双阈值
   来源：freqtrade_bridge/risk/ 代码默认、freqtrade/user_data/config.json、
        KronosFusionStrategy.py 环境变量默认、PRD FR3.2/3.4/3.5、ADR-0004、架构 §4.3 */
var PARAMS = [
  { g: "交易风控", name: "单日亏损熔断", type: "num", v: 3, unit: "%（权益比）", note: "超过后当日停止开新仓", src: "CircuitBreaker 默认" },
  { g: "交易风控", name: "连续亏损熔断", type: "num", v: 3, unit: "笔", note: "连续亏损达到即触发", src: "CircuitBreaker 默认" },
  { g: "交易风控", name: "最大回撤熔断", type: "num", v: 20, unit: "%", note: "全历史权益窗口", src: "DrawdownGuard 默认" },
  { g: "交易风控", name: "相关性护栏", type: "num", v: 0.85, unit: "", note: "回看 72 根 K 线", src: "CorrelationGuard 默认" },
  { g: "交易风控", name: "全局止损", type: "num", v: -10, unit: "%", note: "单笔兜底止损", src: "config.json stoploss" },
  { g: "交易风控", name: "同时持仓上限", type: "num", v: 3, unit: "笔（每笔 100 USDT）", note: "占权益比例由仓位模块约束", src: "config.json max_open_trades" },
  { g: "信号执行", name: "决策周期", type: "enum", v: "5m", opts: ["1m", "5m", "15m"], note: "freqtrade timeframe", src: "config.json" },
  { g: "信号执行", name: "Kronos 最小预期收益", type: "num", v: 0.0005, unit: "", note: "低于阈值不出信号 · 环境变量可调", src: "策略模板默认" },
  { g: "信号执行", name: "入场波动率上限", type: "num", v: 8, unit: "%", note: "高波动不入场", src: "策略模板默认" },
  { g: "信号执行", name: "动态止损下限", type: "num", v: 2.5, unit: "%", note: "动态止损的最小距离", src: "策略模板默认" },
  { g: "信号执行", name: "信号陈旧度上限", type: "num", v: 1, unit: "个因子周期", note: "4h→1h 即 4 根 · 越界置空", src: "架构 §4.3" },
  { g: "信号执行", name: "实盘交易", type: "enum", v: "dry-run", opts: ["dry-run", "paper", "live（需满足最终确认红线）"], safe: true, note: "渐进发布：backtest → dry-run → paper → live", src: "config.json dry_run · PRD FR5.4" },
  { g: "验证门禁", name: "留出窗口", type: "num", v: 90, unit: "天", note: "PortfolioDef 整体验证窗", src: "PRD FR3.4" },
  { g: "验证门禁", name: "每周留出晋级上限", type: "num", v: 5, unit: "个", note: "超出的候选顺延下一周", src: "PRD FR3.4" },
  { g: "验证门禁", name: "样本量裁决阈值", type: "dual", v: [30, 69], unit: "笔", note: "低于 30 不判定 · 30~69 临时 PASS", src: "PRD FR3.5" },
  { g: "组合工厂", name: "组合 Top-K", type: "num", v: 3, unit: "（硬上限 5）", note: "权重 = 逆波动率", src: "ADR-0004" },
  { g: "组合工厂", name: "换手预算", type: "num", v: 100, pre: "≤ ", unit: "% / 周期", note: "超出的候选标记后顺延", src: "ADR-0004" },
  { g: "交易宇宙", name: "交易宇宙范围", type: "num", v: 6, unit: "pairs", note: "BTC/ETH/SOL 等 · 目标扩容 30~50", src: "config.json pair_whitelist" }
];

function fmtVal(p) {
  if (p.type === "dual") return p.v[0] + " / " + p.v[1] + " " + p.unit;
  return (p.pre || "") + p.v + (p.unit ? " " + p.unit : "");
}

/* 记录表：唯一时间线（操作 / 审批 / 生命周期 / 人审 / 系统事件） */
var LOGS = [
  { t: "2026-09-13 09:12", type: "系统", src: "评测台", text: "B-20260912 批次完成 · 124 候选 · promising 9", who: "system", ev: "M-8861" },
  { t: "2026-09-13 02:00", type: "系统", src: "data_bridge", text: "快照导出 v2026.09.12 · 对账通过", who: "system", ev: "M-8855" },
  { t: "2026-09-12 22:30", type: "参数", src: "业务参数", text: "IC 降权阈值 0.018 → 0.015 · 规则版本 rv-6 → rv-7", who: "georg", ev: "M-8830" },
  { t: "2026-09-12 18:04", type: "系统", src: "verify", text: "门禁验证通过 · 26 项检查", who: "georg", ev: "—" },
  { t: "2026-09-12 14:02", type: "审批", src: "部署复核", text: "PM-007 部署前复核通过 → dry-run", who: "georg", ev: "M-8842" },
  { t: "2026-09-12 09:41", type: "系统", src: "validation", text: "PM-007 留出窗访问 · 90 天 · 214 笔", who: "system", ev: "M-8817" },
  { t: "2026-09-10 21:15", type: "生命周期", src: "监控", text: "kronos_rev_v2 触发 IC 阈值 → 自动降权", who: "georg", ev: "M-8701" },
  { t: "2026-09-08 11:20", type: "人审", src: "复盘队列", text: "H-042 人审通过 · 4 候选入队 g042", who: "georg", ev: "M-8612" },
  { t: "2026-09-06 03:10", type: "操作", src: "freqtrade", text: "强制平仓 AVAX-USDT-SWAP · 手动干预", who: "georg", ev: "M-8288" },
  { t: "2026-09-02 16:55", type: "系统", src: "组合构建", text: "PM-007 冻结 · Top-K=3 · 逆波动率权重", who: "system", ev: "M-8440" },
  { t: "2026-09-01 12:00", type: "操作", src: "freqtrade", text: "强制开仓 BTC-USDT-SWAP · 双路径实测", who: "georg", ev: "M-8120" }
];

var POSITIONS = [
  { pair: "BTC-USDT-SWAP", dir: "LONG", entry: "84,120.5", now: "84,301.0", pnl: "+0.23%", dur: "3h 40m", pv: "PM-007@r3" },
  { pair: "ETH-USDT-SWAP", dir: "SHORT", entry: "3,084.2", now: "3,102.7", pnl: "-0.60%", dur: "1h 15m", pv: "PM-007@r3" },
  { pair: "SOL-USDT-SWAP", dir: "LONG", entry: "182.44", now: "183.19", pnl: "+0.41%", dur: "5h 02m", pv: "PM-007@r3" },
  { pair: "DOGE-USDT-SWAP", dir: "SHORT", entry: "0.22180", now: "0.22105", pnl: "+0.34%", dur: "9h 33m", pv: "PM-009@r1" }
];

var TRADES = [
  { pair: "ETH-USDT-SWAP", dir: "LONG", pnl: "+1.12%", why: "止盈", dur: "6h 12m" },
  { pair: "BTC-USDT-SWAP", dir: "LONG", pnl: "+0.87%", why: "信号离场", dur: "4h 51m" },
  { pair: "BNB-USDT-SWAP", dir: "SHORT", pnl: "-0.44%", why: "止损", dur: "2h 05m" },
  { pair: "SOL-USDT-SWAP", dir: "LONG", pnl: "+0.63%", why: "信号离场", dur: "8h 40m" },
  { pair: "XRP-USDT-SWAP", dir: "SHORT", pnl: "+0.29%", why: "止盈", dur: "5h 18m" }
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

function gotoView(name) {
  var target = document.querySelector('.nav-item[data-view="' + name + '"]');
  if (target) { target.click(); return; }
  var secs = document.querySelectorAll(".view");
  for (var j = 0; j < secs.length; j++) secs[j].classList.remove("active");
  document.getElementById("view-" + name).classList.add("active");
  document.querySelector("main").scrollTop = 0;
  history.replaceState(null, "", "#" + name);
}

document.addEventListener("click", function (e) {
  var g = e.target.closest("[data-goto]");
  if (!g) return;
  gotoView(g.getAttribute("data-goto"));
});

/* 左树收起 / 展开 */
document.getElementById("nav-toggle").addEventListener("click", function () {
  var collapsed = document.body.classList.toggle("nav-collapsed");
  this.textContent = collapsed ? "»" : "«";
});

/* 时钟（UTC） */
function tick() {
  var d = new Date();
  var p = function (x) { return (x < 10 ? "0" : "") + x; };
  document.getElementById("clock").textContent =
    p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + ":" + p(d.getUTCSeconds());
}
setInterval(tick, 1000); tick();

/* ── 工厂 ─────────────────────────────── */
function renderStages(elId, stages) {
  var max = Math.max.apply(null, stages.map(function (s) { return s.v; }));
  document.getElementById(elId).innerHTML = stages.map(function (s) {
    var w = Math.max(2, (s.v / max) * 100);
    return '<div class="fstage"><div class="name">' + s.name + "</div>" +
      '<div class="bar"><i class="' + s.cls + '" style="width:' + w + '%"></i></div>' +
      '<div class="val">' + s.v + "</div></div>";
  }).join("");
}

function renderBatches(elId) {
  document.getElementById(elId).innerHTML = "<table><thead><tr>" +
    '<th>批次</th><th>数据版本</th><th class="num">候选</th><th class="num">晋级</th><th class="num">淘汰</th><th class="num">成本否定</th></tr></thead><tbody>' +
    BATCHES.map(function (b) {
      return "<tr><td><b>" + b.id + "</b></td><td class=\"muted mono\">" + b.dv + '</td><td class="num">' + b.n +
        '</td><td class="num pos">' + b.prom + '</td><td class="num">' + b.dead +
        '</td><td class="num neg">' + b.cn + "</td></tr>";
    }).join("") + "</tbody></table>";
}

/* ── 因子库 ─────────────────────────────── */
var selectedFactor = FACTORS[0].id;
var compareSet = {};
[FACTORS[0].id, FACTORS[2].id].forEach(function (id) { compareSet[id] = true; });

function verdictBadge(v) {
  var cls = v === "promising" ? "green" : v === "dead" ? "red" : v === "decayed" ? "amber" : "";
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
      '<td><span class="fid">' + f.id + "</span></td><td class=\"muted\">" + esc(f.hyp) + "</td><td>" + f.gen + "</td><td>" + f.scope +
      '</td><td class="num">' + f.ric.toFixed(3) + '</td><td class="num">' + f.icir.toFixed(2) +
      '</td><td class="num">' + f.pos + "</td><td>" +
      (f.cost === "cost_ok" ? '<span class="badge">cost_ok</span>' : '<span class="badge red">cost_negative</span>') +
      "</td><td>" + miniFlow(f) + '</td><td class="muted mono">' + f.dv + "</td></tr>";
  }).join("") || '<tr><td colspan="11" class="muted">无匹配候选 — 检查过滤器</td></tr>';
}

function updateCompareBtn() {
  var n = Object.keys(compareSet).length;
  var btn = document.getElementById("btn-compare");
  btn.textContent = "对比（" + n + "）";
  btn.disabled = n < 2;
}

document.getElementById("factor-table").addEventListener("click", function (e) {
  var cb = e.target.closest("input[data-cmp]");
  if (cb) {
    var id = cb.getAttribute("data-cmp");
    if (cb.checked) {
      if (Object.keys(compareSet).length >= 4) { cb.checked = false; return; }
      compareSet[id] = true;
    } else { delete compareSet[id]; }
    updateCompareBtn();
    return;
  }
  var tr = e.target.closest("tr.click");
  if (!tr) return;
  selectedFactor = tr.getAttribute("data-fid");
  renderFactorTable();
  renderDetail();
  gotoView("detail");
});

["f-verdict", "f-gen", "f-dv"].forEach(function (id) {
  document.getElementById(id).addEventListener("change", renderFactorTable);
});
document.getElementById("f-q").addEventListener("input", renderFactorTable);

document.getElementById("btn-compare").addEventListener("click", function () {
  if (Object.keys(compareSet).length < 2) return;
  renderCompare();
  gotoView("compare");
});

/* ── 生命周期工作流（四阶段宏观口径 · ADR-0008 / PRD §2.3）──
   研究评测 → 策略组合 → 部署交易 → 监控反馈；数据治理（S1）为全链底座，不计入因子流程 */
var MACRO_STAGES = ["研究评测", "策略组合", "部署交易", "监控反馈"];

function flowStatus(f, m) {
  var fl = f.flow;
  if (m === fl.rejected) return "reject";
  if (m <= fl.reached) return fl.cur === m ? "active" : "done";
  return "pending";
}

function flowWord(st) {
  return st === "done" ? "通过" : st === "active" ? "进行中" : st === "reject" ? "拒绝" : "未到达";
}

/* 因子列表：4 节点迷你进展（悬停显示阶段名与状态） */
function miniFlow(f) {
  return '<span class="mini-flow">' + MACRO_STAGES.map(function (name, m) {
    var st = flowStatus(f, m);
    var decayed = st === "active" && m === 3 && f.verdict === "decayed";
    var tip = name + "：" + (decayed ? "已降权（" + (f.flow.note11 || "") + "）" : flowWord(st));
    return '<span class="mstep ' + st + '" title="' + tip + '">' +
      '<span class="mf ' + st + (decayed ? " warn" : "") + '"></span>' +
      '<span class="mlb">' + name + "</span></span>";
  }).join("") + "</span>";
}

function flowInfo(f, m) {
  var fl = f.flow;
  if (m === 0) {
    if (fl.rejected === 0) return f.cost === "cost_negative" ? "成本否定 → dead" : "纯度门拒绝";
    return "RankIC " + f.ric.toFixed(3) + " · 纯度/成本/查重通过" +
      (fl.reached >= 1 ? " · 选择期存续" : " · 评测中");
  }
  if (m === 1) return fl.pm
    ? "入选 " + fl.pm + " · 权重 " + fl.w + " · 已过留出/最终确认"
    : (fl.reached >= 1 ? "组合候选评估中" : "未到达");
  if (m === 2) return fl.reached >= 2 ? (fl.note10 || "部署前复核 + 挂载") : "未到达";
  if (m === 3) return fl.reached >= 3 ? (fl.note11 || "IC 与成本漂移正常") : "未到达";
  return "—";
}

/* 因子详情：单主轴鱼骨图，节点信息上下交错 */
function renderWorkflow(f) {
  var fl = f.flow;
  var cols = MACRO_STAGES.map(function (name, m) {
    var st = flowStatus(f, m);
    var info = st === "pending" ? "未到达" : flowInfo(f, m);
    var dot = '<div class="fsh-dotrow"><span class="fsh-dot ' + st + '">' +
      (st === "done" ? "✓" : st === "reject" ? "✕" : st === "active" ? "●" : "·") + "</span></div>";
    var txt = '<div class="fsh-name">' + name + '</div>' +
      '<div class="fsh-status ' + st + '">' + flowWord(st) + '</div>' +
      '<div class="fsh-info">' + info + "</div>";
    return '<div class="fsh-col ' + st + '">' +
      (m % 2 === 0
        ? '<div class="fsh-slot top">' + txt + "</div>" + dot + '<div class="fsh-slot"></div>'
        : '<div class="fsh-slot"></div>' + dot + '<div class="fsh-slot bottom">' + txt + "</div>") +
      "</div>";
  }).join("");
  document.getElementById("d-flow").innerHTML =
    '<div class="fish-wrap"><div class="fish-inner">' + cols + "</div></div>";
  document.getElementById("d-flow-aux").textContent =
    fl.rejected >= 0 ? "于「" + MACRO_STAGES[fl.rejected] + "」被拒绝" :
      fl.reached >= 3 ? "在跑 · 挂载于 " + fl.pm : "研究评测存续 · 未入选组合";
}

/* ── 因子详情 ─────────────────────────────── */
function renderDetail() {
  var f = FACTORS.find(function (x) { return x.id === selectedFactor; }) || FACTORS[0];
  document.getElementById("d-id").textContent = f.id;
  var vb = document.getElementById("d-verdict");
  vb.textContent = f.verdict;
  vb.className = "badge " + (f.verdict === "promising" ? "green" : f.verdict === "weak" ? "" : f.verdict === "decayed" ? "amber" : "red");
  document.getElementById("d-hyp").textContent = f.hid + " · " + f.hyp + " · " + f.genNote;
  renderWorkflow(f);

  document.getElementById("d-ric").textContent = f.ric.toFixed(3);
  document.getElementById("d-ric-sub").textContent = "std 0.0" + (10 + f.seed % 40) + " · " + f.dv;
  document.getElementById("d-icir").textContent = f.icir.toFixed(2);
  document.getElementById("d-pos").textContent = f.pos + "%";
  var netEl = document.getElementById("d-net");
  netEl.textContent = fmtPct(f.net);
  netEl.className = "big " + (f.net >= 0 ? "pos" : "neg");
  document.getElementById("d-to").textContent = f.turnover;
  document.getElementById("d-hold").textContent = "持有 " + f.hold;
  document.getElementById("d-ntr").textContent = f.ntr;
  document.getElementById("d-pow").textContent =
    f.ntr < 30 ? "UNDERPOWERED" : f.ntr < 70 ? "30~69 临时 PASS" : "≥69 可信判定";

  var eq = series(f.seed, 160, f.net / 900, 0.6, 0);
  var w = 560, h = 170;
  var main = '<polyline points="' + linePath(eq, w, h, 8) + '" fill="none" stroke="#2563eb" stroke-width="1.6"/>';
  var dd = eq.map(function (v) { return v * 0.35 - 6; });
  main += '<polyline points="' + linePath(dd, w, h, 8) + '" fill="none" stroke="#dc2626" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>';
  document.getElementById("d-equity").innerHTML = svgChart(w, h, main);
  document.getElementById("d-eq-range").textContent = "2026-03-16 → 2026-09-12 · 选择期";

  var rnd = mulberry32(f.seed + 1);
  var hz = [1, 2, 4, 12, 24];
  document.getElementById("d-icbars").innerHTML = svgChart(560, 110, hz.map(function (hzv, i) {
    var val = Math.max(0.002, f.ric * Math.exp(-0.28 * Math.sqrt(hzv))) * (0.8 + rnd() * 0.4);
    var bh = (val / 0.055) * 80;
    return '<rect x="' + (40 + i * 100) + '" y="' + (95 - bh) + '" width="56" height="' + bh +
      '" fill="#2563eb" opacity="' + (0.85 - i * 0.13) + '"/>' +
      '<text x="' + (68 + i * 100) + '" y="107" fill="#9ca3af" font-size="9" text-anchor="middle">' + hzv + "h</text>";
  }).join(""));

  document.getElementById("d-qbars").innerHTML = svgChart(560, 120, [1, 2, 3, 4, 5].map(function (q, i) {
    var val = (q - 3) * (f.ric * 9) + (f.net >= 0 ? 0.2 : -0.2);
    var bh = Math.abs(val) / 1.6 * 50 + 4;
    var up = val >= 0;
    return '<rect x="' + (40 + i * 100) + '" y="' + (up ? 60 - bh : 60) + '" width="56" height="' + bh +
      '" fill="' + (up ? "#10b981" : "#ef4444") + '" opacity="0.85"/>' +
      '<text x="' + (68 + i * 100) + '" y="114" fill="#9ca3af" font-size="9" text-anchor="middle">Q' + q + "</text>";
  }).join(""));

  document.getElementById("d-cost").innerHTML =
    "<dt>Taker 费</dt><dd>" + f.taker + ' <span class="muted">· 硬过滤字段</span></dd>' +
    "<dt>滑点</dt><dd>" + f.slip + ' <span class="muted">· dry-run 成交校准</span></dd>' +
    "<dt>资金费拖累</dt><dd>" + f.funding + ' <span class="muted">· 8h 结算年化</span></dd>' +
    "<dt>成本裁决</dt><dd>" + (f.cost === "cost_ok" ? '<span class="pos">cost_ok</span>' : '<span class="neg">cost_negative → 一律 dead</span>') + "</dd>";

  document.getElementById("d-manifest").innerHTML =
    "<dt>报告</dt><dd class=\"mono\">reports/bench/" + f.id + "/" + f.dv + "/report.json</dd>" +
    "<dt>manifest</dt><dd class=\"mono muted\">M-" + (7000 + f.seed) + " · sha256:9f" + (f.seed * 137) + "e…</dd>" +
    "<dt>窗口</dt><dd>选择期 2026-03-16 → 2026-09-12 · 留出未访问</dd>" +
    "<dt>关联</dt><dd>" + esc(f.hid + " " + f.hyp) + (f.flow.pm ? " · " + f.flow.pm + " 成员" : " · 未入组") + "</dd>" +
    "<dt>成本模型</dt><dd class=\"mono muted\">cm-v1 · 与 data_version 并列入 manifest</dd>";
}

/* ── 对比 ─────────────────────────────── */
var CMP_COLORS = ["#2563eb", "#10b981", "#d97706", "#7c3aed"];

function renderCompare() {
  var ids = Object.keys(compareSet);
  document.getElementById("cmp-chips").innerHTML = FACTORS.map(function (f) {
    return '<span class="chip' + (compareSet[f.id] ? " on" : "") + '" data-cmpc="' + f.id + '">' + f.id + "</span>";
  }).join("");

  var w = 900, h = 240;
  var content = "";
  var sets = [];
  ids.forEach(function (id) {
    var f = FACTORS.find(function (x) { return x.id === id; });
    var eq = series(f.seed, 160, f.net / 900, 0.6, 0);
    sets.push({ f: f, eq: eq });
    content += '<polyline points="' + linePath(eq, w, h, 10) + '" fill="none" stroke="' +
      CMP_COLORS[sets.length % 4] + '" stroke-width="1.3"/>';
  });
  document.getElementById("cmp-chart").innerHTML = svgChart(w, h, content);
  document.getElementById("cmp-count").textContent = ids.length + " 项";
  document.getElementById("cmp-legend").innerHTML = sets.map(function (s, i) {
    return '<span><i style="background:' + CMP_COLORS[i % 4] + '"></i>' + s.f.id + "</span>";
  }).join("");

  for (var i = 0; i < 4; i++) {
    document.getElementById("cmp-h" + i).textContent = sets[i] ? sets[i].f.id : "—";
  }
  var metrics = [
    { name: "Rank IC", get: function (f) { return f.ric.toFixed(3); }, best: "max" },
    { name: "ICIR", get: function (f) { return f.icir.toFixed(2); }, best: "max" },
    { name: "成本后收益 %", get: function (f) { return fmtPct(f.net); }, best: "max" },
    { name: "换手", get: function (f) { return f.turnover; }, best: null },
    { name: "毛交易样本", get: function (f) { return String(f.ntr); }, best: "max" },
    { name: "结论", get: function (f) { return f.verdict; }, best: null }
  ];
  document.getElementById("cmp-rows").innerHTML = metrics.map(function (m) {
    var tds = sets.map(function (s) {
      var v = m.get(s.f);
      var cls = "";
      if (m.best && sets.length > 1) {
        var nums = sets.map(function (x) { return parseFloat(m.get(x.f)); }).filter(function (x) { return !isNaN(x); });
        var bestV = m.best === "max" ? Math.max.apply(null, nums) : Math.min.apply(null, nums);
        if (!isNaN(bestV) && parseFloat(v) === bestV) cls = ' class="pos"';
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
  updateCompareBtn();
});

/* ── 策略运营 ─────────────────────────────── */
function renderStrategy() {
  var w = 880, h = 200;
  var pnl = series(7, 16, 0.42, 0.9, 0);
  document.getElementById("st-equity").innerHTML = svgChart(w, h,
    '<polyline points="' + linePath(pnl, w, h, 10) + '" fill="none" stroke="#10b981" stroke-width="1.6"/>');

  /* 信号源滚动 IC */
  var ic = series(15, 30, 0.002, 0.014, 0.03);
  var thY = 150 - (0.015 / 0.06) * 130 - 8;
  document.getElementById("sg-ic").innerHTML = svgChart(560, 150,
    '<line x1="0" y1="' + thY + '" x2="560" y2="' + thY +
    '" stroke="#dc2626" stroke-width="1" stroke-dasharray="4 4" opacity="0.6"/>' +
    '<polyline points="' + linePath(ic, 560, 150, 10) + '" fill="none" stroke="#334155" stroke-width="1.4"/>');

  document.getElementById("pos-rows").innerHTML = POSITIONS.map(function (p) {
    return "<tr><td><b>" + p.pair + "</b></td><td>" + (p.dir === "LONG" ? '<span class="pos">LONG</span>' : '<span class="neg">SHORT</span>') +
      '</td><td class="num">' + p.entry + '</td><td class="num">' + p.now + '</td><td class="num ' +
      (p.pnl[0] === "+" ? "pos" : "neg") + '">' + p.pnl + '</td><td class="num muted">' + p.dur +
      '</td><td class="muted mono">' + p.pv + "</td></tr>";
  }).join("");

  document.getElementById("trade-rows").innerHTML = TRADES.map(function (t) {
    return "<tr><td>" + t.pair + "</td><td>" + (t.dir === "LONG" ? '<span class="pos">LONG</span>' : '<span class="neg">SHORT</span>') +
      '</td><td class="num ' + (t.pnl[0] === "+" ? "pos" : "neg") + '">' + t.pnl +
      '</td><td class="muted">' + t.why + '</td><td class="num">' + t.dur + "</td></tr>";
  }).join("");
}

/* ── 设置：服务矩阵 + 记录表 ─────────────────────── */
function renderMatrix() {
  document.getElementById("svc-rows").innerHTML = SERVICES.map(function (s) {
    var st = s.ok === true ? '<span class="pos">' + s.st + "</span>" :
      s.ok === false ? '<span class="neg">' + s.st + "</span>" : '<span class="badge">规划中</span>';
    var ops = s.ops.map(function (o) { return '<button class="btn sm" disabled>' + o + "</button>"; }).join(" ");
    var danger = s.danger.map(function (o) { return '<button class="btn sm danger" disabled>' + o + "</button>"; }).join(" ");
    return '<tr><td><b class="mono">' + s.name + "</b></td><td>" + st +
      '</td><td class="muted">' + s.metric + '</td><td><div class="ops">' + ops + " " + danger + "</div></td></tr>";
  }).join("");
}

function renderParams() {
  document.getElementById("param-rows").innerHTML = PARAMS.map(function (p, i) {
    var val = p.safe ? '<span class="badge red">' + fmtVal(p) + "</span>" : "<b>" + fmtVal(p) + "</b>";
    return "<tr><td><b>" + p.name + '</b></td><td class="muted">' + p.g + "</td>" +
      '<td class="muted">' + p.note + ' <span class="mono" style="font-size:10px;color:var(--text-3);">· ' + p.src + "</span></td>" +
      "<td>" + val + '</td><td><button class="btn sm" data-act="edit" data-i="' + i + '">编辑</button></td></tr>';
  }).join("");
}

document.getElementById("param-rows").addEventListener("click", function (e) {
  var btn = e.target.closest('[data-act="edit"]');
  if (!btn) return;
  openParamModal(parseInt(btn.getAttribute("data-i"), 10));
});

var pmIdx = -1;
function openParamModal(i) {
  pmIdx = i;
  var p = PARAMS[i];
  document.getElementById("pm-name").textContent = p.name;
  document.getElementById("pm-meta").textContent = p.g + " · 来源：" + p.src;
  document.getElementById("pm-desc").textContent = p.note;
  var f = document.getElementById("pm-fields");
  if (p.type === "enum") {
    f.innerHTML = '<select id="pm-v" class="modal-input">' +
      p.opts.map(function (o) { return '<option' + (o === p.v ? " selected" : "") + '>' + o + '</option>'; }).join("") + '</select>';
  } else if (p.type === "dual") {
    f.innerHTML = '<div class="dual"><input id="pm-v" class="modal-input" inputmode="numeric" value="' + p.v[0] + '">' +
      '<span class="dual-sep">/</span><input id="pm-v2" class="modal-input" inputmode="numeric" value="' + p.v[1] + '">' +
      '<span class="unit">' + p.unit + '</span></div>';
  } else {
    f.innerHTML = '<div class="unit-wrap">' + (p.pre ? '<span class="unit">' + p.pre + '</span>' : '') +
      '<input id="pm-v" class="modal-input" inputmode="decimal" value="' + p.v + '">' +
      (p.unit ? '<span class="unit">' + p.unit + '</span>' : '') + '</div>';
  }
  document.getElementById("param-modal").style.display = "flex";
  setTimeout(function () { var inp = document.getElementById("pm-v"); if (inp) { inp.focus(); inp.select(); } }, 30);
}

function closeParamModal() {
  document.getElementById("param-modal").style.display = "none";
}

function saveParam() {
  if (pmIdx < 0) { closeParamModal(); return; }
  var p = PARAMS[pmIdx];
  var oldV = fmtVal(p);
  var nv;
  if (p.type === "enum") {
    nv = document.getElementById("pm-v").value;
  } else if (p.type === "dual") {
    var a1 = parseFloat(document.getElementById("pm-v").value);
    var b1 = parseFloat(document.getElementById("pm-v2").value);
    if (isNaN(a1) || isNaN(b1)) { toast("请输入有效的数字阈值"); return; }
    nv = a1 + " / " + b1 + " " + p.unit;
  } else {
    var num = parseFloat(document.getElementById("pm-v").value);
    if (isNaN(num)) { toast("请输入有效数字（可含负号与小数）"); return; }
    nv = (p.pre || "") + num + (p.unit ? " " + p.unit : "");
  }
  if (nv === oldV) { closeParamModal(); return; }
  if (p.type === "dual") p.v = [a1, b1];
  else p.v = num;
  paramRV += 1;
  var d = new Date(), pad = function (x) { return (x < 10 ? "0" : "") + x; };
  var ts = d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate()) + " " +
    pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds());
  LOGS.unshift({ t: ts, type: "参数", src: "业务参数",
    text: p.name + "：" + nv + " · 规则版本 rv-" + (paramRV - 1) + " → rv-" + paramRV,
    who: "georg", ev: "界面修改" });
  renderParams();
  renderLogs();
  var rn = document.getElementById("rv-num");
  if (rn) rn.textContent = "rv-" + paramRV;
  toast("参数「" + p.name + "」已保存 · 规则版本 rv-" + (paramRV - 1) + " → rv-" + paramRV + "，已记入日志记录");
  closeParamModal();
}

document.getElementById("pm-close").addEventListener("click", closeParamModal);
document.getElementById("pm-cancel").addEventListener("click", closeParamModal);
document.getElementById("pm-save").addEventListener("click", saveParam);
document.getElementById("pm-fields").addEventListener("keydown", function (e) {
  if (e.key === "Enter") saveParam();
  if (e.key === "Escape") closeParamModal();
});
document.getElementById("param-modal").addEventListener("click", function (e) {
  if (e.target === this) closeParamModal();
});
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeParamModal();
});

function toast(msg) {
  var t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(t._timer);
  t._timer = setTimeout(function () { t.classList.remove("show"); }, 3200);
}

function renderLogs() {
  var ft = document.getElementById("log-type").value;
  var rows = LOGS.filter(function (l) { return !ft || l.type === ft; });
  document.getElementById("log-rows").innerHTML = rows.map(function (l) {
    return '<tr><td class="mono muted">' + l.t + '</td><td><span class="badge blue">' + l.type + "</span></td>" +
      '<td class="mono muted">' + l.src + "</td><td>" + l.text + "</td><td>" + l.who +
      '</td><td class="mono muted">' + l.ev + "</td></tr>";
  }).join("") || '<tr><td colspan="6" class="muted">该类型暂无记录</td></tr>';
  document.getElementById("log-count").textContent = "共 " + rows.length + " 条";
}

document.getElementById("log-type").addEventListener("change", renderLogs);

/* 设置页 tab */
document.querySelectorAll(".tab-btn").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
    btn.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach(function (p) { p.classList.remove("active"); });
    document.getElementById("tab-" + btn.getAttribute("data-tab")).classList.add("active");
  });
});

/* ── 总览：北极星 + 动态工作流（五阶段口径 · ADR-0008）──
   S1 数据治理 = 底座条（不占漏斗节点）；主链 S2 研究评测 → S3 策略组合 → S4 部署交易 →
   S5 监控反馈；S5 → S2 复盘回流弧。实时模式下粒子是语义化的：候选沿主链流动，在门禁处
   按通过率晋级或坠落「证据库」，紫色粒子沿回流弧把人审后的新假设带回研究评测。 */
var SVGNS = "http://www.w3.org/2000/svg";

var OV_STAGES = [
  {
    idx: "S2", name: "研究评测", anchor: "proposed · evaluating", fr: "FR2 · FR3.1-3.4",
    desc: "把假设变成组合就绪因子（存续 + 晋级裁决 + 成本后为正）",
    live: { num: "214", unit: "存量候选", sub1: "本周新增 128 · 评测中 89", sub2: "选择期存续 47 · 有效独立 31" },
    detail: [
      ["本周新增候选", "128", "漏斗分母 · 不设产出目标（ADR-0008）"],
      ["有效独立数", "31", "选择期 purged CV 的 OOS PnL 聚类 · 防自欺护栏"],
      ["成本后为正占比", "34%", "taker / maker / 零成本三档 · cost_negative 一律 dead"],
      ["查重拒绝", "7", "|ρ| > 0.99 拒绝 · 0.90~0.99 标记变体"],
      ["最大流失级", "成本门", "FR3.8 周报逐级指认"],
      ["假设 → 结论中位", "6.2 天", "可审计结论：promising / dead / underpowered"]
    ]
  },
  {
    idx: "S3", name: "策略组合", anchor: "validated", fr: "FR4 · FR3.4/3.5",
    desc: "边际贡献门 → Top-K/权重 → 冻结 PortfolioDef → 留出 → 最终确认",
    live: { num: "17", unit: "组合验证中", sub1: "组合门 5 · 留出 9 · 最终确认 3", sub2: "留出通过率 71% · 本周晋级 2/5" },
    detail: [
      ["留出通过率", "71%", "90 天留出 · PortfolioDef 整体裁决"],
      ["样本量三级裁决", "5 / 1 / 0", "≥69 可信 / 30~69 临时 PASS / <30 UNDERPOWERED"],
      ["边际贡献门拒绝", "4", "无正边际贡献不进入冻结"],
      ["换手达标率", "100%", "单周期换手 ≤100%（FR4.4）"],
      ["Top-K 配置", "3 · 硬上限 5", "选择期逆波动率权重"],
      ["防泄漏违例", "0", "看结果后改字段 → 新 ID 重跑，必须为 0（FR4.5）"]
    ]
  },
  {
    idx: "S4", name: "部署交易", anchor: "champion · challenger", fr: "FR5",
    desc: "部署前复核 → 挂载 → dry-run / paper，确定性系统执行，风控不可绕过",
    live: { num: "2", unit: "在跑组合", sub1: "5 因子 · Challenger 3 待替换", sub2: "确认 → 挂载 0.6 天 · parity 100%" },
    detail: [
      ["部署前复核通过率", "86%", "晚于留出窗的最近窗口 · challenger 替换重做（FR5.2）"],
      ["确认 → 挂载", "0.6 天", "门槛 ≤1 天（G5）"],
      ["决策时 parity", "100%", "离线特征 → 预测 → 仓位 → order-intent（FR5.7）"],
      ["执行四桶", "96.4% accepted", "intended / attempted / accepted / failed"],
      ["滑点偏差", "+0.4bp", "实际成交回流 → 持续校准 cm-v1"],
      ["风控事件", "1", "相关性护栏触发 · 未熔断 · kill-switch 就绪"]
    ]
  },
  {
    idx: "S5", name: "监控反馈", anchor: "monitoring · decayed · disabled", fr: "FR6 · FR7",
    desc: "北极星承载阶段：衰减观测 → 生命周期动作 → 归因复盘 → 新假设回流",
    live: { num: "+4.8%", unit: "滚动 90 天超额", sub1: "滚动窗 3/4 为正 · 回撤 -2.3% / 阈 -8%", sub2: "降权 3 · 停用 2 · 复盘 12 → 新假设 9" },
    detail: [
      ["滚动 90 天超额", "+4.8%", "成本后 · 相对各策略预注册基准（北极星）"],
      ["滚动窗持续性", "3/4 为正", "最近 4 个滚动 90 天窗 · 要求 ≥3"],
      ["IC 漂移", "-0.002 / 月", "低于 0.015 连续 5 日自动降权"],
      ["回测偏差", "-0.3%", "回测 vs paper · 成本漂移 +2%"],
      ["生命周期动作", "降权 3 · 停用 2", "恢复重验 1/1 = 100%（FR6.2）"],
      ["复盘回流", "12 → 9", "复盘 → 人审入队 · generation+1 · 回到研究评测"]
    ]
  }
];

/* 门禁胶囊：只有真实筛选门显示转化率；S4 → S5 是时间推移，不设百分比 */
var OV_GATE_PILLS = [
  { label: "冻结转化", pct: "26%" },
  { label: "验证 → 挂载", pct: "75%" },
  { label: "持续运行", pct: null }
];
var OV_PASS_RATE = [0.55, 0.75, 1]; // 粒子过门示意通过率（可视化速率，非真实比例）

/* 时段流量周基线：in 流入 / kill 淘汰 / out 流出；hold = 选择期滚存 */
var OV_FLOW = [
  { in: 128, kill: 81, out: 12, hold: 47 },
  { in: 12, kill: 3, out: 9 },
  { in: 9, kill: 1, out: 8 },
  { in: 8, kill: 1, out: 0 }
];
var OV_REVIEW = { review: 3, hyp: 2, decay: 2 }; // 周基线：复盘 / 新假设入队 / 降权

var OV_RANGES = {
  day: { label: "今日", scale: 0.14 },
  week: { label: "本周", scale: 1 },
  month: { label: "本月", scale: 4.2 },
  year: { label: "今年", scale: 46 },
  custom: { label: "自定义区间", scale: 2.6 }
};

var ovMode = "live";
var ovSel = 0;
var ovGeom = null;
var ovAnim = { raf: 0, active: false };

function ovSpark8(scale, base) {
  var r = mulberry32(Math.round(base * 97 + scale * 13));
  var pts = [];
  for (var i = 0; i < 8; i++) {
    pts.push(Math.max(0.4, (base + r() * base * 1.1) * scale * (0.55 + 0.45 * i / 7)));
  }
  return pts;
}

function ovFlowCards() {
  var s = (OV_RANGES[ovMode] || OV_RANGES.week).scale;
  function f(v) { return Math.max(1, Math.round(v * s)); }
  var b = OV_FLOW;
  var rv = f(OV_REVIEW.review), hyp = f(OV_REVIEW.hyp), decay = f(OV_REVIEW.decay);
  return [
    { num: String(f(b[0].in)), unit: "时段流入", sub1: "初筛淘汰 " + f(b[0].kill) + " · 存续滚存 " + f(b[0].hold), sub2: "冻结流出 " + f(b[0].out) + " · 转化 26%", spark: ovSpark8(s, 10) },
    { num: String(f(b[1].in)), unit: "新冻结组合", sub1: "留出/确认淘汰 " + f(b[1].kill), sub2: "验证通过流出 " + f(b[1].out) + " · 转化 75%", spark: ovSpark8(s, 4) },
    { num: String(f(b[2].in)), unit: "进入部署复核", sub1: "复核拒绝 " + f(b[2].kill), sub2: "新挂载 " + f(b[2].out) + " · 用时 0.6 天", spark: ovSpark8(s, 2) },
    { num: String(f(b[3].in)), unit: "进入监控", sub1: "降权 " + decay + " · 停用 " + Math.max(0, decay - 1), sub2: "复盘 " + rv + " → 新假设 " + hyp, spark: ovSpark8(s, 2) }
  ];
}

function ovCardsHtml() {
  var live = ovMode === "live";
  var flows = live ? null : ovFlowCards();
  return '<div class="flow-nodes">' + OV_STAGES.map(function (st, i) {
    var d = live ? st.live : flows[i];
    var spark = "";
    if (!live) {
      spark = '<div class="fnode-spark"><svg width="100%" height="22" viewBox="0 0 100 22" preserveAspectRatio="none">' +
        '<polyline points="' + linePath(d.spark, 100, 22, 3) + '" fill="none" stroke="#10b981" stroke-width="1.4"/>' +
        '</svg><span>阶段流量趋势</span></div>';
    }
    return '<div class="fnode' + (i === ovSel ? " sel" : "") + '" data-i="' + i + '">' +
      '<div class="fnode-top"><span class="fnode-idx">' + st.idx + '</span><span class="fnode-name">' + st.name +
      '</span><span class="fnode-anchor">' + st.anchor + '</span></div>' +
      '<div class="fnode-num">' + d.num + "<small> " + d.unit + "</small></div>" +
      '<div class="fnode-sub">' + d.sub1 + '</div>' +
      '<div class="fnode-sub muted">' + d.sub2 + '</div>' +
      spark +
      '<div class="fnode-foot">' + st.fr + '</div>' +
      '</div>';
  }).join("") + "</div>";
}

function ovDetailRender() {
  var st = OV_STAGES[ovSel];
  var items = st.detail.map(function (m) {
    return '<div class="ovd-item"><div class="ovd-k">' + m[0] + '</div><div class="ovd-v">' + m[1] +
      '</div><div class="ovd-n">' + m[2] + "</div></div>";
  }).join("");
  document.getElementById("ov-detail").innerHTML =
    '<div class="ovd-head"><span class="fnode-idx">' + st.idx + '</span><b>' + st.name + "</b>" +
    '<span class="muted">' + st.desc + '</span><span class="badge blue">' + st.anchor + '</span>' +
    '<span class="muted mono">' + st.fr + "</span></div>" +
    '<div class="ovd-grid">' + items + "</div>";
}

function ovBaseRender() {
  document.getElementById("flow-base").innerHTML =
    '<span class="fb-tag">S1 底座 · 数据治理</span>' +
    '<span class="fb-item">快照 <b class="mono">v2026.09.12</b> <b class="pos">对账通过</b></span>' +
    '<span class="fb-item">缺失/重复 K 线 <b class="pos">0</b></span>' +
    '<span class="fb-item">采集延迟 <b>0.8s</b></span>' +
    '<span class="fb-item">NAS 备份 <b class="pos">09-12 ✓</b></span>' +
    '<span class="fb-item">宇宙 <b>50 对</b></span>' +
    '<span class="fb-note">研究只读不可变快照（FR1 · ADR-0007）——支撑上方全部阶段，失效快照下游必须拒绝</span>';
}

function ovRender() {
  var stage = document.getElementById("flow-stage");
  var W = Math.max(760, stage.clientWidth || 1100);
  var H = 452, cardBot = ovMode === "live" ? 158 : 200, laneY = 246, trayY = 292, trayH = 42, arcY = 424;
  var N = OV_STAGES.length;
  var xs = [];
  for (var i = 0; i < N; i++) xs.push(W * (2 * i + 1) / (2 * N));
  var x0 = xs[0], xL = xs[N - 1];
  var live = ovMode === "live";

  var svg = '<svg id="flow-svg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + " " + H + '">';
  /* 主链 */
  svg += '<line x1="' + (x0 - 44) + '" y1="' + laneY + '" x2="' + (xL + 30) + '" y2="' + laneY + '" stroke="#e5e7eb" stroke-width="4" stroke-linecap="round"/>';
  svg += '<line class="lane-dash" x1="' + (x0 - 44) + '" y1="' + laneY + '" x2="' + (xL + 30) + '" y2="' + laneY + '" stroke="#2563eb" stroke-width="4" stroke-linecap="round" stroke-dasharray="3 15" opacity="0.25"/>';
  svg += '<path d="M ' + (x0 - 42) + " " + (laneY - 6) + " L " + (x0 - 34) + " " + laneY + " L " + (x0 - 42) + " " + (laneY + 6) + '" fill="none" stroke="#9ca3af" stroke-width="1.6"/>';
  svg += '<text x="' + (x0 - 44) + '" y="' + (laneY - 16) + '" font-size="10" fill="#9ca3af">候选流入</text>';
  /* 节点：连接线 + halo */
  for (var i = 0; i < N; i++) {
    svg += '<line x1="' + xs[i] + '" y1="' + cardBot + '" x2="' + xs[i] + '" y2="' + (laneY - 12) + '" stroke="#d1d5db" stroke-width="1.4" stroke-dasharray="2 4"/>';
    svg += '<circle id="ov-halo-' + i + '" cx="' + xs[i] + '" cy="' + laneY + '" r="11" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>';
  }
  /* 门禁胶囊 */
  for (var g = 0; g < N - 1; g++) {
    var mid = (xs[g] + xs[g + 1]) / 2;
    var t = OV_GATE_PILLS[g].label + (OV_GATE_PILLS[g].pct ? " " + OV_GATE_PILLS[g].pct : "");
    var tw = t.length * 6.4 + 18;
    svg += '<line x1="' + mid + '" y1="' + (laneY - 10) + '" x2="' + mid + '" y2="' + (laneY - 3) + '" stroke="#d1d5db" stroke-width="1.2"/>';
    svg += '<rect x="' + (mid - tw / 2) + '" y="' + (laneY - 30) + '" width="' + tw + '" height="20" rx="10" fill="#f3f4f6" stroke="#e5e7eb"/>';
    svg += '<text x="' + mid + '" y="' + (laneY - 16) + '" text-anchor="middle" font-size="10.5" fill="#6b7280">' + t + "</text>";
  }
  /* 证据库托盘 */
  var killTxt;
  if (live) {
    killTxt = "累计淘汰 306 · 降权 3 · 停用 2";
  } else {
    var sc = (OV_RANGES[ovMode] || OV_RANGES.week).scale;
    function kf(v) { return Math.max(1, Math.round(v * sc)); }
    killTxt = "时段淘汰 " + kf(OV_FLOW[0].kill + OV_FLOW[1].kill + OV_FLOW[2].kill) +
      " · 复盘 " + kf(OV_REVIEW.review) + " → 新假设 " + kf(OV_REVIEW.hyp);
  }
  svg += '<rect x="' + (x0 - 30) + '" y="' + trayY + '" width="' + (xL - x0 + 60) + '" height="' + trayH + '" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-dasharray="4 4" opacity="0.95"/>';
  svg += '<text x="' + (x0 - 12) + '" y="' + (trayY + 26) + '" font-size="11" font-weight="600" fill="#7c3aed">证据库 · 归因复盘（失败也是资产）</text>';
  svg += '<text x="' + (xL + 42) + '" y="' + (trayY + 26) + '" text-anchor="end" font-size="11" fill="#7c3aed">' + killTxt + "</text>";
  /* 回流弧 S5 → S2 */
  svg += '<path id="ov-arc" d="M ' + xL + " " + (laneY + 14) + " C " + xL + " " + arcY + ", " + x0 + " " + arcY + ", " + x0 + " " + (laneY + 14) + '" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-dasharray="5 6" opacity="0.55"/>';
  svg += '<path d="M ' + (x0 - 6) + " " + (laneY + 26) + " L " + x0 + " " + (laneY + 16) + " L " + (x0 + 6) + " " + (laneY + 26) + '" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-linecap="round" opacity="0.8"/>';
  svg += '<text x="' + ((x0 + xL) / 2) + '" y="' + (arcY - 10) + '" text-anchor="middle" font-size="10.5" fill="#7c3aed" opacity="0.85">复盘回流 · 归因 → 人审 → 新假设入队（generation+1）· 本季 12 次复盘 → 9 新假设</text>';
  svg += '<g id="ov-parts"></g></svg>';

  stage.innerHTML = svg + ovCardsHtml();
  ovBaseRender();

  ovGeom = {
    xs: xs, laneY: laneY, trayY: trayY,
    halos: OV_STAGES.map(function (_, i) { return document.getElementById("ov-halo-" + i); }),
    pulseT: [-9, -9, -9, -9]
  };
}

function ovStartAnim() {
  if (ovAnim.active) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var partsG = document.getElementById("ov-parts");
  var arc = document.getElementById("ov-arc");
  if (!partsG || !arc || !ovGeom) return;
  ovAnim.active = true;
  var xs = ovGeom.xs, laneY = ovGeom.laneY, trayY = ovGeom.trayY;
  var halos = ovGeom.halos, pulseT = ovGeom.pulseT;
  var arcLen = arc.getTotalLength();

  var parts = [];
  function makeEl(color) {
    var el = document.createElementNS(SVGNS, "circle");
    el.setAttribute("r", "3.4"); el.setAttribute("fill", color); el.setAttribute("opacity", "0");
    partsG.appendChild(el);
    return el;
  }
  function spawn(x) {
    parts.push({ x: x === undefined ? -14 : x, y: laneY, node: 0, st: "run", speed: 110 + Math.random() * 70, fade: 0, el: makeEl("#2563eb") });
  }
  for (var i = 0; i < 16; i++) spawn(24 + Math.random() * (xs[3] - 60));

  var returns = [];
  function spawnRet(delay) {
    returns.push({ len: -delay, speed: 95 + Math.random() * 45, el: makeEl("#7c3aed") });
  }
  spawnRet(1000); spawnRet(4600);

  var last = performance.now();
  function frame(now) {
    if (!ovAnim.active) return;
    var dt = Math.min(0.05, (now - last) / 1000); last = now;

    if (parts.length < 16 && Math.random() < 0.05) spawn();

    parts = parts.filter(function (p) {
      if (p.st === "run") {
        p.x += p.speed * dt;
        var tx = xs[p.node];
        if (p.x >= tx) {
          p.x = tx; pulseT[p.node] = now;
          if (p.node === 3) { p.st = "done"; p.el.setAttribute("fill", "#10b981"); }
          else if (Math.random() < OV_PASS_RATE[p.node]) { p.node++; }
          else { p.st = "fall"; p.el.setAttribute("fill", "#9ca3af"); p.vy = 95 + Math.random() * 55; }
        }
        p.el.setAttribute("cx", p.x.toFixed(1)); p.el.setAttribute("cy", p.y.toFixed(1));
        p.el.setAttribute("opacity", "0.85");
        return true;
      }
      if (p.st === "fall") {
        p.y += p.vy * dt;
        p.el.setAttribute("cy", p.y.toFixed(1));
        if (p.y >= trayY + 8) { p.el.parentNode.removeChild(p.el); return false; }
        return true;
      }
      p.fade += dt * 1.4;
      p.el.setAttribute("opacity", String(Math.max(0, 0.85 - p.fade)));
      if (p.fade >= 1) { p.el.parentNode.removeChild(p.el); return false; }
      return true;
    });

    returns.forEach(function (rp) {
      rp.len += rp.speed * dt;
      if (rp.len < 0) { rp.el.setAttribute("opacity", "0"); return; }
      if (rp.len >= arcLen) { pulseT[0] = now; rp.len = -(5000 + Math.random() * 6000); return; }
      var pos = arc.getPointAtLength(rp.len);
      rp.el.setAttribute("cx", pos.x.toFixed(1)); rp.el.setAttribute("cy", pos.y.toFixed(1));
      rp.el.setAttribute("opacity", "0.9");
    });

    for (var k = 0; k < halos.length; k++) {
      var dt2 = (now - pulseT[k]) / 1000;
      var r = dt2 >= 0 && dt2 < 0.6 ? 11 + 5 * Math.sin(dt2 / 0.6 * Math.PI) : 11;
      halos[k].setAttribute("r", r.toFixed(1));
    }
    ovAnim.raf = requestAnimationFrame(frame);
  }
  ovAnim.raf = requestAnimationFrame(frame);
}

function ovStopAnim() {
  ovAnim.active = false;
  if (ovAnim.raf) cancelAnimationFrame(ovAnim.raf);
}

function renderHero() {
  document.getElementById("ov-spark").innerHTML = svgChart(560, 44,
    '<polyline points="' + linePath(series(7, 24, 0.55, 0.8, 0), 560, 44, 6) + '" fill="none" stroke="#10b981" stroke-width="1.6"/>');
  document.getElementById("ov-spark-pm").innerHTML = svgChart(360, 40,
    '<polyline points="' + linePath(series(31, 18, 0.4, 0.9, 0), 360, 40, 6) + '" fill="none" stroke="#2563eb" stroke-width="1.6"/>');
}

document.querySelectorAll("#ov-seg .seg-btn").forEach(function (b) {
  b.addEventListener("click", function () { ovSetMode(b.getAttribute("data-r")); });
});
document.getElementById("ov-apply").addEventListener("click", function () {
  var f = document.getElementById("ov-from").value, t = document.getElementById("ov-to").value;
  OV_RANGES.custom.label = (f || "起") + " → " + (t || "止");
  ovSetMode("custom");
});
document.getElementById("flow-stage").addEventListener("click", function (e) {
  var n = e.target.closest(".fnode");
  if (!n) return;
  ovSel = parseInt(n.getAttribute("data-i"), 10);
  document.querySelectorAll("#flow-stage .fnode").forEach(function (c) {
    c.classList.toggle("sel", parseInt(c.getAttribute("data-i"), 10) === ovSel);
  });
  ovDetailRender();
});

function ovSetMode(r) {
  ovMode = r;
  document.querySelectorAll("#ov-seg .seg-btn").forEach(function (b) {
    b.classList.toggle("active", b.getAttribute("data-r") === r);
  });
  var custom = document.getElementById("ov-custom");
  var note = document.getElementById("ov-mode-note");
  var pill = document.getElementById("ov-live-pill");
  ovStopAnim();
  if (r === "live") {
    custom.style.display = "none";
    pill.style.display = "inline-flex";
    note.textContent = "实时：粒子 = 候选沿主链流动，按门禁通过率晋级或坠落证据库（速率示意）· 紫色粒子为复盘回流";
    ovRender();
    ovStartAnim();
  } else {
    pill.style.display = "none";
    custom.style.display = r === "custom" ? "inline-flex" : "none";
    var lbl = r === "custom" ? OV_RANGES.custom.label : OV_RANGES[r].label;
    note.textContent = "时段统计：" + lbl + " · 节点为该时段流量，门禁胶囊为转化率，节点下为趋势";
    ovRender();
  }
  ovDetailRender();
}

var ovResizeT = 0;
window.addEventListener("resize", function () {
  clearTimeout(ovResizeT);
  ovResizeT = setTimeout(function () {
    ovStopAnim(); ovRender();
    if (ovMode === "live") ovStartAnim();
  }, 150);
});

/* ── 初始化 ─────────────────────────────── */
renderStages("factory-stages", STAGES);
renderBatches("factory-batches");
renderFactorTable();
updateCompareBtn();
renderDetail();
renderCompare();
renderStrategy();
renderMatrix();
renderParams();
renderLogs();
renderHero();
ovSetMode(ovMode);

/* hash 深链：#factors / #detail / #strategy … */
(function () {
  var h = location.hash.replace("#", "");
  if (h && document.getElementById("view-" + h)) {
    var navItem = document.querySelector('.nav-item[data-view="' + h + '"]');
    if (navItem) navItem.click();
    else gotoView(h);
  }
})();
