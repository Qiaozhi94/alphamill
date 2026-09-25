#!/usr/bin/env python3
"""规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。

校验 docs/features/<version>/Fddd-*/ 三件套：
  - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
  - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
  - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
    review/done 的 tests 路径真实存在
  - 进入开发流转（ready-for-development / developing / code-reviewing）的 tasks.md
    第 3 节必须含 `### [TEST] 组`（层 2 旅程验收轨；只看该节，放错章节判红）
  - BACKLOG.md 与所有非 done Feature 双向集合一致

纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
并补了变异测试。用法：python tools/validate_spec_lifecycle.py
退出码 0 = 全部通过；1 = 存在违规。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# 状态词表 v4.2（sdd-flow 主干）：doc-reviewing / developing / code-reviewing 为规范词。
# 存量旧词（in-progress / review / ready）保留为兼容别名，读取时归一化到规范词——
# 迁移期内两者等价，门禁对两者执法强度一致（见 STATUS_ALIAS）。
STATUS_V4 = (
    "draft",
    "doc-reviewing",
    "ready-for-development",
    "developing",
    "code-reviewing",
    "done",
)
STATUS_ALIAS = {
    "in-progress": "developing",
    "review": "code-reviewing",
    "ready": "ready-for-development",
}
ALLOWED_STATUS = set(STATUS_V4) | set(STATUS_ALIAS)
ALLOWED_GATES = {"0", "1"}


def norm_status(status: str | None) -> str | None:
    """把兼容旧词归一化为 v4.2 规范词；未知词原样返回（交由 ALLOWED_STATUS 判红）。"""
    return STATUS_ALIAS.get(status, status) if status else status


SPEC_SECTIONS = [
    "0. 来源与意图",
    "1. 问题、目标与非目标",
    "2. 用户场景",
    "3. 范围与边界",
    "4. 需求",
    "5. 生命周期与不变量",
    "6. 成功与验收",
    "7. 测试、依赖与决策",
    "8. 待确认问题",
]
DESIGN_SECTIONS = [
    "0. 输入与约束",
    "1. 技术概要与影响面",
    "2. 架构与模块边界",
    "3. 数据模型与 Migration",
    "4. 接口、Contract 与 Event",
    "5. Runtime、Workflow 与并发",
    "6. UI 与可观测性",
    "7. 失败、恢复、安全与兼容",
    "8. 测试策略与验收映射",
    "9. 已确认决策与残余风险",
    "10. 待确认设计问题",
]
TASKS_SECTIONS = [
    "0. 来源与执行规则",
    "1. 前置条件",
    "2. 实现任务",
    "3. 验证与验收任务",
    "4. 依赖与并行关系",
    "5. 明确后移",
]
UNFINISHED_MARKERS = ("TODO", "TBD", "待补", "未补", "pending", "PENDING")
# [TEST] 组是「进入代码开发前」的硬性要求：不含 done（历史 Feature 豁免，纳入会
# 立刻破坏 F001/F004）与 draft（尚未进入流转）；且只认 tasks.md 第 3 节内的标题，
# 放错章节不算数（R2-007）。集合为归一化后的规范词（旧词经 norm_status 映射）。
TEST_GROUP_STATUSES = {"ready-for-development", "developing", "code-reviewing"}
TEST_GROUP_RE = re.compile(r"^###\s+\[TEST\]", re.M)
REQ_RE = re.compile(r"\b(?:FR|DR|TR|IR|UX|NFR)-\d+\b")
AC_RE = re.compile(r"^-\s+\[([ xX])\]\s+\*\*AC-(\d+)\*\*\s*\(([^)]*)\)\s*:\s*(.*)$")
Q_RE = re.compile(r"^-\s+\[([ xX])\]\s+[QD]Q?-\d+")


def parse_frontmatter(text: str) -> dict | None:
    norm = text.replace("\r\n", "\n")
    m = re.match(r"^---\n([\s\S]*?)\n---", norm)
    if not m:
        return None
    fm: dict = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fm


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "\n", text.replace("\r\n", "\n"))


def top_level_sections(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", strip_code_blocks(text), re.M)]


def section_body(text: str, title: str) -> str | None:
    clean = strip_code_blocks(text)
    lines = clean.split("\n")
    start = None
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.+)$", line)
        if m and m.group(1).strip() == title:
            start = i + 1
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        if re.match(r"^##\s", line):
            break
        body.append(line)
    return "\n".join(body)


def requirement_ids(text: str) -> set[str]:
    return set(REQ_RE.findall(text or ""))


def question_section_issues(body: str | None) -> list[str]:
    if body is None:
        return ["章节缺失"]
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    if not lines:
        return ["空章节"]
    if lines == ["无"]:
        return []
    return [
        f"非规范内容（只允许 Q/DQ checkbox 或单独「无」）：{ln[:60]}"
        for ln in lines
        if not Q_RE.match(ln)
    ]


def open_questions(body: str | None) -> int:
    if body is None:
        return 0
    return sum(1 for ln in body.split("\n") if re.match(r"^-\s+\[ \]\s+[QD]Q?-\d+", ln.strip()))


def discover_features(root: pathlib.Path) -> tuple[dict, list[str]]:
    feats: dict[str, dict] = {}
    errors: list[str] = []
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return feats, errors
    for ver in features_dir.iterdir():
        if not ver.is_dir() or ver.name in ("TEMPLATE", "releases"):
            continue
        for f in ver.iterdir():
            if not f.is_dir() or not re.match(r"^F\d{3}-", f.name):
                continue
            files = {n: f / n for n in ("spec.md", "design.md", "tasks.md")}
            missing = [n for n, p in files.items() if not p.is_file()]
            if missing:
                errors.append(f"{f.name}: 三件套缺失: {', '.join(missing)}")
                continue
            feats[f.name] = {
                "dir": f,
                "id": f.name[:4],
                "version_dir": ver.name,
                "spec": files["spec.md"].read_text(encoding="utf-8"),
                "design": files["design.md"].read_text(encoding="utf-8"),
                "tasks": files["tasks.md"].read_text(encoding="utf-8"),
            }
    return feats, errors


# 仓库内真实产物的扩展名白名单（末段扩展名不在其中的 backtick 不算路径引用）。
FILE_EXTENSIONS = frozenset(
    {
        "py",
        "md",
        "ps1",
        "sh",
        "json",
        "jsonl",
        "yml",
        "yaml",
        "toml",
        "cfg",
        "ini",
        "csv",
        "tsv",
        "txt",
        "sql",
        "parquet",
        "lock",
    }
)


def looks_like_test_path(token: str) -> bool:
    """AC 正文里只有形如「仓库内文件路径」的 backtick 才算 tests/验收证据引用。

    接受 `tests/unit/x.py`、`deployment/verify.ps1`、`tests/fixtures/f007/README.md` 这类真实文件；
    拒绝标识符与取值（`promotion_verdict`、`E_INPUT_INVALID`、`[0,30)`、`universe_at(T)`、`DR-005`）
    以及 URL——否则所有进入 code-reviewing 的规格都会报一堆假「路径不存在」。判据：非 URL、含 `/`、
    且最后一段的扩展名在白名单内。

    扩展名必须白名单化，不能只看「末段有点」：F003 AC-010 的 `/health.device=cpu` 满足「有点」，
    被判成「绝对路径」判红，而那句原文又被 `check_doc_consistency` 钉死——两条门禁互相打架，
    唯一出路是收紧本判据（2026-09-26）。
    """
    if token.startswith("http") or "/" not in token:
        return False
    last = token.rsplit("/", 1)[-1]
    if "." not in last:
        return False
    return last.rsplit(".", 1)[-1].lower() in FILE_EXTENSIONS


def check_feature(feat: dict, root: pathlib.Path, errors: list[str]):
    name = feat["dir"].name

    def tag(msg: str) -> None:
        errors.append(f"{name}: {msg}")

    spec_fm = parse_frontmatter(feat["spec"])
    if spec_fm is None:
        tag("spec.md 缺少 frontmatter")
        return
    if spec_fm.get("kind") != "feature":
        tag(f"spec frontmatter kind 应为 feature，实际 {spec_fm.get('kind')}")
    if spec_fm.get("id") != feat["id"]:
        tag(f"spec frontmatter id={spec_fm.get('id')} 与目录 {feat['id']} 不一致")
    if spec_fm.get("status") not in ALLOWED_STATUS:
        tag(f"非法 status: {spec_fm.get('status')}")
    if str(spec_fm.get("gate_version")) not in ALLOWED_GATES:
        tag(f"非法 gate_version: {spec_fm.get('gate_version')}")
    for fname, text in (("design.md", feat["design"]), ("tasks.md", feat["tasks"])):
        fm = parse_frontmatter(text)
        if fm and "status" in fm:
            tag(f"{fname} 不得声明独立 status（spec 是唯一真源）")

    if str(spec_fm.get("gate_version")) != "1":
        return  # gate v0 只做以上结构/元数据校验

    for fname, text, sections in (
        ("spec.md", feat["spec"], SPEC_SECTIONS),
        ("design.md", feat["design"], DESIGN_SECTIONS),
        ("tasks.md", feat["tasks"], TASKS_SECTIONS),
    ):
        actual = set(top_level_sections(text))
        missing = [s for s in sections if s not in actual]
        extra = [s for s in actual if s not in sections]
        if missing:
            tag(f"{fname} 缺失章节: {' | '.join(missing)}")
        if extra:
            tag(f"{fname} 多余顶层章节（须并入固定章节或删除）: {' | '.join(extra)}")

    tasks_clean = strip_code_blocks(feat["tasks"])
    in_section2 = False
    for line in tasks_clean.split("\n"):
        h = re.match(r"^##\s+(.+)$", line)
        if h:
            in_section2 = h.group(1).strip() == "2. 实现任务"
            continue
        if re.match(r"^###\s+Phase", line.strip()) and not in_section2:
            tag("tasks.md 的 Phase 只能作为「2. 实现任务」下的三级标题")
    if norm_status(spec_fm.get("status")) in TEST_GROUP_STATUSES:
        section3 = section_body(feat["tasks"], "3. 验证与验收任务") or ""
        if not TEST_GROUP_RE.search(section3):
            tag("tasks.md 第 3 节缺少必需的 [TEST] 组（层 2 旅程验收轨）")
    for line in tasks_clean.split("\n"):
        t = re.match(r"^-\s+\[([ xX])\]\s+(T\d+)", line)
        if t and t.group(1).lower() == "x" and any(m in line for m in UNFINISHED_MARKERS):
            tag(f"tasks.md 已勾任务 {t.group(2)} 仍含未完成标记")

    spec_q = section_body(feat["spec"], "8. 待确认问题")
    design_dq = section_body(feat["design"], "10. 待确认设计问题")
    for fname, body in (("spec.md", spec_q), ("design.md", design_dq)):
        for issue in question_section_issues(body):
            tag(f"{fname} 待确认问题: {issue}")
    if norm_status(spec_fm.get("status")) in (
        "ready-for-development",
        "developing",
        "code-reviewing",
        "done",
    ):
        open_n = open_questions(spec_q) + open_questions(design_dq)
        if open_n:
            tag(f"{open_n} 个 Q/DQ 未关闭（ready-for-development 及以上不允许）")

    req_ids = requirement_ids(section_body(feat["spec"], "4. 需求") or feat["spec"])
    seen = set()
    for line in strip_code_blocks(feat["spec"]).split("\n"):
        ac = AC_RE.match(line)
        if not ac:
            continue
        if ac.group(2) in seen:
            tag(f"AC-{ac.group(2)} 重复")
        seen.add(ac.group(2))
        refs = set(REQ_RE.findall(ac.group(3)))
        bad = [r for r in refs if r not in req_ids]
        if bad:
            tag(f"AC-{ac.group(2)} 引用不存在的需求: {', '.join(sorted(bad))}")
        tests = [
            token for token in re.findall(r"`([^`]+)`", ac.group(4)) if looks_like_test_path(token)
        ]
        if norm_status(spec_fm.get("status")) in ("code-reviewing", "done") and not tests:
            tag(f"AC-{ac.group(2)} 在 {spec_fm.get('status')} 状态缺少 tests: 路径")
        # tests 路径存在性只在 code-reviewing/done 强制；路径格式任何状态都校验。
        if norm_status(spec_fm.get("status")) not in ("code-reviewing", "done"):
            continue
        for t in tests:
            if t.startswith("/") or ".." in t:
                tag(f"AC-{ac.group(2)} tests 路径不合法（禁止绝对路径/.. 逃逸）: {t}")
                continue
            resolved = (root / t).resolve()
            if not resolved.is_relative_to(root.resolve()):
                tag(f"AC-{ac.group(2)} tests 路径逃逸仓库根: {t}")
            elif not resolved.is_file():
                tag(f"AC-{ac.group(2)} tests 路径不存在: {t}")


def check_backlog(root: pathlib.Path, feats: dict, errors: list[str]):
    backlog = root / "BACKLOG.md"
    if not backlog.is_file():
        errors.append("BACKLOG.md 不存在（feature 活跃索引）")
        return
    rows = []
    row_re = re.compile(
        r"\|\s*(F\d{3}-[^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*\[spec\]\((docs/features/[^)]+)\)\s*\|"
    )
    for line in backlog.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n"):
        if line.lstrip().startswith("## "):
            break  # 只解析活跃索引表；「规划中」等后续小节不参与门禁双向校验
        m = row_re.match(line.strip())
        if m:
            rows.append(
                (m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
            )
    active = [f for f in feats.values() if parse_frontmatter(f["spec"]).get("status") != "done"]
    row_names = {r[0] for r in rows}
    for f in active:
        if f["dir"].name not in row_names:
            errors.append(f"BACKLOG 缺少非 done Feature: {f['dir'].name}")
    for rname, rver, rstatus, rlink in rows:
        f = feats.get(rname)
        if f is None:
            errors.append(f"BACKLOG 含未知 Feature: {rname}")
            continue
        fm = parse_frontmatter(f["spec"])
        if fm.get("status") == "done":
            errors.append(f"BACKLOG 含已 done Feature: {rname}（done 移出活跃索引）")
            continue
        expect_link = f"docs/features/{f['version_dir']}/{rname}/spec.md"
        if rlink != expect_link:
            errors.append(f"BACKLOG {rname} 链接应为 {expect_link}，实际 {rlink}")
        if rstatus != fm.get("status"):
            errors.append(f"BACKLOG {rname} status={rstatus} 与 spec ({fm.get('status')}) 不一致")
        if rver != fm.get("version"):
            errors.append(f"BACKLOG {rname} version={rver} 与 spec ({fm.get('version')}) 不一致")


def verify_repo(root: pathlib.Path = ROOT) -> tuple[bool, list[str]]:
    errors: list[str] = []
    feats, disc = discover_features(root)
    errors.extend(disc)
    seen: dict[str, str] = {}
    for f in feats.values():
        if f["id"] in seen:
            errors.append(f"Feature ID {f['id']} 重复: {seen[f['id']]} 与 {f['dir'].name}")
        seen[f["id"]] = f["dir"].name
        check_feature(f, root, errors)
    check_backlog(root, feats, errors)
    return (not errors, errors)


def main() -> int:
    ok, errors = verify_repo()
    if ok:
        print("validate_spec_lifecycle: 全部通过")
        return 0
    print("validate_spec_lifecycle: 失败", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
