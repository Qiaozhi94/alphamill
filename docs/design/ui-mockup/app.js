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
    flow: { reached: 6, rejected: -1, cur: 6, pm: "PM-007", w: "0.34", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "manual_funding_carry", hid: "H-031", hyp: "资金费率套利", genNote: "人工 · 论文因子", genDate: "2026-07-02",
    gen: "manual", scope: "TS", ric: 0.031, icir: 0.88, pos: 63, net: 5.1, cost: "cost_ok", verdict: "promising",
    dv: "v2026.09.12", seed: 22, turnover: "0.4x/周", hold: "p50 3.1d · p90 5d", ntr: 58,
    taker: "0.02%", slip: "0.01%", funding: "+6.8%/年(收益)",
    flow: { reached: 6, rejected: -1, cur: 6, pm: "PM-009", w: "单成员", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "kronos_rev_v3", hid: "H-019", hyp: "Kronos 60m 反转", genNote: "Kronos 基础模型", genDate: "2026-07-18",
    gen: "kronos", scope: "XS", ric: 0.037, icir: 0.44, pos: 54, net: 3.9, cost: "cost_ok", verdict: "promising",
    dv: "v2026.09.12", seed: 33, turnover: "5.1x/周", hold: "p50 4h · p90 9h", ntr: 733,
    taker: "0.05%", slip: "0.04%", funding: "-2.1%/年",
    flow: { reached: 6, rejected: -1, cur: 6, pm: "PM-007", w: "0.41", note10: "dry-run · 2026-08-28 起", note11: "IC 与成本漂移正常" } },

  { id: "alphagen_gen042_f001", hid: "H-042", hyp: "日内动量衰减", genNote: "RL 协同池 · g042", genDate: "2026-08-30",
    gen: "alphagen", scope: "XS", ric: 0.021, icir: 0.29, pos: 52, net: 1.2, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 44, turnover: "4.0x/周", hold: "p50 5h · p90 11h", ntr: 388,
    taker: "0.05%", slip: "0.03%", funding: "-1.8%/年",
    flow: { reached: 2, rejected: -1, cur: 2, pm: null } },

  { id: "gp_alpha_017", hid: "H-051", hyp: "波动率挤压", genNote: "遗传规划", genDate: "2026-08-22",
    gen: "genetic", scope: "TS", ric: 0.018, icir: 0.22, pos: 51, net: 0.7, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 55, turnover: "2.2x/周", hold: "p50 9h · p90 20h", ntr: 190,
    taker: "0.05%", slip: "0.02%", funding: "-0.9%/年",
    flow: { reached: 2, rejected: -1, cur: 2, pm: null } },

  { id: "expr_mom_break_v2", hid: "H-044", hyp: "动量破位", genNote: "表达式枚举", genDate: "2026-08-25",
    gen: "expression", scope: "TS", ric: 0.052, icir: 0.71, pos: 59, net: -2.3, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.12", seed: 66, turnover: "11.7x/周", hold: "p50 2h · p90 5h", ntr: 1204,
    taker: "0.05%", slip: "0.06%", funding: "-4.4%/年",
    flow: { reached: 1, rejected: 1, cur: -1, pm: null } },

  { id: "alphagen_gen041_f009", hid: "H-038", hyp: "期限结构", genNote: "RL 协同池 · g041", genDate: "2026-08-20",
    gen: "alphagen", scope: "XS", ric: 0.046, icir: 0.66, pos: 58, net: -0.8, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.05", seed: 77, turnover: "8.9x/周", hold: "p50 3h · p90 7h", ntr: 902,
    taker: "0.05%", slip: "0.05%", funding: "-3.7%/年",
    flow: { reached: 1, rejected: 1, cur: -1, pm: null } },

  { id: "kronos_rev_v2", hid: "H-019", hyp: "Kronos 60m 反转", genNote: "Kronos 基础模型", genDate: "2026-06-10",
    gen: "kronos", scope: "XS", ric: 0.029, icir: 0.31, pos: 53, net: -0.4, cost: "cost_ok", verdict: "decayed",
    dv: "v2026.09.05", seed: 88, turnover: "4.8x/周", hold: "p50 4h · p90 8h", ntr: 691,
    taker: "0.05%", slip: "0.04%", funding: "-2.0%/年",
    flow: { reached: 6, rejected: -1, cur: 6, pm: "PM-005", w: "0.52", note10: "dry-run · 2026-06-14 起", note11: "已降权 · 2026-09-02 · 归因复盘完成，新假设已入队" } },

  { id: "gp_alpha_009", hid: "H-029", hyp: "均值回复", genNote: "遗传规划", genDate: "2026-07-30",
    gen: "genetic", scope: "TS", ric: -0.004, icir: -0.11, pos: 47, net: -1.1, cost: "cost_negative", verdict: "dead",
    dv: "v2026.09.05", seed: 99, turnover: "6.6x/周", hold: "p50 3h · p90 6h", ntr: 540,
    taker: "0.05%", slip: "0.05%", funding: "-2.8%/年",
    flow: { reached: 1, rejected: 1, cur: -1, pm: null } },

  { id: "manual_oi_diverge", hid: "H-047", hyp: "OI 背离", genNote: "人工 · 假设清单", genDate: "2026-09-01",
    gen: "manual", scope: "XS", ric: 0.026, icir: 0.35, pos: 55, net: 2.2, cost: "cost_ok", verdict: "weak",
    dv: "v2026.09.12", seed: 12, turnover: "1.8x/周", hold: "p50 11h · p90 22h", ntr: 141,
    taker: "0.05%", slip: "0.02%", funding: "-0.7%/年",
    flow: { reached: 2, rejected: -1, cur: 2, pm: null } }
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
  { name: "留出验证", v: 12, cls: "hot" },
  { name: "最终确认", v: 5, cls: "hot" },
  { name: "Champion", v: 2, cls: "ok" },
  { name: "Challenger", v: 3, cls: "ok" },
  { name: "监控", v: 18, cls: "" },
  { name: "衰减", v: 41, cls: "" },
  { name: "停用", v: 96, cls: "" }
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

/* 业务参数：修改即生成新规则版本并记入日志（FR7.4） */
var PARAMS = [
  { g: "交易风控", name: "单日最大亏损熔断", val: "2%", note: "触发后当日停止开新仓" },
  { g: "交易风控", name: "最大回撤熔断", val: "8%", note: "触发后全组合降杠杆" },
  { g: "交易风控", name: "相关性护栏", val: "0.70", note: "组合内两两信号相关上限" },
  { g: "交易风控", name: "单 pair 仓位上限", val: "10%", note: "占权益比例" },
  { g: "验证门禁", name: "留出窗口", val: "90 天", note: "PortfolioDef 整体验证窗" },
  { g: "验证门禁", name: "每周留出晋级上限", val: "5", note: "超出的候选顺延下一周" },
  { g: "验证门禁", name: "样本量裁决阈值", val: "30 / 69 笔", note: "低于 30 不做判定" },
  { g: "验证门禁", name: "IC 降权阈值", val: "0.015", note: "连续 5 日低于阈值自动降权" },
  { g: "成本模型", name: "Taker 费率", val: "0.05%", note: "评测硬过滤字段 · cm-v1" },
  { g: "成本模型", name: "滑点模型", val: "dry-run 校准", note: "随实际成交更新" },
  { g: "信号执行", name: "信号陈旧度上限", val: "4 根决策 K 线", note: "越界信号置空不使用" },
  { g: "信号执行", name: "实盘交易", val: "关闭", note: "需最终确认 + 可信样本量后人工开启", safe: true },
  { g: "交易宇宙", name: "交易宇宙范围", val: "50 pairs", note: "FR1.5 扩容后 · 新增 pair 需过数据质量门" },
  { g: "组合工厂", name: "组合 Top-K", val: "3（硬上限 5）", note: "权重 = 逆波动率" },
  { g: "组合工厂", name: "换手预算", val: "≤ 100% / 周期", note: "超出的候选标记后顺延" },
  { g: "通知", name: "告警通知渠道", val: "Telegram", note: "熔断 / IC 降权 / 同步异常即时推送" },
  { g: "通知", name: "周报生成", val: "每周一 09:00", note: "完整指标体系周报（FR7.5）" }
];

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

/* ── 生命周期工作流（7 个宏观阶段）──
   生成 → 评测（纯度/成本/查重子门）→ 选择期 → 组合 → 验证（留出+最终确认）→ 上线（复核+挂载）→ 监控 */
var MACRO_STAGES = ["生成", "评测", "选择期", "组合", "验证", "上线", "监控"];

function flowStatus(f, m) {
  var fl = f.flow;
  if (m === fl.rejected) return "reject";
  if (m <= fl.reached) return fl.cur === m ? "active" : "done";
  return "pending";
}

function flowWord(st) {
  return st === "done" ? "通过" : st === "active" ? "进行中" : st === "reject" ? "拒绝" : "未到达";
}

/* 因子列表：7 节点迷你进展（悬停显示阶段名与状态） */
function miniFlow(f) {
  return '<span class="mini-flow">' + MACRO_STAGES.map(function (name, m) {
    var st = flowStatus(f, m);
    var decayed = st === "active" && f.verdict === "decayed";
    var tip = name + "：" + (decayed ? "已降权（" + (f.flow.note11 || "") + "）" : flowWord(st));
    return '<span class="mstep ' + st + '" title="' + tip + '">' +
      '<span class="mf ' + st + (decayed ? " warn" : "") + '"></span>' +
      '<span class="mlb">' + name + "</span></span>";
  }).join("") + "</span>";
}

function flowInfo(f, m) {
  var fl = f.flow;
  if (m === 0) return f.hid + " · " + f.genNote;
  if (m === 1) return fl.rejected === 1
    ? (f.cost === "cost_negative" ? "成本否定 → dead" : "纯度门拒绝")
    : "RankIC " + f.ric.toFixed(3) + " · 纯度/成本/查重通过";
  if (m === 2) return fl.reached >= 3 ? "180 天窗口 · 查重通过" : "存续 · 未入选组合";
  if (m === 3) return fl.pm ? "入选 " + fl.pm + " · 权重 " + fl.w : "未入选组合";
  if (m === 4) return "留出 90 天 · 214 笔 · 隔离确认通过";
  if (m === 5) return fl.note10 || "部署前复核 + 挂载";
  if (m === 6) return fl.note11 || "IC 与成本漂移正常";
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
      fl.reached >= 6 ? "当前挂载于 " + fl.pm : "选择期存续 · 未入选组合";
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
  document.getElementById("param-rows").innerHTML = PARAMS.map(function (p) {
    var val = p.safe ? '<span class="badge red">' + p.val + "</span>" : "<b>" + p.val + "</b>";
    return '<tr><td class="muted">' + p.g + "</td><td>" + p.name + "</td><td>" + val +
      '</td><td class="muted">' + p.note + '</td><td><button class="btn sm" disabled>编辑</button></td></tr>';
  }).join("");
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

/* ── 总览：实时流水线动画 ─────────────────────── */
var OVERVIEW_FLOW = [
  { name: "生成", num: "128", label: "本周产出", extra: "存量提案 214" },
  { name: "评测", num: "89", label: "评测中", extra: "本周初筛淘汰 81" },
  { name: "选择期", num: "47", label: "存续", extra: "180 天窗口 · 查重通过" },
  { name: "组合", num: "12", label: "组合验证中", extra: "边际贡献评估 + 冻结" },
  { name: "验证", num: "17", label: "留出 + 最终确认", extra: "每周晋级上限 5" },
  { name: "上线", num: "5", label: "已挂载因子", extra: "PM-007 · PM-009 dry-run" },
  { name: "监控", num: "18", label: "监控中因子", extra: "PnL +6.42% · 衰减 41 · 停用 96" }
];

var SVGNS = "http://www.w3.org/2000/svg";

function renderOverview() {
  document.getElementById("ov-spark").innerHTML = svgChart(360, 44,
    '<polyline points="' + linePath(series(7, 16, 0.42, 0.9, 0), 360, 44, 6) +
    '" fill="none" stroke="#10b981" stroke-width="1.6"/>');

  var host = document.getElementById("flow-anim");
  var W = 1200, H = 268, Y = 112, N = OVERVIEW_FLOW.length;
  var x0 = 70, x1 = W - 70, xs = [];
  for (var i = 0; i < N; i++) xs.push(x0 + i * (x1 - x0) / (N - 1));

  var fbColor = "#7c3aed";
  var svg = '<svg width="100%" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">';
  svg += '<line id="flowlane" x1="' + x0 + '" y1="' + Y + '" x2="' + x1 + '" y2="' + Y + '"/>';
  svg += '<line x1="' + (x0 - 34) + '" y1="' + Y + '" x2="' + (x1 + 34) + '" y2="' + Y +
    '" stroke="#e5e7eb" stroke-width="4" stroke-linecap="round"/>';
  svg += '<line x1="' + (x0 - 34) + '" y1="' + Y + '" x2="' + (x1 + 34) + '" y2="' + Y +
    '" stroke="#2563eb" stroke-width="4" stroke-linecap="round" stroke-dasharray="3 15" opacity="0.3" class="lane-dash"/>';

  /* 淘汰粒子层（画在文字下方） */
  svg += '<g id="falls"></g>';

  OVERVIEW_FLOW.forEach(function (st, i) {
    var x = xs[i];
    svg += '<circle id="halo-' + i + '" cx="' + x + '" cy="' + Y + '" r="11" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>';
    svg += '<text x="' + x + '" y="' + (Y - 56) + '" text-anchor="middle" font-size="13" font-weight="600" fill="#111827">' + st.name + '</text>';
    svg += '<text x="' + x + '" y="' + (Y - 32) + '" text-anchor="middle" font-size="21" font-weight="600" fill="#2563eb">' + st.num + '</text>';
    svg += '<text x="' + x + '" y="' + (Y + 36) + '" text-anchor="middle" font-size="11" fill="#374151">' + st.label + '</text>';
    svg += '<text x="' + x + '" y="' + (Y + 52) + '" text-anchor="middle" font-size="10" fill="#9ca3af">' + st.extra + '</text>';
  });

  /* 证据库：所有拒绝/失败/衰减的归宿，复盘的原材料 */
  var poolY = 208;
  svg += '<rect x="180" y="' + poolY + '" width="960" height="34" rx="6" fill="#f5f3ff" stroke="' +
    fbColor + '" stroke-dasharray="4 4" opacity="0.95"/>';
  svg += '<text x="200" y="' + (poolY + 21) + '" font-size="11" font-weight="600" fill="' + fbColor + '">证据库 · 归因复盘</text>';
  svg += '<text x="1120" y="' + (poolY + 21) + '" text-anchor="end" font-size="11" fill="' + fbColor +
    '">累计淘汰 306 · 本季复盘 12 次 → 新假设入队 9（generation +1）</text>';

  /* 反馈弧：证据库 → 生成 */
  svg += '<path id="fb-path" d="M 185 ' + (poolY + 14) + ' C 115 ' + (poolY + 12) + ', ' + (x0 - 14) + ' ' + (Y + 70) + ', ' + (x0 - 14) + ' ' + (Y + 22) +
    '" fill="none" stroke="' + fbColor + '" stroke-width="2" stroke-dasharray="5 6" opacity="0.55"/>';
  svg += '<path d="M ' + (x0 - 20) + ' ' + (Y + 30) + ' L ' + (x0 - 14) + ' ' + (Y + 18) + ' L ' + (x0 - 8) + ' ' + (Y + 30) +
    '" fill="none" stroke="' + fbColor + '" stroke-width="2" stroke-linecap="round" opacity="0.8"/>';
  svg += '<g id="parts"></g><g id="fb-parts"></g></svg>';
  host.innerHTML = svg;

  var lane = document.getElementById("flowlane");
  var laneLen = lane.getTotalLength();
  var fbPath = document.getElementById("fb-path");
  var fbLen = fbPath.getTotalLength();

  var weights = OVERVIEW_FLOW.map(function (o) { return parseFloat(o.num); });
  var totalW = weights.reduce(function (a, b) { return a + b; }, 0);
  function pickTarget() {
    var r = Math.random() * totalW, acc = 0;
    for (var i = 0; i < weights.length; i++) { acc += weights[i]; if (r <= acc) return i; }
    return N - 1;
  }

  var halos = [];
  for (var hIdx = 0; hIdx < N; hIdx++) halos.push(document.getElementById("halo-" + hIdx));
  var pulseT = {};
  for (var pIdx = 0; pIdx < N; pIdx++) pulseT[pIdx] = -9;

  var parts = [], fbParts = [], falls = [];
  function spawnPart(randomP) {
    var el = document.createElementNS(SVGNS, "circle");
    el.setAttribute("r", "3.4");
    el.setAttribute("fill", "#2563eb");
    el.setAttribute("opacity", "0");
    document.getElementById("parts").appendChild(el);
    parts.push({ p: randomP ? Math.random() * laneLen : 0, target: pickTarget(),
      speed: 55 + Math.random() * 65, el: el, fade: 0 });
  }
  function spawnFb(delay) {
    var el = document.createElementNS(SVGNS, "circle");
    el.setAttribute("r", "3.4");
    el.setAttribute("fill", fbColor);
    el.setAttribute("opacity", "0");
    document.getElementById("fb-parts").appendChild(el);
    fbParts.push({ len: -delay, speed: 110 + Math.random() * 40, el: el });
  }

  for (var sCount = 0; sCount < 34; sCount++) spawnPart(Math.random() * laneLen);
  spawnFb(0); spawnFb(2600); spawnFb(5200);

  /* 淘汰粒子：评测/选择期/组合/验证/监控 各自不定期落入证据库 */
  var FALL_FROM = [1, 2, 3, 4, 6];
  var fallNext = {}, now0 = performance.now();
  FALL_FROM.forEach(function (m) { fallNext[m] = now0 + 1200 + Math.random() * 5200; });
  var fallsG = document.getElementById("falls");

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return;

  var last = performance.now();
  function frame(now) {
    var dt = Math.min(0.05, (now - last) / 1000); last = now;

    /* 淘汰坠落 */
    FALL_FROM.forEach(function (m) {
      if (now >= (fallNext[m] || 0)) {
        fallNext[m] = now + 5000 + Math.random() * 7000;
        var el = document.createElementNS(SVGNS, "circle");
        var decay = m === 6;
        el.setAttribute("r", "2.6");
        el.setAttribute("fill", decay ? "#d97706" : "#9ca3af");
        el.setAttribute("opacity", "0.8");
        fallsG.appendChild(el);
        falls.push({ x: xs[m], y: Y + 8, vy: 85 + Math.random() * 35, el: el, ty: poolY - 2,
          c: decay ? "#d97706" : "#9ca3af" });
      }
    });
    falls = falls.filter(function (f) {
      f.y += f.vy * dt;
      if (f.y >= f.ty) { f.el.parentNode && f.el.parentNode.removeChild(f.el); return false; }
      f.el.setAttribute("cy", f.y.toFixed(1));
      return true;
    });

    parts.forEach(function (pt) {
      var stopX = xs[pt.target];
      if (pt.fade === 0) {
        pt.p += pt.speed * dt;
        if (pt.p > laneLen) pt.p = laneLen;
        var pos = lane.getPointAtLength(pt.p);
        pt.el.setAttribute("cx", pos.x); pt.el.setAttribute("cy", pos.y);
        pt.el.setAttribute("opacity", "0.85");
        if (pt.p >= laneLen || pos.x >= xs[pt.target] - 0.5) { pt.fade = 0.001; pulseT[pt.target] = now; }
      } else {
        pt.fade += dt * 1.6;
        pt.el.setAttribute("opacity", String(Math.max(0, 0.85 - pt.fade)));
        if (pt.fade >= 1) {
          pt.p = 0; pt.target = pickTarget(); pt.fade = 0;
          pt.el.setAttribute("opacity", "0");
        }
      }
    });

    fbParts.forEach(function (pt) {
      pt.len += pt.speed * dt;
      if (pt.len < 0) { pt.el.setAttribute("opacity", "0"); return; }
      if (pt.len >= fbLen) { pulseT[0] = now; pt.len = -(3000 + Math.random() * 5000); return; }
      var pos = fbPath.getPointAtLength(pt.len);
      pt.el.setAttribute("cx", pos.x); pt.el.setAttribute("cy", pos.y);
      pt.el.setAttribute("opacity", "0.9");
    });

    for (var k = 0; k < N; k++) {
      var dt2 = (now - pulseT[k]) / 1000;
      var r = dt2 >= 0 && dt2 < 0.6 ? 11 + 5 * Math.sin(dt2 / 0.6 * Math.PI) : 11;
      halos[k].setAttribute("r", r.toFixed(1));
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

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
renderOverview();

/* hash 深链：#factors / #detail / #strategy … */
(function () {
  var h = location.hash.replace("#", "");
  if (h && document.getElementById("view-" + h)) {
    var navItem = document.querySelector('.nav-item[data-view="' + h + '"]');
    if (navItem) navItem.click();
    else gotoView(h);
  }
})();
