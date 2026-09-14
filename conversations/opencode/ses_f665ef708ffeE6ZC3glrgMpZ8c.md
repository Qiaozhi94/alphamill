---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f665ef708ffeE6ZC3glrgMpZ8c"
title: "ml4t backtest eval diagnostics (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-13T07:17:42Z"
updated_at: "2026-09-13T07:21:27Z"
tokens_input: 202066
tokens_output: 14034
cost: 0.0469
parent_id: "ses_f6664247effe4SLb37r5OF4RZ9"
---

# ml4t backtest eval diagnostics (@explore subagent)

## user · 2026-09-13T07:17:42Z

[CONTEXT] I am analyzing /home/georg/projects/ml4t-zh ("Machine Learning for Trading, 3rd Edition" code). I need to understand its strategy EVALUATION, BACKTESTING, and OVERFITTING-CONTROL machinery in depth, to compare with AlphaMill, a new crypto quant pipeline that has a strict validation gate.

[GOAL] A precise technical description of ml4t's evaluation/backtest stack and the statistical tools it uses to reject false positives. Concrete file paths, function/class names, and what each computes.

[DOWNSTREAM] I will use this to recommend which overfitting/false-discovery controls AlphaMill's evidence gate should implement (e.g. Deflated Sharpe Ratio, Reality Check, cost-survival, holdout discipline).

[REQUEST] Investigate these and report paths + symbols + mechanism:
1. 16_strategy_simulation/: backtesting as falsification; trading-protocol spec; vectorized vs event-driven engines; the specific overfitting controls implemented — Deflated Sharpe Ratio, Rademacher Anti-Serum, White's Reality Check. Find the code that computes them.
2. 20_strategy_synthesis/: IC-Sharpe decorrelation, Fundamental Law diagnostics, model-family cascade, cost-survival analysis, holdout failure modes. What exactly is computed and how.
3. 17_portfolio_construction/: HRP, Kelly, mean-variance, conformal position sizing, allocator comparison.
4. 18_transaction_costs/: cost taxonomy, spread estimation, market impact calibration, VWAP/TWAP/Almgren-Chriss, breakeven costs.
5. 19_risk_management/: VaR/CVaR, drawdown controls, stress testing, kill switches.
6. The ml4t-diagnostic and ml4t-backtest libraries: are they vendored/installed here? What public API do the notebooks call (function names like deflated_sharpe_ratio, white_reality_check, etc.)?

Report structured, technical, with file paths and exact function/class names. Skip plotting code.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-13T07:17:42Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 2 -type d -name \"16_*\" -o -maxdepth 2 -type d -name \"17_*\" -o -maxdepth 2 -type d -name \"18_*\" -o -maxdepth 2 -type d -name \"19_*\" -o -maxdepth 2 -type d -name \"20_*\" 2>/dev/null"})`
- **tool**: `bash({"command": "pip show ml4t-diagnostic ml4t-backtest 2>/dev/null; echo \"---PIP DONE---\"; find / -maxdepth 8 -type d \\( -name \"ml4t_diagnostic*\" -o -name \"ml4t-diagnostic*\" -o -name \"ml4t_backtest*\" -o -name \"ml4t-backtest*\" \\) 2>/dev/null"})`
- **tool**: `glob({"pattern": "**/{16,17,18,19,20}_*/**/*.py", "path": "/home/georg/projects/ml4t-zh"})`


> [reasoning] Let me start by exploring the ml4t-zh repo structure. Launch parallel tools.
<analysis>
**Literal Request**: Map ml4t-zh's evaluation/backtest/overfitting-control machinery across six areas, plus locate ml4t-diagnostic and ml4t-backtest libraries and their public APIs.

**Actual Need**: A precise inventory of statistical false-positive controls (DSR, Reality Check, PBO, cost-survival, holdout) with file paths and symbol names, to decide what AlphaMill's validation gate should adopt.

**Success Looks Like**: Concrete paths + function/class names + what each computes, organized by area, and clear statement on whether ml4t-diagnostic/ml4t-backtest are vendored or installed.
</analysis>

Let me explore the repo structure and locate the relevant directories and libraries in parallel.

  <details><summary>tool output</summary>

  ```text
total 55124
drwxr-xr-x 42 georg georg     4096 Sep 12 01:44 .
drwxr-xr-x 10 georg georg     4096 Sep 10 21:31 ..
-rw-r--r--  1 georg georg     4832 Sep 10 00:21 .env.example
drwxr-xr-x  8 georg georg     4096 Sep 13 13:38 .git
-rw-r--r--  1 georg georg      289 Sep 10 00:21 .gitattributes
drwxr-xr-x  5 georg georg     4096 Sep 10 00:21 .github
-rw-r--r--  1 georg georg     8514 Sep 10 00:21 .gitignore
drwxr-xr-x  3 georg georg     4096 Sep 10 00:21 .jupyter
drwxr-xr-x  3 georg georg     4096 Sep 10 21:50 .omo
-rw-r--r--  1 georg georg     4826 Sep 10 00:21 .pre-commit-config.yaml
-rw-r--r--  1 georg georg       34 Sep 10 00:21 .verified-notebooks.tsv
drwxr-xr-x  3 georg georg     4096 Sep 10 00:21 .workspace
drwxr-xr-x  3 georg georg     4096 Sep 11 01:24 01_process_is_edge
drwxr-xr-x  3 g
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/18_transaction_costs
/home/georg/projects/ml4t-zh/20_strategy_synthesis
/home/georg/projects/ml4t-zh/19_risk_management
/home/georg/projects/ml4t-zh/16_strategy_simulation
/home/georg/projects/ml4t-zh/17_portfolio_construction


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
---PIP DONE---


<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 83 file(s)

/home/georg/projects/ml4t-zh/20_strategy_synthesis/03_signal_quality.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/07_regime_risk.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/02_feature_evaluation.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/08_recommendations.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/05_portfolio_allocation.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/00_holdout_predictions.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/01_aggregate_synthesis.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/04_signal_to_strategy.py
/home/georg/projects/ml4t-zh/20_strategy_synthesis/06_cost_survival.py
/home/georg/projects/ml4t-zh/19_risk_management/09_
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:19:47Z

- **tool**: `bash({"command": "python3 -c \"import ml4t.diagnostic as d; print('DIAG', d.__file__)\" 2>&1; python3 -c \"import ml4t.backtest as b; print('BACK', b.__file__)\" 2>&1; echo \"---\"; python3 -c \"import importlib.util as u; print([m for m in ['ml4t','ml4t_diagnostic','ml4t_backtest'] if u.find_spec(m)])\" 2>&1"})`
- **tool**: `bash({"command": "ls -R /home/georg/projects/ml4t-zh/16_strategy_simulation | head -50; echo \"===17===\"; ls /home/georg/projects/ml4t-zh/17_portfolio_construction; echo \"===18===\"; ls /home/georg/projects/ml4t-zh/18_transaction_costs; echo \"===19===\"; ls /home/georg/projects/ml4t-zh/19_risk_management; echo \"===20===\"; ls /home/georg/projects/ml4t-zh/20_strategy_synthesis"})`
- **tool**: `grep({"pattern": "deflated_sharpe|reality_check|rademacher|anti.?serum|probabilistic_sharpe|PBO|probability_of_backtest|haircut_sharpe|multiple_testing|false_discovery", "path": "/home/georg/projects/ml4t-zh", "output_mode": "files_with_matches", "include": "*.py"})`
- **tool**: `grep({"pattern": "from ml4t|import ml4t", "path": "/home/georg/projects/ml4t-zh", "output_mode": "content", "include": "*.py", "head_limit": 60})`


> [reasoning] The find for ml4t libs timed out. Let me search pip and site-packages more efficiently. Let me look at the directories and pyproject, plus grep for imports.

Let me run parallel searches:
1. Directory structure with markdown files in each area.
2. Find ml4t_diagnostic / ml4t_backtest in site-packages using python.
3. Grep for deflated_sharpe / white_reality_check / rademacher / PBO etc.
4. Read pyproject.
Directory structure mapped. Now let me locate the libraries and the key statistical functions in parallel.

  <details><summary>tool output</summary>

  ```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import ml4t.diagnostic as d; print('DIAG', d.__file__)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'ml4t'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import ml4t.backtest as b; print('BACK', b.__file__)
    ^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'ml4t'
---
[]


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/16_strategy_simulation:
01_backtest_first_principles.ipynb
01_backtest_first_principles.py
02_futures_backtesting.ipynb
02_futures_backtesting.py
03_single_asset_vectorbt.ipynb
03_single_asset_vectorbt.py
04_single_asset_ml4t_backtest.ipynb
04_single_asset_ml4t_backtest.py
05_stateful_strategies.ipynb
05_stateful_strategies.py
06_framework_parity.ipynb
06_framework_parity.py
07_engine_divergence_anatomy.ipynb
07_engine_divergence_anatomy.py
08_signal_method_comparison.ipynb
08_signal_method_comparison.py
09_performance_reporting.ipynb
09_performance_reporting.py
10_regime_backtest_analysis.ipynb
10_regime_backtest_analysis.py
11_sharpe_ratio_inference.ipynb
11_sharpe_ratio_inference.py
12_dsr_validation.ipynb
12_dsr_validation.py
13_ras_protocol.ipynb
13_ras_pr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 35 match(es) in 35 file(s)

/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/08_causal_sanity_checks.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/06_ic_inference.py

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py

/home/georg/projects/ml4t-zh/case_studies/sp500_equity_option_analytics/14_backtest.py

/home/georg/projects/ml4t-zh/case_studies/s
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 60 match(es) in 22 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py
  55: from ml4t.diagnostic.splitters import CombinatorialCV, WalkForwardCV
  56: from ml4t.diagnostic.splitters.config import WalkForwardConfig

/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py
  74: from ml4t.backtest.types import Order, OrderSide, OrderStatus, OrderType, Position
  75: from ml4t.live import LiveRiskConfig, RiskLimitError, SafeBroker, VirtualPortfolio
  76: from ml4t.live.protocols import ExecutionCapability

/home/georg/projects/ml4t-zh/26_mlops_governance/01_drift_monitoring.py
  59: from ml4t.diagnostic.validation import DataFrameValidator

/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:19:50Z

- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 3 -name \"*.pth\" -o -maxdepth 3 -type d -name \"site-packages\" 2>/dev/null; echo \"---venv---\"; ls -d /home/georg/projects/ml4t-zh/.venv /home/georg/projects/ml4t-zh/venv 2>/dev/null; echo \"---pyproject deps---\"; grep -n -i \"ml4t\" /home/georg/projects/ml4t-zh/pyproject.toml"})`
- **tool**: `bash({"command": "grep -rhoE \"from ml4t[\\.a-zA-Z_0-9]* import \\([^)]*\\)|from ml4t[\\.a-zA-Z_0-9]* import [^(\\n]+\" /home/georg/projects/ml4t-zh --include=*.py 2>/dev/null | tr '\\n' ' ' | sed 's/from /\\nfrom /g' | sort -u | head -100"})`
- **tool**: `grep({"pattern": "from ml4t|import ml4t", "path": "/home/georg/projects/ml4t-zh/16_strategy_simulation", "output_mode": "content", "head_limit": 80})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py"})`


> [reasoning] The ml4t package is not installed in this python3. But the notebooks import it. Maybe it's in a venv via uv. Let me check the pyproject and .venv. Also the grep output was truncated. Let me get the full list of ml4t imports, and find site-packages.

Let me search for the library source. Maybe it's installed in a uv venv under the project.
The `ml4t` package isn't in the base python. Let me find the venv/install and extract the full import surface, plus read the key overfitting files.

  <details><summary>tool output</summary>

  ```text
---venv---
---pyproject deps---
2:name = "ml4t"
35:    # `envs/ml4t/Dockerfile` installs Chrome for Testing so the image does resolve one.
54:    # ML4T Libraries (PyPI)
56:    # ml4t-data 0.1.2: HiveStorage.partitions() reports what a write committed, the anomaly
59:    "ml4t-data>=0.1.2",
60:    # ml4t-diagnostic 0.1.2: cross_sectional_ic_series() reports an undefined date
63:    "ml4t-diagnostic>=0.1.4",
64:    "ml4t-engineer>=0.1.3",
65:    "ml4t-backtest>=0.1.3",
66:    "ml4t-live>=0.1.0",
195:    "ml4t-models>=0.1.2",


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
zsh:1: no matches found: --include=*.py


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 68 match(es) in 33 file(s)

/home/georg/projects/ml4t-zh/16_strategy_simulation/02_futures_backtesting.py
  68: from ml4t.backtest import (
  78: from ml4t.backtest.config import CommissionType, SlippageType

/home/georg/projects/ml4t-zh/16_strategy_simulation/18_vectorbt_engine_parity.ipynb
  429: "notes": "Regenerated from ml4t/backtest merge 0c3de46b1881ce6cb9fd72b672a1dba38ebc383b",

/home/georg/projects/ml4t-zh/16_strategy_simulation/06_framework_parity.py
  79: from ml4t.backtest import (
  86: from ml4t.diagnostic.evaluation import PortfolioAnalysis

/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py
  83: from ml4t.diagnostic.evaluation.stats import (
  86: from ml4t.diagnostic.evaluation.stats import (

/home/georg/projects/ml4t-zh/16_strategy_s
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Correcting a Sharpe ratio for the search that found it
18: #
19: # **Docker image**: `ml4t`
20: #
21: # **Book Reference**: Chapter 16, §16.7 - strategy-level overfitting control.
22: #
23: # This notebook demonstrates comprehensive **backtest validation using the Deflated Sharpe Ratio (D
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:19:52Z

- **tool**: `bash({"command": "find /home/georg/.cache/uv /home/georg/.local /home/georg/.venv /opt -maxdepth 12 -type d \\( -name \"diagnostic\" -path \"*ml4t*\" -o -name \"backtest\" -path \"*ml4t*\" \\) 2>/dev/null | head -20; echo \"---site dirs---\"; find /home/georg -maxdepth 8 -type d -name \"ml4t_diagnostic*\" 2>/dev/null | head; find /home/georg/.cache/uv -maxdepth 3 -type d -name \"archive-v0\" 2>/dev/null | head", "timeout": 60000})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/_library_validation.py"})`


> [reasoning] The libraries are PyPI-installed dependencies, not vendored. The base python doesn't have them, but they're declared in pyproject. Let me check if uv has a cached install somewhere, and find the library source to document the public API. Let me search the filesystem for `ml4t_diagnostic` but with a bounded find. Also check uv cache. Let me look at the other key files: 13_ras_protocol.py, 11_sharpe_ratio_inference.py, validation/, 20_strategy_synthesis scripts, and grep for white_reality_check.

Let me search for the library source in the uv cache and site-packages. And read the relevant files.

I should parallelize:
1. Find ml4t library source: `find /home/georg/.cache/uv /home/georg/.venv /root -maxdepth ...` but bounded. Let me use python to check uv cache, and locate via `find / -name "stats.py" -path "*diagnostic*"`.
2. Read 13_ras_protocol.py.
3. Read 11_sharpe_ratio_inference.py.
4. Read validation/_library_validation.py, validation/adapters/ml4t_adapter.py, validation/result.py, weights.py, __init__.py.

Let me do that.
Libraries are PyPI deps (`ml4t-diagnostic>=0.1.4`, `ml4t-backtest>=0.1.3`), not vendored. Let me locate their installed source and read the remaining overfitting/validation files in parallel.

  <details><summary>tool output</summary>

  ```text
---site dirs---
/home/georg/.cache/uv/archive-v0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Charging a strategy for the class it was chosen from
18: #
19: # **Docker image**: `ml4t`
20: #
21: # **Book Reference**: Chapter 16, §16.7 - strategy-level overfitting control.
22: #
23: # This notebook demonstrates the Rademacher Anti-Serum (RAS) protocol for
24: # backtest overfitting de
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # How much do you actually know from a Sharpe ratio?
18: #
19: # **Docker image**: `ml4t`
20: #
21: # ## Purpose
22: # A Sharpe ratio is an estimate computed from a sample, and like any estimate it has a distribution
23: # around the quantity it is estimating. That distribution is much wider th
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/_library_validation.py</path>
<type>file</type>
<content>
1: """Load internal validation helpers from the sibling ml4t-backtest repository."""
2:
3: from __future__ import annotations
4:
5: import importlib
6: import importlib.util
7: from functools import cache
8: from pathlib import Path
9:
10: from ml4t.backtest import __file__ as ml4t_backtest_init
11:
12:
13: def resolve_backtest_repo() -> Path:
14:     """Resolve the sibling ml4t-backtest repository root."""
15:     package_path = Path(ml4t_backtest_init).resolve()
16:     for parent in package_path.parents:
17:         if (parent / "validation" / "benchmark_suite.py").exists():
18:             return parent
19:     fallback = Path.home() / "ml4t" / "libraries"
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:19:58Z

- **tool**: `bash({"command": "ls /home/georg/.cache/uv/archive-v0 | head; echo \"---\"; find /home/georg/.cache/uv/archive-v0 -maxdepth 4 -type d -name \"ml4t\" 2>/dev/null | head; echo \"---home ml4t---\"; ls -d /home/georg/ml4t/libraries/* 2>/dev/null; echo \"---pip list uv---\"; find /home/georg/.cache/uv -maxdepth 2 -name \"*.dist-info\" -type d 2>/dev/null | grep -i ml4t | head", "timeout": 60000})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/__init__.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/result.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/weights.py"})`


> [reasoning] Now I have a lot. Let me find the library source in uv cache. The uv cache has archive-v0. Let me search there. Also check if there's a `~/ml4t/libraries` source.

Let me search the uv cache for the diagnostic package, and also read the 20_strategy_synthesis files and 16 validation adapters.

Let me do bounded searches.
Now let me locate the installed library source in the uv cache and read the strategy synthesis + validation adapter files.

  <details><summary>tool output</summary>

  ```text
--9zzPK_NOVUEsld
-wEiAA2-SXss8spa
06Y7X6EtG0SyIcvf
0lJRZCNWLm0G20y7
0m-TarcyW7yoYkUm
10FA1WAz2s5hLSuK
15YrX4RVtbYej8zX
1B--9ncs0QbS0pvi
1qR0x9KN4kDbKt-E
2H0RKdLEI8CBOnkA
---
---home ml4t---
zsh:1: no matches found: /home/georg/ml4t/libraries/*
---pip list uv---


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/__init__.py</path>
<type>file</type>
<content>
1: """Chapter 16 validation helpers for engine-parity notebooks."""

(End of file - total 1 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/result.py</path>
<type>file</type>
<content>
1: """Standardized backtest result format shared by all framework adapters."""
2:
3: from dataclasses import dataclass, field
4:
5: import pandas as pd
6:
7:
8: @dataclass
9: class BacktestResult:
10:     """Standardized result from any backtesting framework."""
11:
12:     framework: str
13:     equity_curve: pd.Series  # DatetimeIndex -> portfolio value
14:     trades: pd.DataFrame  # (timestamp, asset, side, quantity, price, commission)
15:     positions: pd.DataFrame  # (timestamp, asset, quantity, value) or empty
16:     metrics: dict = field(default_factory=dict)
17:
18:     @property
19:     def final_value(self) -> float:
20:         return float(self.equity_curve
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/weights.py</path>
<type>file</type>
<content>
1: """Shared signal-to-weight conversion for Chapter 16 validation.
2:
3: Converts ML prediction artifacts into a target-weight time series that all
4: three frameworks (ml4t-backtest, VectorBT, Backtrader) consume identically.
5:
6: This eliminates signal-generation differences and isolates execution-engine parity.
7: """
8:
9: import sqlite3
10: from pathlib import Path
11:
12: import numpy as np
13: import pandas as pd
14: import polars as pl
15:
16: from utils import ML4T_DATA_PATH
17: from utils.paths import get_case_study_dir
18:
19: REPO_ROOT = Path(__file__).resolve().parent.parent.parent
20:
21: COST_BPS: dict[str, float] = {
22:     "etfs": 10,
23:     "crypto
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:01Z

- **tool**: `bash({"command": "find /home/georg -maxdepth 6 -type d \\( -name \"ml4t-diagnostic\" -o -name \"ml4t-backtest\" -o -name \"ml4t_diagnostic\" \\) 2>/dev/null; echo \"---proj siblings---\"; ls /home/georg/projects; echo \"---uv grep---\"; grep -rl \"deflated_sharpe_ratio\" /home/georg/.cache/uv 2>/dev/null | head -20", "timeout": 90000})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/03_signal_quality.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/06_cost_survival.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py"})`


> [reasoning] The uv cache doesn't contain ml4t currently (maybe not synced). Let me search more specifically across the whole home for the diagnostic package. Earlier find timed out on `/`. Let me do targeted find in uv archive-v0 for a file like `stats.py` under a `ml4t` path. Use find with maxdepth higher but only archive-v0.

Actually, the archive-v0 contains extracted packages but the structure may be `<hash>/<pkg>`. Let me grep for "deflated_sharpe_ratio" in the uv cache directly. That's the fastest.

Also search for any local clone of ml4t-backtest / ml4t-diagnostic. Let me search /home/georg broadly with find limited.

Let me run:
- `find /home/georg/.cache/uv/archive-v0 -maxdepth 5 -type d -name "diagnostic" 2>/dev/null`
- grep -rl "def shaspe..." Actually grep for `deflated_sharpe_ratio` in /home/georg/.cache/uv with include *.py, but that might be huge. Use `rg` maybe installed. Let's just use grep tool with path.

Also check `~/.cache/uv` indexes.

Let me also look at other repo locations: maybe `/home/georg/projects/ml4t-libraries` etc.

Let me run parallel:
1. find ml4t dirs under /home/georg (bounded depth 6)
2. grep deflated_sharpe_ratio across /home/georg/.cache/uv (files_with_matches)
3. read 20_strategy_synthesis/03_signal_quality.py, 02_feature_evaluation.py, 06_cost_survival.py, holdout.py
4. read 20_strategy_synthesis/01_aggregate_synthesis.py, 04_signal_to_strategy.py

Let me batch. But note read tool only one file per call. I'll issue multiple read calls in parallel.

Given the volume, I'll prioritize. Let me first do the library search and read the 20 files.

  <details><summary>tool output</summary>

  ```text
---proj siblings---
MarketGameSim
alphamill
ml4t-zh
personahub
quant-crypto
skills-manager-backup
zcode-cli
---uv grep---


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/03_signal_quality.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.18.1
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Signal Evidence: Is the Chosen Signal Trustworthy?
18: #
19: # **Docker image**: `ml4t`
20: #
21: # This is NOT a full recap of Ch11-15's model family narrative. It shows
22: # **only** the signal evidence that matters for downstream trading decisions:
23: # validation IC, holdout IC, stab
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/06_cost_survival.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Friction Survival: Where the Edge Dies
18: #
19: # **Docker image**: `ml4t`
20: #
21: # This notebook cross-cuts the case studies by **failure mode**: gross-to-net
22: # Sharpe degradation, breakeven cost thresholds, cadence-frequency vulnerability,
23: # and cost-model realism caveats. Ch1
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py</path>
<type>file</type>
<content>
1: """Holdout prediction and backtest generation for case studies.
2:
3: Provides the core logic for out-of-sample validation: select the best
4: model from the validation registry, retrain on all pre-holdout data,
5: generate predictions on the holdout window, and backtest.
6:
7: Usage::
8:
9:     from holdout import generate_holdout
10:
11:     result = generate_holdout("etfs")
12:     print(f"Holdout Sharpe: {result['holdout_sharpe']:.3f}")
13: """
14:
15: from __future__ import annotations
16:
17: import contextlib
18: import gc
19: import json
20: import shutil
21: import sqlite3
22: import time
23: from datetime import date as dt_date
24: from datetime import timedelta
25: fro
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:07Z

- **tool**: `grep({"pattern": "white_reality_check|reality_check|deflated_sharpe|rademacher|ras_sharpe|compute_pbo|compute_min_trl|reality|whites|spa_test|stepwise", "path": "/home/georg/projects/ml4t-zh", "output_mode": "files_with_matches", "include": "*.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/cohort_metrics.py"})`


> [reasoning] The libraries aren't in the local environment at all. The notebooks expect them installed via uv. Let me check if there's a vendored copy anywhere in the repo, or if the .omo/.workspace has something. Also search case_studies/utils/uncertainty.py which computes DSR/RAS/Reality Check per the grep. That's likely the key production implementation call site.

Let me read:
- case_studies/utils/uncertainty.py
- case_studies/utils/cohort_metrics.py
- case_studies/utils/strategy_analysis.py (may reference)
- scripts/backfill_cohort_metrics.py
- 16_strategy_simulation/validation/adapters/ml4t_adapter.py

And grep for white_reality_check / reality_check usage across repo.

Also read 20_strategy_synthesis/04_signal_to_strategy.py (Fundamental Law, cascade, IC-Sharpe decorrelation), 02_feature_evaluation.py (FDR), 05_portfolio_allocation.py, 07_regime_risk.py.

And 17, 18, 19 key files. This is a lot. Let me be strategic and gather the most important with grep for symbols then read specific.

Let me start with the production uncertainty machinery and grep for the statistical function names.
The ml4t packages aren't installed locally (uv dependency, source not in cache). The key production call sites are in `case_studies/utils/`. Let me extract those and search for Reality Check / FDR usage.

  <details><summary>tool output</summary>

  ```text
Found 40 match(es) in 40 file(s)

/home/georg/projects/ml4t-zh/05_synthetic_data/03_sigcwgan_signatures.py

/home/georg/projects/ml4t-zh/10_text_feature_engineering/01_word2vec_training.py

/home/georg/projects/ml4t-zh/10_text_feature_engineering/07_news_return_signals.py

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py

/home/georg/projects/ml4t-zh/08_financial_features/06_robustness_sensitivity.py

/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py

/home/georg/projects/ml4t-zh/sitecustomize.py

/home/georg/projects/ml4t-zh/22_rag_financial_research/04_ragas_evaluation.py

/home/ge
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py</path>
<type>file</type>
<content>
1: """Backtest performance uncertainty: block bootstrap, HAC SE, PSR/DSR, paired comparisons.
2:
3: Operates on the daily out-of-sample strategy return series persisted at
4: ``run_log/backtest/{hash}/daily_returns.parquet``. Series-level CIs are computed
5: via stationary block bootstrap; Sharpe SE uses the López de Prado (2025) closed
6: form with autocorrelation, skew, and kurtosis corrections; mean-return SE uses
7: Newey-West HAC. Selection bias across K variants uses the library's
8: :func:`deflated_sharpe_ratio`. Challenger-vs-baseline uncertainty uses paired
9: stationary block bootstrap on daily-return differences.
10:
11: All bootstraps share a single seed so the same call is
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/cohort_metrics.py</path>
<type>file</type>
<content>
1: """Compute-and-register the per-case-study ``cohort_metrics`` selection-bias table.
2:
3: This is the in-repo home of the cohort selection-bias producer that the
4: strategy-analysis notebook (``NN_strategy_analysis.py``) runs so a reader who
5: never touches Chapter 20 still lands a populated ``cohort_metrics`` table. It
6: was migrated verbatim from ``agents/scripts/backfill_cohort_metrics.py`` (the
7: post-engine-rerun backfill); the only change is that the per-cohort write goes
8: through :func:`case_studies.utils.registry.register_cohort_metrics` instead of
9: an inline upsert.
10:
11: For each case study the table carries, per cohort:
12:
13: * Raw-K, MP-K, ER-K DSR (with
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:12Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py", "offset": 1268, "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/04_signal_to_strategy.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py"})`


> [reasoning] Excellent, this is the core. Now I need:
- remainder of uncertainty.py (PBO computation lines 1268+)
- 20_strategy_synthesis/04_signal_to_strategy.py (Fundamental Law, IC-Sharpe decorrelation, cascade)
- 20_strategy_synthesis/02_feature_evaluation.py (FDR)
- 17_portfolio_construction (HRP, Kelly, MV, conformal, allocator comparison)
- 18_transaction_costs
- 19_risk_management
- ml4t adapter for backtest engine

Let me read the rest of uncertainty.py, plus 04_signal_to_strategy.py, 07_multiple_testing.py, and 20/02_feature_evaluation.py. Also grep 17,18,19 for key symbols.

I'll batch reads.
Now the remaining uncertainty.py PBO block plus the Fundamental Law / FDR notebooks and the adapter.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py</path>
<type>file</type>
<content>
1268:     out["pbo_n_combinations"] = None
1269:     out["pbo_median_oos_rank"] = None
1270:     out["pbo_mean_degradation"] = None
1271:     out["pbo_n_folds"] = None
1272:     if fold_returns_by_hash is not None:
1273:         try:
1274:             from ml4t.diagnostic.evaluation.stats import compute_pbo
1275:
1276:             fold_names = [n for n in names if n in fold_returns_by_hash]
1277:             if len(fold_names) >= 2:
1278:                 fold_sharpes = np.array(
1279:                     [fold_returns_by_hash[n] for n in fold_names], dtype=np.float64
1280:                 ).T  # (n_folds, K)
1281:                 n_folds = fold_sharpes.shape[0]
1282:                 if
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/04_signal_to_strategy.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Translation to Strategy: The Central Conversion Story
18: #
19: # **Docker image**: `ml4t`
20: #
21: # The IC-to-Sharpe gap is the central narrative of Ch16-20. Ch16 introduced
22: # the concept with individual examples; this notebook shows the **full 9-CS
23: # picture including holdo
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown] tags=[]
17: # # Multiple Testing and Selection Bias
18: #
19: # **Docker image**: `ml4t`
20: #
21: # **Chapter 7: Defining the Learning Task**
22: # **Section Reference**: 7.4 - Search Accounting and Multiple Testing
23: #
24: # ## Purpose
25: #
26: # This notebook addresses the **factor
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:15Z

- **tool**: `grep({"pattern": "^(def|class) ", "path": "/home/georg/projects/ml4t-zh/17_portfolio_construction", "output_mode": "content", "include": "*.py", "head_limit": 120})`
- **tool**: `grep({"pattern": "^(def|class) ", "path": "/home/georg/projects/ml4t-zh/18_transaction_costs", "output_mode": "content", "include": "*.py", "head_limit": 120})`
- **tool**: `grep({"pattern": "^(def|class) ", "path": "/home/georg/projects/ml4t-zh/19_risk_management", "output_mode": "content", "include": "*.py", "head_limit": 120})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/adapters/ml4t_adapter.py"})`


> [reasoning] Now I need the 20_strategy_synthesis/02_feature_evaluation.py (FDR-controlled feature triage), 05_portfolio_allocation.py (allocator comparison), 07_regime_risk.py (decay), and 17/18/19 key notebooks. Also the ml4t_adapter.py and validation adapters. And the 16 backtest_first_principles/trading protocol.

Given time, I should gather remaining key symbols via grep and read targeted sections. Let me grep for key function/class definitions across chapters 17,18,19,20 and read the important ones. Also read ml4t_adapter.py and the validation adapters list.

Let me do parallel:
1. Read 20/02_feature_evaluation.py
2. Read 17/06_hierarchical_risk_parity.py and 17/04_kelly_criterion.py? These are long. Maybe grep for def in 17,18,19 to get symbol inventory.
3. Read 16/validation/adapters/ml4t_adapter.py
4. Read 18/03_market_impact_calibration.py and 18/05_almgren_chriss_optimal_execution.py

Let me first grep function/class definitions in chapters 17-19 to build an inventory, and read feature_evaluation and the ml4t adapter.

Let me be efficient with grep `^def |^class ` across directories with content mode.
Now let me build symbol inventories for ch17-19 and read the FDR feature triage + adapter.

  <details><summary>tool output</summary>

  ```text
Found 120 match(es) in 17 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/17_portfolio_construction/01_portfolio_metrics.py
  439: def compute_drawdown_series(returns: pd.Series) -> pd.Series:
  808: def analyze_period(returns: pd.Series, benchmark: pd.Series, start: str, end: str):
  939: def add_metric(category: str, name: str, value: str) -> None:

/home/georg/projects/ml4t-zh/17_portfolio_construction/deepm/configs.py
  11: class FeatureConfig:
  42: class ModelConfig:
  68: class TrainingConfig:
  103: def validate_training_config(cfg: TrainingConfig) -> None:
  115: def as_tuple(values: Iterable[int]) -> tuple[int, ...]:

/home/georg/projects/ml4t-zh/17_portfolio_construction/deepm/inference.py
  16: def infer_risk_weights_rolling(

/home/georg/projects/ml4
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 102 match(es) in 13 file(s)

/home/georg/projects/ml4t-zh/18_transaction_costs/12_commission_slippage_comparison.py
  373: def asset_class_cost_row(asset_class: str, cfg: dict) -> dict:
  561: def make_weight_dict(step: int) -> dict:
  590: class SimpleStrategy(Strategy):
  641: def run_backtest_variant(weight_dict: dict, commission_model, config: BacktestConfig) -> dict:

/home/georg/projects/ml4t-zh/18_transaction_costs/06_ml4t_execution_demo.py
  691: def compose_limit_and_impact(

/home/georg/projects/ml4t-zh/18_transaction_costs/09_frequency_tradeoff.py
  92: class CostAssumptions:
  174: def momentum_frequency_backtest(
  219: def annualized_sharpe(returns: np.ndarray) -> float:
  303: def calculate_break_even_alpha(annual_turnover: float, round_trip_cost_bps: float) -> float:

…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 120 match(es) in 10 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/19_risk_management/02_exit_strategies.py
  199: def build_exit_result(
  228: def long_barrier_fill(
  263: def summarize_trades(results: list[dict]) -> dict:
  287: class FixedExitConfig:
  301: def simulate_fixed_exits(
  473: class TrailingStopConfig:
  480: def trailing_stop_fill(open_price: float, low_price: float, stop_price: float) -> float | None:
  496: def simulate_trailing_stops(
  589: class ATRStopConfig:
  601: def simulate_atr_exits(
  873: def ml_exit_triggered(
  889: def simulate_ml_exits(
  1013: class HybridExitConfig:
  1034: def hybrid_bar_fill(
  1063: def simulate_one_hybrid_exit(
  1110: def simulate_hybrid_exits(
  1367: def create_position_state(
  1402: def shoul
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/adapters/ml4t_adapter.py</path>
<type>file</type>
<content>
1: """ml4t-backtest adapter for backtesting validation.
2:
3: Takes pre-computed target weights and runs them through ml4t-backtest's Engine
4: with TargetWeightExecutor, returning a standardized BacktestResult.
5:
6: Supports multiple modes to match different framework behaviors:
7: - "backtrader": Integer shares, next-bar open fills, commission headroom (matches BT exactly)
8: - "vectorbt": Fractional shares, same-bar close fills (matches VBT)
9: - "lean": Verified LEAN execution/account semantics with case-study cost assumptions
10: - "default": Library defaults (next-bar open, fractional shares)
11: """
12:
13: import math
14: from datetime import datetime
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:20Z

- **tool**: `bash({"command": "grep -rhoE \"from ml4t\\.diagnostic[a-zA-Z_.]* import\" /home/georg/projects/ml4t-zh --include='*.py' 2>/dev/null | sort | uniq -c | sort -rn; echo \"=== FUNCS imported ===\"; grep -rhA40 \"from ml4t.diagnostic.evaluation.stats import\" /home/georg/projects/ml4t-zh --include='*.py' 2>/dev/null | grep -oE \"^\\s+[a-zA-Z_][a-zA-Z_0-9]*\" | tr -d ' ' | sort -u"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/02_feature_evaluation.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/07_regime_risk.py", "limit": 430})`


> [reasoning] I have a lot. Now I need a few more specifics:
- 16/01_backtest_first_principles.py: trading protocol spec, falsification
- 20/02_feature_evaluation.py: FDR-controlled feature triage
- 20/05_portfolio_allocation.py: allocator comparison
- 20/07_regime_risk.py: decay mechanisms
- 17/07_conformal_position_sizing.py: conformal position sizing
- 18/05_almgren_chriss, 18/09 frequency tradeoff, _cost_analysis functions
- 19/01_var_cvar, 19/06_stress_testing
- 17/09_allocator_comparison functions (already have)
- also the libraries: find whether any vendored. We know not. But is there a docs or tests referencing public API? The question asks whether vendored/installed here and what public API notebooks call. I have enough: they're PyPI deps declared in pyproject, not vendored, not installed in base env; notebooks import `ml4t.diagnostic.evaluation.stats` with specific functions. Let me gather the exact public API list by grepping imports from ml4t.diagnostic.evaluation.stats.

Let me grep all imports from ml4t.diagnostic and ml4t.backtest fully.

Also check tests/test_uncertainty_cscv.py to understand expected library behaviors and test_family_comparison_scope. Maybe not needed.

Let me get:
1. Full import list from ml4t.diagnostic.
2. Read 20/02_feature_evaluation.py.
3. Read 20/07_regime_risk.py.
4. Read 17/07_conformal_position_sizing.py.

Let me batch these.
Now the FDR triage, regime decay, conformal sizing, and the complete ml4t-diagnostic public API surface.

  <details><summary>tool output</summary>

  ```text
90 from ml4t.diagnostic.metrics import
     39 from ml4t.diagnostic.evaluation.stats import
     20 from ml4t.diagnostic.evaluation import
     14 from ml4t.diagnostic.splitters.calendar import
      6 from ml4t.diagnostic.splitters import
      5 from ml4t.diagnostic.signal import
      5 from ml4t.diagnostic.integration import
      5 from ml4t.diagnostic.evaluation.autocorrelation import
      4 from ml4t.diagnostic.visualization import
      4 from ml4t.diagnostic.metrics.uncertainty import
      4 from ml4t.diagnostic.evaluation.stationarity import
      3 from ml4t.diagnostic.splitters.config import
      3 from ml4t.diagnostic.evaluation.volatility import
      3 from ml4t.diagnostic.config import
      2 from ml4t.diagnostic.evaluation.excursion import
      2 from ml4t.diagnostic.
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/02_feature_evaluation.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Feature Evaluation Across Case Studies
18: #
19: # **Docker image**: `ml4t`
20: #
21: # Each case study runs an FDR-controlled triage pass on its candidate
22: # feature menu (Ch8 §8.5), classifying every feature as PROCEED, REVISE,
23: # or STOP. This notebook reads those nine ledgers
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/20_strategy_synthesis/07_regime_risk.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Risk Overlays and Stability Across Regimes
18: #
19: # **Docker image**: `ml4t`
20: #
21: # Ch19 catalogues the risk-overlay machinery (stop-loss, trailing stop,
22: # daily loss limit, drawdown breaker, time exit, vol target). This notebook
23: # reads each case study's overlay backtests dir
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:24Z

- **tool**: `grep({"pattern": "cascade|decorrelat|fundamental law|Fundamental Law|breadth|transfer coefficient|information coefficient", "path": "/home/georg/projects/ml4t-zh/20_strategy_synthesis", "output_mode": "content", "include": "*.py", "head_limit": 60})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/17_portfolio_construction/07_conformal_position_sizing.py", "limit": 140})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/19_risk_management/01_var_cvar.py", "limit": 120})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/18_transaction_costs/_cost_analysis.py"})`


> [reasoning] I have a comprehensive picture. Now I need a few more specifics:

- 16/01_backtest_first_principles.py: trading protocol spec / falsification framing. Read the markdown top.
- 17/07_conformal_position_sizing.py: conformal sizing mechanism.
- 18/05_almgren_chriss key params; 18/_cost_analysis functions (spread estimators).
- 19/01_var_cvar key functions and 19/06 stress testing / kill switches. Also 19/05 trade_shap and 19/07 drift.
- The "model-family cascade" in 20 — likely in 04_signal_to_strategy but I didn't see an explicit cascade. README says "Family cascade table (Table 20.5)". Maybe the cascade is in 01_aggregate_synthesis (pipeline stage survival). Let me grep for "cascade" in 20.
- "IC-Sharpe decorrelation" in 20 — grep for decorrelation/correlation.
- "holdout failure modes" — 00_holdout_predictions + holdout.py (degeneracy). Have that.

Let me grep for "cascade" and "decorrelat" and "Fundamental Law" across 20.

Also read 20/05_portfolio_allocation.py maybe.

Also question 6 asks: are ml4t-diagnostic / ml4t-backtest vendored/installed? Answer: declared as PyPI deps, not vendored, not installed in the current base python (only in the docker/uv env). I should confirm there's no vendored copy in the repo. I searched and found none.

Let me run targeted greps.

  <details><summary>tool output</summary>

  ```text
Found 24 match(es) in 5 file(s)

/home/georg/projects/ml4t-zh/20_strategy_synthesis/03_signal_quality.py
  101: # Each cell is the mean information coefficient over every prediction that family
  162: "Heatmap of mean information coefficient with case studies as rows and model "

/home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py
  1121: # for the Ch18 htm_cost_cascade comparison only and must never be selected as the

/home/georg/projects/ml4t-zh/20_strategy_synthesis/08_recommendations.py
  26: # NB00–NB05; the HTM cost-cascade figures (which reproduce
  330: "detail": "HTM cost cascade max Sharpe = -0.28 at 20% half-spread fraction; net Sharpe negative across the full cascade (-0.47 at 50%, -0.72 at 100%)",
  630: #   liquid-universe construction, but the cost cascade turns i
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/17_portfolio_construction/07_conformal_position_sizing.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Conformal Prediction Position Sizing: Two Case Studies
18: #
19: # **Docker image**: `ml4t`
20: #
21: # This notebook builds uncertainty-based position sizing on top of registered
22: # walk-forward validation predictions for ETFs (`fwd_ret_21d`) and CME futures
23: # (`fwd_
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/19_risk_management/01_var_cvar.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Value at Risk and Conditional Value at Risk
18: # **Docker image**: `ml4t`
19: #
20: # ## Purpose
21: # **Value at Risk** answers one question: over the next day, how much could a position lose if the
22: # day turns out badly but not catastrophically? Pick a confidence level - say the worst one da
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/18_transaction_costs/_cost_analysis.py</path>
<type>file</type>
<content>
1: """Shared transaction cost analysis for Ch18 notebooks and case study costs.py.
2:
3: Provides:
4: - corwin_schultz_spread(): High-low spread estimator (Corwin & Schultz 2012)
5: - roll_spread(): Serial covariance spread estimator (Roll 1984)
6: - compute_adv(): Rolling average daily volume
7: - compute_adv_usd(): Rolling average daily dollar volume
8: - calibrate_sqrt_impact(): Fit η in Impact = σ·η·√(Q/V)
9: - estimate_kyle_lambda(): Linear price-impact coefficient ΔP = λQ
10: - estimate_capacity(): Max AUM given impact coefficient and alpha
11: - breakeven_alpha(): Required gross alpha given turnover and costs
12: - get_fee_schedule(): Codified exchange fee schedules
13:
14:
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:28Z

- **tool**: `grep({"pattern": "corr|decorrel|spearman.*sharpe|sharpe.*ic", "path": "/home/georg/projects/ml4t-zh/20_strategy_synthesis/05_portfolio_allocation.py", "output_mode": "content", "head_limit": 30})`
- **tool**: `bash({"command": "grep -rhoE \"from ml4t\\.backtest\\.(risk|execution|models)[a-zA-Z_.]* import \\(?[^)]*\" /home/georg/projects/ml4t-zh --include='*.py' 2>/dev/null | head -40; echo \"=== risk rules grep ===\"; grep -rhoE \"(StopLoss|TakeProfit|TrailingStop|DrawdownBreaker|DailyLossLimit|KillSwitch|MaxDrawdown|VolTarget|VolumeParticipationLimit|SqrtImpact|LinearImpact|SquareRootImpact|PowerImpact)[A-Za-z]*\" /home/georg/projects/ml4t-zh/19_risk_management/10_ml4t_backtest_risk_demo.py /home/georg/pr
…[truncated])`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/16_strategy_simulation/01_backtest_first_principles.py", "limit": 120})`
- **tool**: `bash({"command": "grep -nE \"ALLOCATOR|allocator|hrp|kelly|inverse_vol|mvo|risk_parity|equal_weight|conformal\" /home/georg/projects/ml4t-zh/20_strategy_synthesis/05_portfolio_allocation.py | head -50"})`


> [reasoning] I have enough to answer thoroughly. But I should verify a couple of specific items:
- The "model-family cascade" in 20. The README says Table 20.5 "Family cascade". Maybe in 04_signal_to_strategy it's the leader_df. Actually the "cascade" might be in 01_aggregate_synthesis. Let me grep for "cascade" only showed cost cascade. So "model-family cascade" may refer to the pipeline stage survival. I'll note the actual content: family rankings across pipeline stages in 04 and 03. I shouldn't overstate. Let me quickly check 05_portfolio_allocation for allocator comparison details and 01_aggregate_synthesis for stage cascade. Actually the downstream wants accurate; I can describe what code does.

- "IC-Sharpe decorrelation" — maybe in 03_signal_quality (IC vs Sharpe heatmaps) or 04. I didn't find explicit decorrelation. There's `01_aggregate_synthesis` maybe computing correlation between IC and Sharpe. Let me grep for "corr" in 20. Not crucial but the user asked. Let me quickly grep.

- Also 19 kill switches: 10_ml4t_backtest_risk_demo uses ml4t.backtest.risk rules. Let me grep for risk module imports to list rule classes.

- 16/01_backtest_first_principles: trading protocol. Let me read the head.

Let me run a final batch:
1. grep "corr" in 20 dir.
2. grep risk rules/imports for ml4t.backtest.risk and ml4t.backtest.execution.impact.
3. read 16/01_backtest_first_principles.py first 120 lines.
4. read 20/05_portfolio_allocation.py first 120 lines + maybe allocator list.

Let me also grep for "kill" across repo.

Batch.
Final pass: IC-Sharpe decorrelation, allocator list, risk-rule/kill-switch APIs, and the backtest protocol spec.

  <details><summary>tool output</summary>

  ```text
Found 1 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/20_strategy_synthesis/05_portfolio_allocation.py
  628: # on `ew_sharpe` rather than reporting that nothing qualified - which is what happened as soon
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
from ml4t.backtest.execution.impact import NoImpact, SquareRootImpact
from ml4t.backtest.execution import (
from ml4t.backtest.execution.impact import (
from ml4t.backtest.execution.limits import VolumeParticipationLimit
from ml4t.backtest.execution.result import ExecutionResult
from ml4t.backtest.execution.rebalancer import RebalanceConfig, TargetWeightExecutor
from ml4t.backtest.models import (
from ml4t.backtest.risk import (
from ml4t.backtest.execution.rebalancer import RebalanceConfig, TargetWeightExecutor
from ml4t.backtest.risk.position import RuleChain, StopLoss, TakeProfit, TrailingStop
from ml4t.backtest.risk import RuleChain, StopLoss, TakeProfit, TimeExit
from ml4t.backtest.execution.rebalancer import RebalanceConfig, TargetWeightExecutor
from ml4t.backtest.execution.rebalance
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/16_strategy_simulation/01_backtest_first_principles.py</path>
<type>file</type>
<content>
1: # ---
2: # jupyter:
3: #   jupytext:
4: #     cell_metadata_filter: tags,-all
5: #     text_representation:
6: #       extension: .py
7: #       format_name: percent
8: #       format_version: '1.3'
9: #       jupytext_version: 1.19.3
10: #   kernelspec:
11: #     display_name: Python 3 (ipykernel)
12: #     language: python
13: #     name: python3
14: # ---
15:
16: # %% [markdown]
17: # # Backtesting First Principles: From Returns to Portfolio Simulation
18: #
19: # **Docker image**: `ml4t`
20: #
21: # ## Purpose
22: # Build an auditable portfolio simulator from first principles with Polars and NumPy. The
23: # implementation makes signal timing, next-open execu
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
22:# isolate the allocator layer: the same forecasts are routed through equal
23:# weight, inverse-vol, MVO, risk parity and score-weighted allocators, and the
24:# resulting Sharpe spread says how much room the allocator has to add or subtract
33:# - Compare allocator performance across diverse asset classes and frequencies
35:# - Examine the spread between best and worst allocators per case study
43:"""Ch20 Portfolio Allocation — spine-pinned allocator comparison across 8 case studies.
46:signal carrier fixed per case study, then compare allocators at the allocation
47:stage only, so the best-minus-worst spread measures what the allocator alone
64:    extract_allocator,
132:    print(f"No resolved spine, excluded from the allocator comparison: {NO_SPINE}")
134:# This section isolates the
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:34Z

- **tool**: `bash({"command": "grep -rli \"fundamental law\\|transfer coefficient\\|decorrelat\" /home/georg/projects/ml4t-zh --include='*.py' --include='*.md' 2>/dev/null | head -20; echo \"=== IC corr ===\"; grep -rn \"pearsonr\\|spearmanr\\|corrcoef\\|\\.corr(\" /home/georg/projects/ml4t-zh/20_strategy_synthesis/*.py 2>/dev/null | head -20; echo \"=== aggregate IC sharpe ===\"; grep -n \"ic.*sharpe\\|sharpe.*ic\" /home/georg/projects/ml4t-zh/20_strategy_synthesis/01_aggregate_synthesis.py | head -20"})`


> [reasoning] I now have a comprehensive picture. I have enough to write the structured report. Let me be careful about the fact that ml4t libraries are PyPI deps, not vendored/installed in this environment. The user asked "are they vendored/installed here?" Answer: neither vendored nor installed in the current base python; declared in pyproject as PyPI deps and expected via `uv run`/Docker image `ml4t`. Source not present locally (uv cache doesn't have it downloaded), so I couldn't enumerate the library internals, only the call sites. I should be explicit about this limitation.

Let me also note the specific library public API functions called with signatures based on call sites.

Let me compose the final report. Need:
- analysis block
- structured results with files list (absolute paths)
- answer section covering all 6 areas
- next steps

I should include the key function/class names and what each computes, and explicitly flag not skipping plotting.

Let me organize:

1. Where the libraries live + public API
2. Ch16 overfitting controls (DSR, RAS, PBO, Reality Check) + engines/protocol
3. Ch20 synthesis
4. Ch17
5. Ch18
6. Ch19

Include the production call site `case_studies/utils/uncertainty.py` and `cohort_metrics.py` which is the actual deployed machinery (more important than the notebook demos).

Key facts:

Library location: pyproject lines 59-66 list ml4t-data>=0.1.2, ml4t-diagnostic>=0.1.4, ml4t-engineer>=0.1.3, ml4t-backtest>=0.1.3, ml4t-live>=0.1.0, ml4t-models>=0.1.2. Not vendored; base python3 has no ml4t. `16_strategy_simulation/validation/_library_validation.py` resolves sibling ml4t-backtest repo for internal helpers. Docker image `ml4t`.

Public API from ml4t.diagnostic.evaluation.stats (imported):
- deflated_sharpe_ratio (lib_dsr), deflated_sharpe_ratio_from_statistics, compute_min_trl, min_trl_fwer, compute_pbo, effective_number_of_trials, rademacher_complexity, ras_sharpe_adjustment, ras_ic_adjustment, RASResult, benjamini_hochberg_fdr, holm_bonferroni, multiple_testing_summary, whites_reality_check, compute_sharpe_variance, _optimal_block_size, _stationary_bootstrap_indices, compute_ic_hac_stats (metrics.ic_inference), cross_sectional_ic_series, compute_ic_uncertainty, PortfolioAnalysis, TradeShapAnalyzer.

Production usage in case_studies/utils/uncertainty.py:
- compute_backtest_uncertainty -> block bootstrap, HAC, psr_pvalue via deflated_sharpe_ratio with periods_per_year
- compute_reality_check -> whites_reality_check
- compute_cohort_metrics -> effective_number_of_trials (MP/ER), deflated_sharpe_ratio raw/MP/ER, rademacher_complexity + ras_sharpe_adjustment, compute_pbo via _cscv_split_pairs
- compute_selection_adjustment (deprecated raw-K)
- cohort_metrics.py registers.

Ch16:
- 01_backtest_first_principles.py: self-contained simulator, next-open execution, pre-registered pass/fail, no holdout.
- 12_dsr_validation.py: local deflated_sharpe_ratio + library deflated_sharpe_ratio_from_statistics; compute_pbo with cscv_sharpe_matrices; rademacher_complexity, ras_sharpe_adjustment.
- 13_ras_protocol.py: rademacher_complexity, ras_sharpe_adjustment, ras_ic_adjustment; massart_upper_bound; units discipline.
- 11_sharpe_ratio_inference.py: PSR, MinTRL, Lo 2002, compute_min_trl, lib_dsr.
- 14_cost_sensitivity.py, 07/08/10 engines etc.
- validation/adapters: ml4t_adapter, vectorbt_adapter, lean_adapter; BacktestResult.

Ch20:
- holdout.py: select_best_models, generate_holdout, build_holdout_split, _is_degenerate_predictions, has_holdout_predictions, delete_holdout_predictions; TRAIN_DISPATCH; HOLDOUT_SELECTION_STAGES (excludes cost_sensitivity).
- 01_aggregate_synthesis.py
- 02_feature_evaluation.py: FDR triage, PROCEED via BH or stability.
- 03_signal_quality.py: IC vs signal Sharpe.
- 04_signal_to_strategy.py: IC-Sharpe translation validation vs holdout.
- 05_portfolio_allocation.py: allocators equal_weight, inverse_vol, mvo_ledoit_wolf, risk_parity, hrp, conformal_weighted; best-minus-worst spread, breadth.
- 06_cost_survival.py: _breakeven, _sharpe_at, cost_margin_ratio, resilience classes.
- 07_regime_risk.py: overlay categories, validation-vs-holdout.
- 08_recommendations.py.

Note: "IC-Sharpe decorrelation" and "Fundamental Law" — the notebook 04 does NOT compute a Fundamental Law transfer-coefficient decomposition; I couldn't find "Fundamental Law" string except README. Actually the README of ch20 says "Fundamental Law diagnostic (Figure 20.3)" for 04. But the code I read for 04 doesn't compute it — maybe it was removed/deprecated, or it's in the parquet. I should state honestly: the current 04 computes IC/Sharpe translation and leader agreement, not a Fundamental Law decomposition; no `br`/`TC` symbol found. Let me do a quick grep for "breadth" in case_studies/utils or 20 to be sure. Actually grep earlier showed breadth only in 05. And "Fundamental Law" only in READMEs? Let me quickly grep whole repo for "fundamental law" case-insensitive and "transfer coefficient". This matters for accuracy.

Also "IC-Sharpe decorrelation" — maybe in 01_aggregate_synthesis or measurement_quality. Let me grep quickly.

Let me run one final grep.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/12_gradient_boosting/chapter_12.md
/home/georg/projects/ml4t-zh/ml4t_bilingual.md
/home/georg/projects/ml4t-zh/README.md
/home/georg/projects/ml4t-zh/20_strategy_synthesis/README.md
/home/georg/projects/ml4t-zh/20_strategy_synthesis/chapter_20.md
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py
/home/georg/projects/ml4t-zh/08_financial_features/chapter_08.md
/home/georg/projects/ml4t-zh/08_financial_features/README.md
/home/georg/projects/ml4t-zh/08_financial_features/case_study_feature_summary.py
/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/README.md
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/02_labels.py
/home/georg/projects/ml4t-z
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:44Z

- **tool**: `bash({"command": "grep -n \"decorrelat\\|fundamental\\|transfer coefficient\\|deflated_sharpe\\|def deflated\\|def .*ic\\|corr\" /home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py | head -40; echo \"=== ch20 chapter20 md fundamental law ===\"; grep -n -i \"fundamental law\\|transfer coefficient\\|decorrelat\" /home/georg/projects/ml4t-zh/20_strategy_synthesis/chapter_20.md | head -20"})`


> [reasoning] Let me check backtest_explorer.py for a "deflated_sharpe" method and maybe an IC-Sharpe correlation. It was in the grep for "decorrelat". Let me grep that file.

  <details><summary>tool output</summary>

  ```text
92:def _parse_spec(spec_str: str | None) -> dict | None:
171:    def summary(self) -> dict[str, int]:
852:    # deflated_sharpe: DSR from registry data
855:    def deflated_sharpe(
866:        multiple-testing correction) is computed on the fly from
877:        correction was computed over and ``k_variants_scoped`` is the count
880:        correction belonged to rather than a leader that appears to need
883:        ``deflated_sharpe``, ``expected_max_sharpe``, ``dsr_pvalue``,
893:            Columns: source, sharpe, psr_pvalue, deflated_sharpe,
899:        from ml4t.diagnostic.evaluation.stats import deflated_sharpe_ratio
940:                psr = deflated_sharpe_ratio([arr], periods_per_year=periods_per_year)
979:            # live one leaves `k_variants` untouched, and the correction wou
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:48Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py", "offset": 840, "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py", "offset": 1371, "limit": 90})`


> [reasoning] The Fundamental Law diagnostic and IC-Sharpe scatter is implemented in `case_studies/utils/backtest_explorer.py` method `ic_sharpe_scatter(prediction_hash)` (line 1371). Let me read that method to describe how breadth is computed. Also `deflated_sharpe` method at 855. Let me read lines 840-1010 and 1371-1460.
Found the Fundamental Law / IC-Sharpe machinery in `backtest_explorer.py`. Reading both methods.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py</path>
<type>file</type>
<content>
840:         best_per_stage = df.sort("sharpe", descending=True).group_by("stage").first()
841:
842:         # Sort by pipeline order
843:         return (
844:             best_per_stage.with_columns(
845:                 pl.col("stage").replace_strict(stage_order, default=99).alias("_order")
846:             )
847:             .sort("_order")
848:             .drop("_order")
849:         )
850:
851:     # -----------------------------------------------------------------
852:     # deflated_sharpe: DSR from registry data
853:     # -----------------------------------------------------------------
854:
855:     def deflated_sharpe(
856:         self,
857:         stage: str = "s
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py</path>
<type>file</type>
<content>
1371:     def ic_sharpe_scatter(
1372:         self,
1373:         stage: str = "signal",
1374:         *,
1375:         top_n: int = 10,
1376:     ) -> pl.DataFrame:
1377:         """Join prediction IC per fold with backtest Sharpe per fold.
1378:
1379:         This enables the empirical fundamental law test: plotting IC
1380:         against realized Sharpe at the fold level to see whether
1381:         better predictions produce better portfolio returns.
1382:
1383:         Parameters
1384:         ----------
1385:         stage : str
1386:             Pipeline stage to filter backtests.
1387:         top_n : int
1388:             Number of top backtests (by headline Sharpe) t
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:52Z


> [reasoning] I have all I need. Let me write the report. I'll be structured and technical. Include absolute paths. Cap lists at 5 where possible per AGENTS.md, but the request demands completeness; I'll organize with sections and keep bullet counts reasonable.

Note: the report should be technical and complete. The ADHD output style says cap lists at 5 items, but this is a research report request, exception "explain fully when asked to explain." The request explicitly asks for structured technical detail. I'll balance.

Let me write.
<analysis>
**Literal Request**: Map ml4t-zh's evaluation/backtest/overfitting stack across chapters 16-20 and locate the ml4t-diagnostic/ml4t-backtest libraries and their public API.
**Actual Need**: A factual, symbol-level comparison target for AlphaMill's strict validation gate, so they can pick which false-discovery controls to adopt.
**Success Looks Like**: Exact paths, class/function names, what each computes, and an unambiguous statement on library vendoring/install status.
</analysis>

# ml4t-zh evaluation / backtesting / overfitting machinery

## 0. Library status (question 6, answered first)

**Neither vendored nor installed in the working environment.** They are PyPI dependencies declared in `/home/georg/projects/ml4t-zh/pyproject.toml` (lines 56-66):

```
ml4t-data>=0.1.2, ml4t-diagnostic>=0.1.4, ml4t-engineer>=0.1.3,
ml4t-backtest>=0.1.3, ml4t-live>=0.1.0, ml4t-models>=0.1.2
```

- `python3 -c "import ml4t"` fails; no `ml4t*` directory exists anywhere under `/home/georg/.cache/uv`, `/home/georg/.local`, or the repo. The uv cache has no extracted ml4t diagnostic/backtest package.
- The notebooks assume the Docker image named `ml4t` or `uv run`, per every chapter's docstring (`**Docker image**: ml4t`).
- The only in-repo handling of the library source is `/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/_library_validation.py`: it imports `ml4t.backtest.__file__`, walks up to a sibling repo containing `validation/benchmark_suite.py`, or falls back to `~/ml4t/libraries/ml4t-backtest`. So internal engine-parity helpers are loaded from source when present; none is present here.
- Consequence: I can document the **public API the notebooks call** (exact imported names and call signatures) but not the library internals. The production statistical wrappers in `case_studies/utils/` are in-repo and fully readable, and they are where the real gating logic lives.

### ml4t-diagnostic public API actually invoked

`ml4t.diagnostic.evaluation.stats` (39 imports, the overfitting core):
`deflated_sharpe_ratio`, `deflated_sharpe_ratio_from_statistics`, `compute_min_trl`, `min_trl_fwer`, `compute_pbo`, `effective_number_of_trials`, `rademacher_complexity`, `ras_sharpe_adjustment`, `ras_ic_adjustment`, `RASResult`, `benjamini_hochberg_fdr`, `holm_bonferroni`, `multiple_testing_summary`, `whites_reality_check`, `compute_sharpe_variance`, `_optimal_block_size`, `_stationary_bootstrap_indices`.

Other namespaces: `ml4t.diagnostic.metrics` (`sharpe_ratio`, `sortino_ratio`, `cross_sectional_ic`, `cross_sectional_ic_series`, `compute_ic_hac_stats`, `compute_ic_uncertainty`, `pooled_ic`), `ml4t.diagnostic.evaluation` (`PortfolioAnalysis`, `TradeShapAnalyzer`), `ml4t.diagnostic.splitters` (`CombinatorialCV`, `WalkForwardCV`), `ml4t.diagnostic.signal.signal_ic.extract_signal_ic_series`.

`ml4t.backtest` public API: `BacktestConfig`, `DataFeed`, `Engine`, `ExecutionMode`, `OrderSide`, `Strategy`; `config.{CommissionType, SlippageType, ExecutionPrice, ShareType, FillOrdering}`; `execution.rebalancer.{RebalanceConfig, TargetWeightExecutor}`; `execution.impact.{NoImpact, SquareImpact, LinearImpact}`; `execution.limits.VolumeParticipationLimit`; `risk/{RuleChain, StopLoss, TakeProfit, TrailingStop, TimeExit, DailyLossLimit, MaxDrawdownLimit, RiskManager}`; `analytics.{MAEMFEAnalyzer, TradeAnalyzer}`; presets via `BacktestConfig.from_preset("backtrader"|"vectorbt"|"lean")`.

---

## 1. Chapter 16 - backtesting as falsification and search-aware Sharpe inference

### Trading protocol / falsification
`/home/georg/projects/ml4t-zh/16_strategy_simulation/01_backtest_first_principles.py`
- Self-contained Polars/NumPy simulator, no framework. Signal read at month-end close, orders fill at **next session open** (`next-open` gap is the anti-lookahead device), fee charged on every traded dollar, cash constraint enforced, benchmark rebalanced on identical dates. Pass/fail criteria are written before the run ("configuration is fixed before the run and is never adjusted").
- `chapter_16.md` documents §16.2 protocol (timing, rebalancing, sizing, fills, costs, constraints, data availability, benchmark) and §16.1 "backtest is not proof, it is a structured attempt to show it fails."

### Engines and parity harness
- `/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/result.py` - `@dataclass BacktestResult` (framework, equity_curve, trades, positions, metrics; properties `final_value`, `total_return`, `n_trades`).
- `/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/weights.py` - `predictions_to_weights` (top-quintile), `_top_quintile_weights`, `load_case_study_data`, `load_prices`, `load_signals`, `_truncate_to_common_end`; `COST_BPS` per case study. Isolates signal generation so engine divergence is the only variable.
- `/home/georg/projects/ml4t-zh/16_strategy_simulation/validation/adapters/ml4t_adapter.py` - `run_ml4t(...)` with modes `default`/`backtrader`/`vectorbt`/`lean`. Classes `PrecomputedWeightStrategy`, `VBTSequentialStrategy` (frozen pre-trade value, sequential fills, cash-capped), `SequentialWeightStrategy` (Backtrader cheat-on-close), `LeanWeightStrategy` (frozen value, integer shares). `_forward_fill_prices`, `_install_synthetic_execution_guard`, `_convert_result`. Sibling adapters `vectorbt_adapter.py`, `lean_adapter.py`. Parity notebooks each carry provenance "Regenerated from ml4t/backtest merge 0c3de46b...".
- Vectorized vs event-driven treated as *simulation semantics* (`07_engine_divergence_anatomy.py`, `18_vectorbt_engine_parity.py`): cash release, order sequencing, fill conventions.

### Deflated Sharpe Ratio
`/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py`
- Local educational implementation `deflated_sharpe_ratio(...)` with `_expected_max_sharpe(variance_trials, n_trials)` (extreme-value/Gumbel form using Euler-Mascheroni) and `_format_dsr_result(...)`. It exposes the paper equation: `z = (SR_native - E[max]) * sqrt(n-1) / sqrt(1 - skew*SR + (kurt-1)/4 * SR^2)`, p-value via `stats.norm.sf`.
- Library call: `deflated_sharpe_ratio_from_statistics(observed_sharpe, n_samples, n_trials, variance_trials, skewness, excess_kurtosis)` returning `.probability`, `.min_trl_years`, `.has_adequate_sample`. Library rescales cross-trial variance with a finite-sample multiple-trial convention, evaluates the non-normal variance at the adjusted benchmark, supports autocorrelation and `correlation_method="marchenko_pastur"|"effective_rank"`.
- Also defines local `probabilistic_sharpe_ratio(...)` (single-strategy, benchmark SR).

### Probability of Backtest Overfitting (PBO / CSCV)
Same file, section 8:
- `cscv_sharpe_matrices(strategy_returns, n_blocks)` - builds complementary IS/OOS Sharpe rows for every `C(n_blocks, n_blocks/2)` CSCV split from sufficient statistics (`_sharpe_from_moments`).
- `compute_pbo(is_performance, oos_performance)` (library) returns `.pbo`, `.n_combinations`, `.is_best_rank_oos_median`, `.degradation_mean`.
- `simulate_strategy_returns(...)` creates all-noise vs mixed-edge panels; section 8 explicitly tests **under-reported trial counts** (`reported_n_trials=10` vs `true_n_trials=200`) - DSR is fooled, PBO is not.

### Rademacher Anti-Serum (RAS)
`/home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py`
- Library: `rademacher_complexity(performance, n_simulations, random_state)` (Monte Carlo over random sign vectors), `ras_sharpe_adjustment(observed_sharpe, complexity, n_samples, n_strategies, delta=, return_result=)` returning native-frequency lower bound, `ras_ic_adjustment(observed_ic, complexity, n_samples, delta, kappa, return_result=)` with `RASResult` fields `.adjusted_values`, `.n_significant`, `.data_snooping_penalty`, `.estimation_error`.
- Local `massart_upper_bound(performance)` = `max_norm * sqrt(2 log N)/T`; local `normalize_column_norms`.
- **Unit discipline is the key teaching point**: complexity is computed on non-demeaned, volatility-standardized per-period returns and annualized only after the bound. Hourly example uses annualizer `sqrt(24*365)`.
- RAS bound from Paleologo Procedure 8.2: `theta >= theta_hat - 2R_hat - 3 sqrt(2 log(2/delta)/T) - sqrt(2 log(2N/delta)/T)`.
- Comparison table: DSR = selection-adjusted tail probability; RAS = finite-sample lower bound that prices candidate **correlation** directly (identical candidates have lower complexity).

### Single-strategy inference (PSR/MinTRL/Lo)
`/home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py`
- Local `sharpe_ratio_variance` (Mertens 2002), `sharpe_ratio_se`, `lo_2002_annualized_sharpe` (Lo 2002 Eq.17 with Newey-West lag cutoff), `probabilistic_sharpe_ratio`, `minimum_track_record_length` (canonical + prospective power planning), `complete_sharpe_inference`, `sharpe_ratio_checklist`.
- Library: `lib_dsr` (`deflated_sharpe_ratio(returns, frequency="daily")`, K=1 → PSR) and `compute_min_trl(returns, target_sharpe, frequency)`. Library adds AR(1) variance and returns `sharpe_ratio_annualized/expected_max_sharpe/deflated_sharpe/probability/is_significant/min_trl_years/has_adequate_sample`.

### White's Reality Check - code location in Ch16
There is **no dedicated White's Reality Check notebook in Ch16**; the README lists it as concept, but the implemented function lives in the shared utilities (section 6). Ch16's three implemented controls are DSR, PBO/CSCV, RAS. Cost sensitivity is `14_cost_sensitivity.py` (uses `ml4t.diagnostic.visualization.backtest.cost_attribution.plot_cost_sensitivity`).

---

## 6. Production selection-bias machinery (most important for AlphaMill)

This is the actual deployed gate, not the teaching notebooks.

### `/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py`
- `compute_backtest_uncertainty(...)` - block bootstrap (`_stationary_bootstrap_indices`) CIs for Sharpe/Sortino/ann-return/maxDD/Calmar, `_sharpe_se_lo` (LdP-2025 closed form via `compute_sharpe_variance(sharpe, n_samples, skewness, kurtosis, autocorrelation, n_trials=1)`), `_newey_west_mean_se`, `resolve_block_length` (rebalance_step → `_optimal_block_size` → horizon floor), per-variant PSR via `deflated_sharpe_ratio(arr, periods_per_year=...)`.
- `compute_paired_uncertainty(...)` - paired stationary bootstrap on daily-return differences, information ratio, `prob_challenger_wins`, two-sided bootstrap p-value. `joint_returns(...)` handles overlay-vs-carrier vs strategy-vs-benchmark alignment.
- `compute_independent_diff_uncertainty(...)` - for disjoint windows (holdout vs validation).
- `compute_reality_check(challenger_returns, benchmark_returns, block_size, n_bootstrap, seed)` → calls `whites_reality_check(returns_benchmark=, returns_strategies=, bootstrap_samples=, block_size=, random_state=)`; returns `reality_check_pvalue/statistic/best/k_strategies`.
- `compute_selection_adjustment(...)` - **deprecated**, raw-K only (DSR, expected max, MinTRL, Reality Check, PBO).
- `compute_cohort_metrics(returns_by_hash, periods_per_year, baseline_returns, fold_returns_by_hash, ...)` - the real bundle. Per cohort it computes:
  - `leader_min_trl` via `compute_min_trl`
  - `n_trials_effective_mp` via `effective_number_of_trials(matrix, method="marchenko_pastur")`
  - `n_trials_effective_er` via `method="effective_rank"`
  - three DSRs: raw, `correlation_method="marchenko_pastur"`, `correlation_method="effective_rank"` (each with `deflated_sharpe`, p-value, `expected_max_sharpe`, `min_trl`)
  - RAS: `rademacher_complexity(matrix, n_simulations, random_state)` then `ras_sharpe_adjustment(annualized_sharpes, complexity, n_samples, n_strategies, return_result=True)` → `ras_leader`, `ras_complexity`, `ras_n_strategies`
  - Reality Check vs `baseline_returns`
  - PBO: `_cscv_split_pairs(fold_sharpes)` builds `C(n_folds, n_folds//2)` IS/OOS mean-Sharpe matrices → `compute_pbo(is_perf, oos_perf)` → `pbo`, `pbo_n_combinations`, `pbo_median_oos_rank`, `pbo_mean_degradation`, `pbo_n_folds`
  - `cohort_member_digest(hashes)` (SHA-256, order-independent) to prove a stored correction belongs to the cohort it is reported against.
- Stage baseline registry: `STAGE_SEQUENCE = (signal, allocation, risk_overlay, cost_sensitivity)`, `STAGE_BASELINE`, `descends_from(...)`, `carried_blocks(...)`.

### `/home/georg/projects/ml4t-zh/case_studies/utils/cohort_metrics.py`
- `compute_and_register(cs, universe_filter, prediction_hashes, ...)` computes three cohort granularities (per-family, per-(stage,label), per-label) and persists to `cohort_metrics`.
- `process_cohort`, `_list_family_cohorts`, `_list_stagelabel_cohorts`, `_list_label_cohorts`, `_per_fold_sharpe_by_variant`, `_resolve_baseline_hash`.
- Guards: `degenerate_prediction_sql`, `full_coverage_prediction_sql`, `_UNIVERSE_FILTER_CLAUSE`, `_LIVE_POPULATION_CLAUSE`; `cost_sensitivity` excluded from K.

### `/home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py`
- `BacktestExplorer.deflated_sharpe(stage, top_n, periods_per_year, prediction_hashes)` - per-variant PSR computed on the fly from `daily_returns.parquet`; selection-bias columns (ER DSR default, MP and raw alongside, RAS, Reality Check, PBO) read from the persisted `cohort_metrics`. Enforces that a stored correction is only reported when `member_digest`/`k_variants` match the scoped cohort.
- `BacktestExplorer.ic_sharpe_scatter(stage, top_n)` - joins per-fold IC with per-fold Sharpe, "the empirical fundamental law test."

### Ch7 multiple-testing (feature-level FDR)
`/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py`
- Library: `benjamini_hochberg_fdr(p_values, alpha, return_details)` (BH FDR), `holm_bonferroni` (FWER), `multiple_testing_summary`, `min_trl_fwer(observed_sharpe, n_trials, variance_trials, target_sharpe, frequency)`, `deflated_sharpe_ratio`, `compute_pbo`, `rademacher_complexity`, `ras_ic_adjustment`.
- `compute_ic_hac_stats(ic_series, label_horizon=)` (Newey-West HAC t/p per factor).
- Explicit exploration/confirmation two-pass: BH on the full set at alpha=0.10 promotes; BH on promoted only at alpha=0.05 confirms.
- Harvey/Liu/Zhu threshold table t>2.0/3.0/3.5.

---

## 2. Chapter 20 - synthesis: IC-Sharpe, cascade, cost survival, holdout

### Holdout discipline - the core overfitting control
`/home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py`
- `select_best_models(cs_id, top_n, min_ic, families, labels)` - pools validation backtests across `HOLDOUT_SELECTION_STAGES = ("signal","allocation","risk_overlay")` (explicitly excludes `cost_sensitivity` and `benchmark` family, matching the cohort DSR trial-count basis), dedupes by `prediction_hash`, applies `LABEL_RESTRICTIONS` and `UNIVERSE_RESTRICTIONS`.
- `build_holdout_split(mds, setup)` - train window matches CV fold window length, ends before holdout start minus label buffer.
- `_is_degenerate_predictions(...)` - rejects constant/all-NaN/single-unique retrains; `generate_holdout(...)` falls back to rank-2/3... (`max_fallback_attempts=5`) and records `selection_ordinal`.
- `has_holdout_predictions`, `load_existing_holdout`, `delete_holdout_predictions`, `_referencing_columns` (schema-read FK-safe deletion). `TRAIN_DISPATCH` maps linear/gbm/deep_learning/tabular_dl/latent_factors.
- `00_holdout_predictions.py` generates rank-1-on-holdout predictions; `load_existing_holdout` computes **val_sharpe for the exact same checkpoint** as the holdout.

### Feature triage (FDR)
`/home/georg/projects/ml4t-zh/20_strategy_synthesis/02_feature_evaluation.py`
- Reads per-CS `triage_ledger.parquet`; `fdr_sig = fdr_p < FDR_ALPHA (0.05)`. PROCEED is the **union** of BH significance and `stable_and_above_threshold` (effect size + fold sign consistency), explicitly not nested. `funnel` computes candidate/FDR-sig/PROCEED counts; forward-links PROCEED rate to rank-1 validation and holdout Sharpe.

### IC-Sharpe translation / Fundamental Law
- `03_signal_quality.py`: IC heatmap vs median signal-stage Sharpe heatmap per family; within-family max−median spread ("choice of configuration doing the work"); family stats.
- `04_signal_to_strategy.py`: holdout IC vs holdout Sharpe with CIs; validation-vs-holdout Sharpe arrows for the same configuration; IC-leader vs Sharpe-leader agreement; cadence table. Explicitly warns validation IC available is a sweep maximum while holdout IC is the selected single draw (the "manufactured decay" bug is documented and fixed).
- `backtest_explorer.ic_sharpe_scatter` is the fold-level empirical Fundamental Law join (IC vs Sharpe/CAGR/maxDD per fold). The **breadth-adjusted** Fundamental Law figure (`I ≈ IC × sqrt(BR)`) is described in `20_strategy_synthesis/chapter_20.md` §20.3/Figure 20.12 and computed in `05_portfolio_allocation.py` (breadth = rebalance frequency × top-K), not in 04.

### Model-family cascade
The "cascade" is not a single function: it is the stage-carry lineage plus per-stage family ranking. `01_aggregate_synthesis.py` aggregates registries; `BacktestExplorer.champion_lineage` and `descends_from`/`carried_blocks` enforce that a later stage's leader actually descends from the earlier baseline block (shared signal hash fixes predictions only). `05_portfolio_allocation.py` restricts to `equal_weight, inverse_vol, mvo_ledoit_wolf, risk_parity, hrp, conformal_weighted`, holds the signal carrier fixed, and measures best−worst allocator spread per case study + breadth analysis.

### Cost survival
`/home/georg/projects/ml4t-zh/20_strategy_synthesis/06_cost_survival.py`
- `_sharpe_at(curve, cost_bps)` linear interpolation between grid brackets; `_breakeven(curve)` interpolates the last positive → first negative grid Sharpe and flags **censored** curves (still positive at grid ceiling).
- `sharpe_drag`, `drag_pct`, `cost_margin_bps`, `cost_margin_ratio = breakeven/assumed`, `resilience` in {does not survive, fragile, marginal, robust, very robust}; `TURNOVER_MULTIPLIER` per cadence. Options case uses executable bid/ask (median round-trip spread 1091 bps, best executable Sharpe −1.05).

### Regime / holdout failure modes
`07_regime_risk.py`: `classify_overlay` (trailing_stop, mae_mfe_calibrated, stop_loss, take_profit, daily_limit, dd_breaker, vol_target, combined, time_exit), `extract_risk_name`, per-CS baseline vs best overlay, category mean Sharpe delta and `pct_positive`, category×CS heatmap, drawdown protection. `08_recommendations.py` records per-CS next steps and holdout collapse; documented failure modes include structural break, prediction-quality drift, and portfolio-translation drift.

---

## 3. Chapter 17 - portfolio construction

`/home/georg/projects/ml4t-zh/17_portfolio_construction/`
- `02_mean_variance_optimization.py`: `simulate_portfolios`, `optimize_max_sharpe`, `optimize_min_vol`, `equal_risk_contribution`, `compute_efficient_frontier`, `validate_optimization_result`, `neg_sharpe`; `DailyTargetWeightStrategy`, `run_daily_target_engine`.
- `03_robust_optimization.py`: Riskfolio-Lib risk parity / min-CVaR / min-variance.
- `04_kelly_criterion.py`: `compute_kelly_fraction`, `compute_growth_rate`, `kelly_fraction_continuous`, `empirical_growth_rate`, `optimal_kelly_empirical`, `simulate_wealth_paths`, `terminal_wealth_distribution`.
- `06_hierarchical_risk_parity.py`: `correlation_distance`, `cluster_assets`, `get_quasi_diagonal_order`, `cluster_variance`, `recursive_bisection` (HRP).
- `07_conformal_position_sizing.py`: Mondrian split-conformal, horizon-embargoed prior residuals; `w_i ∝ 1/Δ_i` (inverse interval width). Calls `compute_ic_hac_stats`, `extract_signal_ic_series`. ETF +5.5%, CME −24.8% documented.
- `09_allocator_comparison.py`: `equal_weight_allocation`, `inverse_vol_allocation`, `mvo_lw_allocation`, `hrp_allocation`, `_recursive_bisect`, `_cluster_variance`, `compute_rebalance_turnover`, `annualized_sharpe_se`, `build_comparison_table`, `AllocatorComparisonStrategy`; selection-bias-aware (`Sharpe SE` per allocator).
- `13_deepm_regime_robust.py`: DeePM SoftMin rolling-window Sharpe loss (`deepm/losses.py: sharpe_ratio, softmin_sharpe, robust_sharpe_loss, compute_net_portfolio_returns`).

---

## 4. Chapter 18 - transaction costs

`/home/georg/projects/ml4t-zh/18_transaction_costs/_cost_analysis.py` (shared library):
- `corwin_schultz_spread(high, low, window)` (Corwin-Schultz high-low estimator), `roll_spread(close, window)` (Roll serial-covariance).
- `compute_adv`, `compute_adv_usd`.
- `calibrate_sqrt_impact(...)` fits `η` in `|r| = σ·η·√(V/ADV)`; `estimate_kyle_lambda(price_changes, signed_volume)` fits `ΔP = λQ` via `HuberRegressor`.
- `estimate_capacity(adv_usd, impact_coeff, gross_alpha_bps, turnover, max_participation)` → max AUM, breakeven participation.
- `breakeven_alpha(turnover, cost_bps) = turnover * cost_bps / 1e4`.
- `FEE_SCHEDULES` + `get_fee_schedule`, `standardized_cost_per_100k`.

Notebooks:
- `01_cost_taxonomy.py`: `cost_components`, `dominant_component_label`, `summarize_dollar_turnover`, `fee_evidence_row`, `cost_schema_row`.
- `02_spread_estimation.py`: `estimate_spreads`, `compute_validation_metrics`, `classify_cost_units` (validates OHLCV spread estimates against microstructure ground truth).
- `03_market_impact_calibration.py`: `add_impact_features`, `estimate_normalized_lambda`, `capacity_curve`, `regime_impact_row`, `session_integrity_ledger`.
- `04_vwap_twap_execution.py`: `TWAPAlgorithm`, `VWAPAlgorithm`, `build_twap_schedule`, `build_vwap_schedule`, `normalize_volume_curve`, `execute_day`, `market_vwap_of`, `summarize_tracking`.
- `05_almgren_chriss_optimal_execution.py`: `AlmgrenChrissParams` (and `ExtendedParams`), `optimal_trajectory`, `expected_cost`, `execution_variance`, `execution_std`, `liquidation_half_life`, `compute_efficient_frontier`, `simulate_execution`, `generate_tca_report`, `executed_fills`.
- `07_ml4t_volume_participation.py` / `06_ml4t_execution_demo.py`: `VolumeParticipationLimit`, `SquareRootImpact`, `LinearImpact`, `NoImpact`, `ExecutionResult`, `compose_limit_and_impact`.
- `09_frequency_tradeoff.py`: `CostAssumptions`, `calculate_break_even_alpha`, `real_net_by_frequency`, `evaluate_decay_scenario`.
- `10_gross_vs_net_performance.py`: `CostStack`, `apply_cost_stack`, `compute_performance`.
- `11_cost_cliff.py`: `IntradayCostStack`, `calculate_intraday_net_performance`, `calculate_break_even_turnover`.
- `12_commission_slippage_comparison.py`: `asset_class_cost_row`, `run_backtest_variant` across 6 commission and 5 slippage models.

---

## 5. Chapter 19 - risk management

`/home/georg/projects/ml4t-zh/19_risk_management/`
- `01_var_cvar.py`: `historical_var`, `parametric_var`, `cornish_fisher_var`, `monte_carlo_var`; `historical_cvar`, `parametric_cvar`, `student_t_cvar`; `kupiec_test` (coverage backtest), `backtest_var`; `drawdown_path`; `portfolio_tail_risk`; `qlike_loss`, `variance_mse` (forecast scoring). Uses `ml4t.diagnostic.evaluation.distribution.analyze_distribution` and `arch.arch_model` GARCH.
- `06_stress_testing.py`: `StressScenario`, `apply_scenario`, `max_drawdown`, `slice_stress_window`, `analyze_stress_period`, `student_t_parameters`, `simulate_student_t_paths`, `monte_carlo_stress_test`, `sensitivity_analysis`, `classify_regime`, `analyze_by_regime`, `compare_portfolios_stress`.
- `02_exit_strategies.py`: `FixedExitConfig`, `TrailingStopConfig`, `ATRStopConfig`, `HybridExitConfig`, `simulate_fixed_exits`, `simulate_trailing_stops`, `simulate_atr_exits`, `simulate_ml_exits`, `simulate_hybrid_exits`, `create_position_state`, `should_exit`.
- `04_factor_exposure.py`: `capm_regression`, `ff3_regression`, `ff5_regression`, `rolling_factor_regression`, `factor_attribution`, `hac_mean_standard_error`.
- `07_drift_detection.py`: `ProductionDriftMonitor`, `DriftMonitorConfig`, `checked_drift_analysis`, `gpu_domain_classifier`, PSI/Wasserstein functions, `policy_alert_level`, `combined_alert_level`.
- `10_ml4t_backtest_risk_demo.py` = **kill switches**: imports `DailyLossLimit`, `MaxDrawdownLimit`, `RiskManager` from `ml4t.backtest.risk`, plus `RuleChain, StopLoss, TakeProfit, TimeExit, TrailingStop`; `first_trigger`, `create_portfolio_state`. `03_position_sizing_mae_mfe.py`: `FixedFractionalConfig`, `calculate_fixed_fractional_size`, `calculate_inverse_volatility_weights`. `09_deep_hedging.py`: `CVaRLoss`, `DeepHedger`, computed CVaR. `11_systematic_risk_sweep.py`: `run_risk_sweep`, `run_1d_sweep`, `run_rule_grid`, `add_surface`.

---

<results>
<files>
- /home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py - production selection-bias bundle: DSR raw/MP/ER, RAS, White's Reality Check, PBO/CSCV, bootstrap CIs, MinTRL, paired bootstrap
- /home/georg/projects/ml4t-zh/case_studies/utils/cohort_metrics.py - computes and persists the per-family/per-stage/per-label cohort trial counts and corrections into registry.db
- /home/georg/projects/ml4t-zh/case_studies/utils/backtest_explorer.py - `deflated_sharpe()` gate and `ic_sharpe_scatter()` fold-level IC-Sharpe (Fundamental Law) join
- /home/georg/projects/ml4t-zh/20_strategy_synthesis/holdout.py - frozen-holdout protocol: rank-1 selection, retrain, degeneracy fallback, stale-holdout deletion
- /home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py - DSR + PBO + RAS tutorial with local math and library calls
- /home/georg/projects/ml4t-zh/16_strategy_simulation/13_ras_protocol.py - Rademacher complexity / RAS in native units, Massart bound
- /home/georg/projects/ml4t-zh/16_strategy_simulation/11_sharpe_ratio_inference.py - PSR, MinTRL, Lo 2002 autocorrelation-aware annualization
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py - BH-FDR, Holm-Bonferroni, HAC IC inference, exploration/confirmation pass
- /home/georg/projects/ml4t-zh/18_transaction_costs/_cost_analysis.py - spread estimators, sqrt impact calibration, Kyle lambda, capacity, breakeven alpha, fee schedules
- /home/georg/projects/ml4t-zh/19_risk_management/10_ml4t_backtest_risk_demo.py - RuleChain/StopLoss/TakeProfit/TrailingStop/DailyLossLimit/MaxDrawdownLimit/RiskManager kill switches
- /home/georg/projects/ml4t-zh/pyproject.toml - declares ml4t-diagnostic>=0.1.4 and ml4t-backtest>=0.1.3 (lines 56-66); libraries are not vendored
</files>

<answer>
**Are the libraries vendored/installed?** No. `ml4t-diagnostic` and `ml4t-backtest` are PyPI dependencies in `pyproject.toml`; the base python has no `ml4t` module and no source copy exists in the uv cache or repo. All library behavior must be inferred from call sites; the in-repo `case_studies/utils/` wrappers are the real production gate.

**Overfitting / false-discovery controls implemented:**
1. **DSR** three ways in production: raw-K, Marchenko-Pastur effective trials, and effective-rank (ER is the default surfaced). Library call `deflated_sharpe_ratio(returns_matrix, periods_per_year=, correlation_method="marchenko_pastur"|"effective_rank")`; returns `deflated_sharpe`, `p_value`, `expected_max_sharpe`, `min_trl`, `is_significant`. `effective_number_of_trials(matrix, method=...)` produces `k_eff`.
2. **White's Reality Check**: `whites_reality_check(returns_benchmark, returns_strategies, bootstrap_samples, block_size, random_state)` in `compute_reality_check()`, benchmarked against the stage baseline.
3. **PBO via CSCV**: `_cscv_split_pairs` builds all `C(n_folds, n_folds//2)` complementary IS/OOS mean-Sharpe rows, then `compute_pbo(is_perf, oos_perf)` returns pbo, rank median, degradation.
4. **RAS**: `rademacher_complexity` + `ras_sharpe_adjustment` (and `ras_ic_adjustment` for signal quality), giving a finite-sample lower bound rather than a probability. Crucially computed on non-demeaned volatility-standardized per-period returns.
5. **FDR/FWER at feature level**: `benjamini_hochberg_fdr` and `holm_bonferroni` on HAC p-values, plus a two-pass exploration/confirmation split.
6. **MinTRL / power planning** and **Lo 2002** autocorrelation-corrected Sharpe inference.
7. **Holdout discipline**: rank-1 chosen on validation Sharpe across signal+allocation+risk_overlay only (cost_sensitivity and benchmark excluded from the trial count), retrained on pre-holdout window matching fold length, frozen, with degeneracy fallback and stale-holdout invalidation.
8. **Cost-survival gate**: interpolated breakeven cost (censored above grid ceiling flagged), cost-margin ratio, resilience classes.
9. **Counterfactual hygiene**: `cohort_member_digest` and `member_digest` prevent reporting a stored DSR/RAS/PBO against a cohort it was not computed over; `k_variants` vs `k_variants_scoped` exposure.

**Not present:** White's Reality Check has no dedicated Ch16 notebook; the Fundamental Law is documented in `chapter_20.md` and implemented as `ic_sharpe_scatter` + breadth in `05_portfolio_allocation.py`, not as a standalone `br`/transfer-coefficient function. No StepM/SPA test or bootstrap-based Sharpe difference test beyond the paired stationary bootstrap is implemented.
</answer>

<next_steps>
To design AlphaMill's gate, port in priority order: (1) `compute_cohort_metrics` semantics - ER/MP-adjusted DSR + RAS + Reality Check + PBO on an aligned T×K return matrix with member-digest provenance; (2) `holdout.py` stage-exclusion rule for trial counting and degeneracy fallback; (3) `_breakeven`/`cost_margin_ratio` cost-survival gate; (4) `resolve_block_length` + stationary-bootstrap CIs. Read `/home/georg/projects/ml4t-zh/case_studies/utils/uncertainty.py` lines 762-1334 as the reference implementation; it is the closest in-repo analog to a strict evidence gate.
</next_steps>
</results>
