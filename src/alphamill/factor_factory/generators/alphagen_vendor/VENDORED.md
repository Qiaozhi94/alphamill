# AlphaGen 上游冻结基线

> 本目录在 T003 只冻结可复现的上游基线，不包含任何 AlphaGen 源码。源码 vendor
> 由 T013 完成。

## 上游 pin

| 资产 | 上游 | pin commit | 来源分支 | commit 日期（UTC） | vendor 日期 |
|---|---|---|---|---|---|
| AlphaGen 核心子集基线 | https://github.com/ICT-FinD-Lab/alphagen | `259687e8f316994426416c530a94842a2fe6405e` | `master`（vendor 时默认分支 HEAD） | `2026-06-04T05:54:37Z` | `2026-09-19` |

`docs/alphamill-research-factor-mining.md` 引用的 commit
`259687e8f316994426416c530a94842a2fe6405e` 已在 clone 中确认存在；它与本次默认分支
HEAD 完全相同。pin 使用完整 40 字符 commit，不使用可移动分支引用。

`_upstream_baseline.json` 对以下核心子集的 20 个 pinned-commit blob 逐文件记录 SHA-256；
`baseline_digest` 对 canonical JSON
`{"repo": <repository>, "commit": <commit>, "files": <files>}` 做 SHA-256。

## 四个功能块的实际布局

| 功能块 | 实际上游路径 | 说明 |
|---|---|---|
| 表达式与算子 | `alphagen/data/expression.py`、`alphagen/data/parser.py`、`alphagen/data/exception.py`、`alphagen/config.py` | 表达式 AST、张量算子实现、字符串解析与 RL 启用算子表。`alphagen_generic/operators.py` 是基线算法适配层，不属于本次核心子集。 |
| 张量求值器 / calculator | `alphagen/data/expression.py`、`alphagen/data/calculator.py`、`alphagen/utils/correlation.py`、`alphagen/utils/pytorch_utils.py` | 通用层提供表达式张量求值和 `AlphaCalculator` / `TensorAlphaCalculator`；上游唯一具体适配器位于被丢弃的 `alphagen_qlib/calculator.py`。 |
| 线性协同池 | `alphagen/models/alpha_pool.py`、`alphagen/models/linear_alpha_pool.py`、`alphagen/data/pool_update.py` | 池接口、线性池、权重优化和池变更记录。 |
| RL 环境与 token 化 | `alphagen/rl/env/core.py`、`alphagen/rl/env/wrapper.py`、`alphagen/rl/policy.py`、`alphagen/data/tokens.py`、`alphagen/data/tree.py`、`alphagen/config.py` | Gymnasium 环境、动作掩码、策略特征提取器、token 定义与表达式树构造。 |

清单还包含上述模块的直接运行支撑：`alphagen/utils/{__init__,logging,maybe,misc,random}.py`。

### 实地核对发现的布局偏差

设计按功能边界要求丢弃 `alphagen_qlib/`，但上游实现并未在 import 边界上完全解耦：

- `alphagen/data/expression.py` 直接从 `alphagen_qlib/stock_data.py` 导入 `StockData` 与
  `FeatureType`；
- `alphagen/data/tokens.py` 直接从同一文件导入 `FeatureType`；
- `alphagen_qlib/calculator.py` 是上游唯一把表达式接到具体数据张量的
  `TensorAlphaCalculator` 实现。

因此 T013 不能把所选文件原样复制后宣称已脱离 qlib。它必须在 vendor 最小 diff 中替换这
些类型 / 数据入口，并按 `# [alphamill] <原因>` 标注；AlphaMill 的湖到张量适配器仍放在
vendor 目录外。

## 明确丢弃

| 路径 | 原因 |
|---|---|
| `alphagen_qlib/` | qlib 数据准备、`StockData` 与具体 calculator；由 AlphaMill 快照数据面和外部 adapter 替代。 |
| `requirements.txt` | 上游依赖陈旧且含错误的 qlib 包；现代依赖由本仓 pin。 |
| `gplearn/` | 论文对照 / L2 降级实现，不属于 T013 的四块核心子集。 |
| `dso/` | 论文对照实现，不属于 T013 的四块核心子集。 |

根目录的 `gp.py`、`dso.py` 以及 `alphagen_generic/`、`alphagen_llm/`、`alphagen/trade/`、
`scripts/` 和 `data_collection/` 同样不在所选核心子集内；manifest 的 `excluded` 字段只记录
设计明确规定的四项丢弃集合。

## 修改清单

**none yet — vendoring happens in T013; this file is the frozen baseline**

T013 必须从本文件记录的 immutable commit 取 blob，并以 `_upstream_baseline.json` 为逐文件
比较真相源。规则为“差异集合 == 标注集合”：每个与 baseline 不同的 vendor 文件都必须带
`# [alphamill] <原因>`，且每处修改都须有对应标注；胶水代码不得放进 vendor 目录。

## 许可说明

上游仓库在 pinned commit **没有 LICENSE**，本清单如实记录为 `license: "none"`。按
ADR-0001，本项目仅作个人、私有使用；这不构成公开分发或商业使用授权。若未来计划公开
分发或商业化，必须先联系 AlphaGen 作者澄清并取得许可。

## 精确重生成命令

在 AlphaMill 仓库根目录执行；scratch clone 必须位于
`/tmp/opencode/alphagen-upstream`。命令只读取 pinned commit 的 Git blobs，不读取工作树文件：

```bash
REPO=/tmp/opencode/alphagen-upstream \
COMMIT=259687e8f316994426416c530a94842a2fe6405e \
COMMIT_DATE=2026-06-04T05:54:37Z \
VENDORED_AT=2026-09-19T00:00:00Z \
OUT=src/alphamill/factor_factory/generators/alphagen_vendor/_upstream_baseline.json \
.venv/bin/python - <<'PY'
import hashlib
import json
import os
import subprocess
from pathlib import Path

repository = "https://github.com/ICT-FinD-Lab/alphagen"
repo = os.environ["REPO"]
commit = os.environ["COMMIT"]
files = sorted((
    "alphagen/config.py",
    "alphagen/data/calculator.py",
    "alphagen/data/exception.py",
    "alphagen/data/expression.py",
    "alphagen/data/parser.py",
    "alphagen/data/pool_update.py",
    "alphagen/data/tokens.py",
    "alphagen/data/tree.py",
    "alphagen/models/alpha_pool.py",
    "alphagen/models/linear_alpha_pool.py",
    "alphagen/rl/env/core.py",
    "alphagen/rl/env/wrapper.py",
    "alphagen/rl/policy.py",
    "alphagen/utils/__init__.py",
    "alphagen/utils/correlation.py",
    "alphagen/utils/logging.py",
    "alphagen/utils/maybe.py",
    "alphagen/utils/misc.py",
    "alphagen/utils/pytorch_utils.py",
    "alphagen/utils/random.py",
))
git_env = {**os.environ, "GIT_MASTER": "1"}


def blob(file: str) -> bytes:
    return subprocess.run(
        ["git", "-C", repo, "cat-file", "blob", f"{commit}:{file}"],
        check=True,
        stdout=subprocess.PIPE,
        env=git_env,
    ).stdout


digests = {
    file: "sha256:" + hashlib.sha256(blob(file)).hexdigest()
    for file in files
}
canonical = json.dumps(
    {"repo": repository, "commit": commit, "files": digests},
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
manifest = {
    "schema_version": 1,
    "repository": repository,
    "commit": commit,
    "commit_date": os.environ["COMMIT_DATE"],
    "vendored_at": os.environ["VENDORED_AT"],
    "license": "none",
    "subset": files,
    "excluded": ["alphagen_qlib/", "requirements.txt", "gplearn/", "dso/"],
    "files": digests,
    "baseline_digest": "sha256:" + hashlib.sha256(canonical).hexdigest(),
}
Path(os.environ["OUT"]).write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
PY
```
