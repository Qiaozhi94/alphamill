---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f665f0894ffewx9yjZ0acsHV2h"
title: "ml4t research workflow core (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-13T07:17:38Z"
updated_at: "2026-09-13T07:18:55Z"
tokens_input: 176957
tokens_output: 9891
cost: 0.0376
parent_id: "ses_f6664247effe4SLb37r5OF4RZ9"
---

# ml4t research workflow core (@explore subagent)

## user · 2026-09-13T07:17:38Z

[CONTEXT] I am analyzing the repo /home/georg/projects/ml4t-zh (companion code for "Machine Learning for Trading, 3rd Edition" by Stefan Jansen). It is a 27-chapter quant research-to-production workflow. I am comparing it against a new project (AlphaMill) that builds an AI-factor-factory-led crypto quant pipeline. I need to understand ml4t's CORE RESEARCH DISCIPLINE so I can extract borrowable design patterns.

[GOAL] Produce a precise, evidence-backed description of ml4t's research framework and methodological discipline: how a strategy idea is defined, validated, and how overfitting is controlled. I need concrete file paths, function/class names, config schemas, and the exact mechanisms (not marketing prose).

[DOWNSTREAM] I will use this to recommend which methodological controls AlphaMill should adopt or strengthen in its evidence/evaluation gate.

[REQUEST] Investigate these areas and report file paths + key symbols + how they work:
1. utils/ directory: shared config, paths, CV code. Especially any walk-forward / purged / embargoed cross-validation implementation (search for "walk_forward", "purged", "embargo", "combinatorial").
2. 01_process_is_edge/: the ML4T workflow concept, the "evidence boundary" (exploration vs confirmation), regime detection.
3. 06_strategy_definition/: trading protocol specification, universe rules, decision schedule, cost model, evaluation protocol, run logging.
4. 07_defining_the_learning_task/: labels (forward return, triple-barrier, trend-scanning), IC/quantile feasibility screens, multiple-testing control (BH-FDR, Deflated Sharpe Ratio), causal plausibility.
5. Any "run log" / experiment registry mechanism used across chapters.
6. How notebooks are structured (Jupytext .py+.ipynb), and what reproducibility guarantees exist.

Report as a structured list: for each area, 2-4 sentences on the mechanism + concrete file paths + the specific function/class names. Skip notebooks' plotting code. Be concrete and technical.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-13T07:17:38Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh"})`
- **tool**: `glob({"pattern": "**/*.py", "path": "/home/georg/projects/ml4t-zh"})`
- **tool**: `grep({"pattern": "walk_forward|purged|embargo|combinatorial", "path": "/home/georg/projects/ml4t-zh", "output_mode": "files_with_matches"})`
- **tool**: `glob({"pattern": "**/README*", "path": "/home/georg/projects/ml4t-zh"})`


> [reasoning] Let me start by exploring the repo structure. I'll launch parallel searches.
<analysis>
**Literal Request**: Investigate ml4t-zh's research framework across 6 areas (utils CV, 01_process_is_edge, 06_strategy_definition, 07_defining_the_learning_task, run logging, notebook structure) with file paths, symbols, and mechanisms.
**Actual Need**: Extract concrete methodological controls (leakage prevention, multiple-testing correction, evidence boundaries, reproducible experiment tracking) to decide what AlphaMill should adopt.
**Success Looks Like**: A technical map with absolute paths, function/class names, and a short explanation of how each control works, so AlphaMill design decisions can cite ml4t precedents.
</analysis>

Let me start with broad reconnaissance in parallel.

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
Found 100 file(s)

/home/georg/projects/ml4t-zh/scripts/download_artifacts.py
/home/georg/projects/ml4t-zh/scripts/pre_run_gate.py
/home/georg/projects/ml4t-zh/scripts/prove_crypto_interface.py
/home/georg/projects/ml4t-zh/scripts/sync_ch16_real_strategy_parity.py
/home/georg/projects/ml4t-zh/scripts/prove_cme_futures_interface.py
/home/georg/projects/ml4t-zh/scripts/probe_latent_identities.py
/home/georg/projects/ml4t-zh/scripts/prove_us_firm_latent_interface.py
/home/georg/projects/ml4t-zh/scripts/pdf_chapter_to_md.py
/home/georg/projects/ml4t-zh/scripts/verify_installation.py
/home/georg/projects/ml4t-zh/scripts/create_experiment.py
/home/georg/projects/ml4t-zh/scripts/prove_us_equities_fold_major.py
/home/georg/projects/ml4t-zh/scripts/migrate_training_identity.py
/home/georg/projects/
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 244 match(es) in 244 file(s)

/home/georg/projects/ml4t-zh/ml4t_bilingual.md

/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.ipynb

/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py

/home/georg/projects/ml4t-zh/06_strategy_definition/chapter_06_zh.md

/home/georg/projects/ml4t-zh/06_strategy_definition/README.md

/home/georg/projects/ml4t-zh/06_strategy_definition/chapter_06.md

/home/georg/projects/ml4t-zh/12_gradient_boosting/chapter_12.md

/home/georg/projects/ml4t-zh/12_gradient_boosting/04_optuna_tuning.py

/home/georg/projects/ml4t-zh/12_gradient_boosting/07_hpo_comparison.py

/home/georg/projects/ml4t-zh/12_gradient_boosting/11_conformal_gbm.py

/home/georg/projects/ml4t-zh/12_gradient_boosting/11_conformal_gbm.ipynb

/home/georg/
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 62 file(s)

/home/georg/projects/ml4t-zh/README.md
/home/georg/projects/ml4t-zh/utils/README.md
/home/georg/projects/ml4t-zh/tests/fixtures/README.md
/home/georg/projects/ml4t-zh/tests/README.md
/home/georg/projects/ml4t-zh/scripts/README.md
/home/georg/projects/ml4t-zh/envs/README.md
/home/georg/projects/ml4t-zh/data/fx/README.md
/home/georg/projects/ml4t-zh/data/macro/README.md
/home/georg/projects/ml4t-zh/data/prediction_markets/README.md
/home/georg/projects/ml4t-zh/data/futures/positioning/README.md
/home/georg/projects/ml4t-zh/data/futures/README.md
/home/georg/projects/ml4t-zh/data/etfs/README.md
/home/georg/projects/ml4t-zh/data/factors/README.md
/home/georg/projects/ml4t-zh/data/equities/positioning/README.md
/home/georg/projects/ml4t-zh/data/equities/market/us_equities/READ
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:41Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/utils /home/georg/projects/ml4t-zh/01_process_is_edge /home/georg/projects/ml4t-zh/06_strategy_definition /home/georg/projects/ml4t-zh/07_defining_the_learning_task /home/georg/projects/ml4t-zh/case_studies/research /home/georg/projects/ml4t-zh/case_studies/utils/registry"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/utils/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/cv.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/holdout.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/strategy.py"})`


> [reasoning] Let me dig into the key directories. Start with utils/, 01_process_is_edge, 06_strategy_definition, 07_defining_the_learning_task, case_studies/research, and run logs.

Let me read the key files in parallel.
Now let me dive into the core files in parallel.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/01_process_is_edge:
total 328
drwxr-xr-x  3 georg georg  4096 Sep 11 01:24 .
drwxr-xr-x 42 georg georg  4096 Sep 12 01:44 ..
-rw-r--r--  1 georg georg  8292 Sep 10 00:21 README.md
drwxr-xr-x  2 georg georg  4096 Sep 10 00:21 assets
-rw-r--r--  1 georg georg 53565 Sep 11 00:40 chapter_01.md
-rw-r--r--  1 georg georg 47103 Sep 11 01:24 chapter_01_zh.md
-rw-r--r--  1 georg georg 58916 Sep 10 00:21 factor_regimes.ipynb
-rw-r--r--  1 georg georg 34740 Sep 10 00:21 factor_regimes.py
-rw-r--r--  1 georg georg 66156 Sep 10 00:21 macro_regimes.ipynb
-rw-r--r--  1 georg georg 34336 Sep 10 00:21 macro_regimes.py

/home/georg/projects/ml4t-zh/06_strategy_definition:
total 372
drwxr-xr-x  3 georg georg  4096 Sep 11 01:25 .
drwxr-xr-x 42 georg georg  4096 Sep 12 01:44 ..
-rw
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/utils/README.md</path>
<type>file</type>
<content>
1: # Shared utilities
2: 
3: Library code imported across every chapter and case study. Notebooks run from the
4: repository root, so `import utils` and `from utils.x import y` resolve with no
5: installation. This is code you **import**, not run — for command-line tools, see
6: [`scripts/`](../scripts).
7: 
8: **Configuration and paths.** `config.py` loads and validates the paths and settings
9: in `.env` (and sorts out CUDA library paths); `paths.py` holds the chapter registry
10: and resolves chapter, case-study, and output directories so notebooks never hard-code
11: a location.
12: 
13: **Figures.** `style.py` defines the ML4T color palette and the matplotlib / Plotly
14: defaults that give every fig
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/cv.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: from dataclasses import dataclass, field, replace
4: from datetime import UTC, datetime
5: from typing import Any
6: 
7: from case_studies.utils.artifact_digest import value_digest
8: from case_studies.utils.registry.specs import canonical_json, canonical_value, compute_hash
9: from utils.cv_splits import generate_cv_splits
10: 
11: 
12: def _normalize_boundary(value: Any) -> str:
13:     raw = value.isoformat() if hasattr(value, "isoformat") else str(value)
14:     try:
15:         boundary = datetime.fromisoformat(raw.replace("Z", "+00:00"))
16:     except ValueError:
17:         return raw
18:     if boundary.tzinfo is not None:
19:         bound
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/holdout.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: from collections.abc import Mapping, Sequence
4: from copy import deepcopy
5: from datetime import time as dt_time
6: from typing import Any
7: 
8: import pandas as pd
9: import polars as pl
10: 
11: _FOLD_FIELDS = ("fold", "train_start", "train_end", "val_start", "val_end")
12: 
13: 
14: def _validation_folds(validation_spec: Mapping[str, Any]) -> list[dict[str, Any]]:
15:     computation = validation_spec.get("computation")
16:     if not isinstance(computation, dict):
17:         raise ValueError("holdout CV derivation requires a current resolved training specification")
18:     cv = computation.get("cv")
19:     if not isinstance(cv, dict):
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/strategy.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: import json
4: import re
5: import sqlite3
6: from contextlib import closing
7: from copy import deepcopy
8: from dataclasses import asdict, dataclass
9: from datetime import date, datetime, timedelta
10: from typing import TYPE_CHECKING, Any, Literal
11: 
12: import polars as pl
13: 
14: from case_studies.utils.artifact_digest import value_digest
15: from case_studies.utils.backtest_loaders import (
16:     get_backtest_config,
17:     load_backtest_prices_for,
18:     load_contract_specs_from_yaml,
19:     load_futures_market_contract,
20: )
21: from case_studies.utils.backtest_presets import (
22:     build_backtest_spec,
23:     serializab
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:48Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/utils/cv_splits.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/utils/config.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/utils/reproducibility.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/01_process_is_edge/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/06_strategy_definition/README.md"})`


> [reasoning] This is a rich repo. Let me now dig into utils/cv_splits.py, utils/config.py, utils/paths.py, utils/reproducibility.py, 01_process_is_edge README + factor_regimes.py, 06 strategy definition README/exploration, 07 labels, signal evaluation, multiple testing, causal sanity. And the registry. Let me read in parallel.
Now the CV core, reproducibility, and the process-is-edge / strategy-definition chapters.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/utils/cv_splits.py</path>
<type>file</type>
<content>
1: """Cross-validation split generation for case study pipelines.
2: 
3: Reads the ``evaluation`` section from ``setup.yaml`` and generates
4: walk-forward date boundaries by delegating to ml4t-diagnostic's
5: ``WalkForwardCV``. This is the single source of truth for CV splits
6: used by all case studies (Ch11+).
7: 
8: Usage:
9:     from utils.cv_splits import generate_cv_splits, load_evaluation_config, make_walk_forward_config
10: 
11:     # Date-boundary splits
12:     splits = generate_cv_splits(dataset, case_study_id="etfs", label_buffer="21D")
13:     for split in splits:
14:         train_mask = (df[date_col] >= split["train_start"]) & (df[date_col] <= split["train_end"])
15:         val_mask   
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/utils/config.py</path>
<type>file</type>
<content>
1: """Centralized configuration using python-dotenv.
2: 
3: This module loads all configuration from the .env file in the repository root.
4: It provides explicit, fail-fast configuration with clear error messages.
5: 
6: Configuration priority:
7: 1. .env file (ONLY source - no fallbacks)
8: 2. Validation ensures paths exist or provides clear instructions
9: 
10: Usage:
11:     from utils import ML4T_PATH, ML4T_DATA_PATH, REPO_ROOT
12: """
13: 
14: import os
15: from pathlib import Path
16: 
17: from dotenv import load_dotenv
18: 
19: # Find repository root (where .env lives)
20: REPO_ROOT = Path(__file__).parent.parent.resolve()
21: ENV_FILE = REPO_ROOT / ".env"
22: 
23: # Auto-create .env from .env.exa
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/utils/reproducibility.py</path>
<type>file</type>
<content>
1: """One-call seed initialization for reproducible notebook runs.
2: 
3: Notebooks that produce any random output should call ``set_global_seeds()``
4: in their preamble, between imports and the first computation. Monte Carlo
5: demos that *want* per-run variability should still call it, with the seed
6: declared in their parameters cell so readers can change it explicitly.
7: """
8: 
9: from __future__ import annotations
10: 
11: import os
12: import random
13: 
14: 
15: def set_global_seeds(seed: int = 42) -> None:
16:     """Seed Python ``random``, NumPy, Torch (CPU+CUDA), and ``PYTHONHASHSEED``.
17: 
18:     Polars and pandas operations that need a seed accept it per-call
19:     (e.g. ``df.
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/01_process_is_edge/README.md</path>
<type>file</type>
<content>
1: # Chapter 1: The Process Is Your Edge
2: 
3: The chapter establishes the chapter's central claim: in trading, durable performance depends less on picking a sophisticated model than on maintaining a disciplined research process that can survive changing markets, noisy signals, and real-world frictions. It gives readers a usable vocabulary for market change, shows why recent shocks exposed fragile assumptions, and reframes ML for trading as an adaptation problem rather than a model-selection contest.
4: 
5: ## Learning Objectives
6: 
7: * Distinguish structural breaks, regimes, data drift, concept drift, and online detection, and explain why static trading models degrade in changing markets

…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/06_strategy_definition/README.md</path>
<type>file</type>
<content>
1: # Chapter 6: Strategy Research Framework
2: 
3: The chapter establishes the chapter's core claim: a trading strategy is not just a signal or model, but an executable decision process that has to be defined at decision time and evaluated as if it were live. It distinguishes the live trading loop from the research loop and shows why disciplined iteration matters if historical testing is supposed to say anything about future behavior. The case studies make the workflow concrete across asset classes, cadences, and market structures, so readers see early that the same research logic must survive very different implementation environments.
4: 
5: ## Learning Objectives
6: 
7: * Place a strat
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:51Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md"})`


> [reasoning] Good. Now let's read the labels, signal evaluation, multiple testing, causal sanity, and the process_is_edge factor_regimes. Also the run log / registry. Let me look at case_studies/README.md, RUN_LOG.md, registry/specs.py, decisions.py, workspace.py, and the exploration.md in 06. Also the 01_process_is_edge notebooks. Let me batch.
Now the labels, multiple-testing, signal evaluation, causal checks, and run-log/registry.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/07_defining_the_learning_task/README.md</path>
<type>file</type>
<content>
1: # Chapter 7: Defining the Learning Task
2: 
3: The chapter shows that feature research starts long before modeling. It turns raw but validated market data into stable, protocol-safe inputs by enforcing train-only fitting, disciplined outlier handling, explicit representation choices, and visible missing-data rules. The payoff is not cosmetic cleanliness but comparability, auditability, and protection against leakage that would otherwise make later signal evaluation meaningless.
4: 
5: ## Learning Objectives
6: 
7: * Build split-aware preprocessing pipelines that produce stable, auditable inputs for label and feature computation.
8: * Define execution-consistent labels, including
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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py</path>
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
17: # **Docker image**: `ml4t`
18: 
19: # %% [markdown]
20: # # Label Engineering Methods
21: #
22: # **Chapter 7: Defining the Learning Task**
23: # **Section Reference**: 7.2 - Label Engineering
24: #
25: # ## Purpose
26: #
27: # This notebook demonstrates **all major labeling methods** f
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/README.md</path>
<type>file</type>
<content>
1: # Case Studies
2: 
3: Nine case studies thread through Chapters 6-20, applying the same ML4T workflow to different asset classes, frequencies, and trading constraints. Each case study defines a universe, builds labels and features, trains models from linear baselines through deep learning, and evaluates strategies through backtesting, portfolio construction, cost analysis, and risk management.
4: 
5: ## Overview
6: 
7: | # | Case Study | Asset Class | Frequency | Universe | Primary Label |
8: |---|------------|-------------|-----------|----------|---------------|
9: | 1 | [ETFs](etfs/) | Multi-asset ETFs | Daily | 100 ETFs | fwd_ret_21d |
10: | 2 | [Crypto Perps Funding](crypto_perps_funding/) |
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md</path>
<type>file</type>
<content>
1: # The Run Log
2: 
3: Every model training run, prediction set, causal-effect estimate, and backtest in
4: the case studies is recorded in a per-case-study **run log**. The run log is a
5: fully-deterministic experiment archive: each entry is content-addressed by a hash
6: of its complete configuration, every artifact it points to is reproducible from
7: that configuration, and nothing is anonymous or re-derivable only by re-running
8: the pipeline.
9: 
10: The run log lives at `case_studies/{case_study}/run_log/` and consists of three
11: things:
12: 
13: 1. A SQLite index (`registry.db`) that catalogs every run.
14: 2. Filesystem subdirectories holding the artifacts each run produced
15:    (`
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:54Z

- **tool**: `grep({"pattern": "class |^def |WalkForward|Combinatorial|Purged|Embargo|CPCV|purge|embargo|nested|Nested", "path": "/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py", "output_mode": "content"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/06_strategy_definition/exploration.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/01_process_is_edge/factor_regimes.py", "limit": 200})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py"})`


> [reasoning] Excellent, RUN_LOG.md is the experiment registry mechanism. Now let me examine:
- 02_cv_foundations.py (walk-forward, purged, embargoed, CPCV implementations, nested CV)
- 01_process_is_edge/factor_regimes.py (regime detection)
- 05_signal_evaluation.py (IC/quantile feasibility screens)
- 08_causal_sanity_checks.py (causal plausibility)
- 06_strategy_definition/exploration.md (evidence boundary)
- registry specs.py, decisions.py, pre_run_gate.py, create_experiment.py
- 16_strategy_simulation/12_dsr_validation.py (CPCV/DSR)
- 11_ml_pipeline/04_nested_cv_hpo.py

Let me batch read. Also search for purged/embargo classes in 06_cv_foundations. Let me grep within that file.
Now CV foundations, signal evaluation, causal checks, and the exploration/evidence-boundary spec.

  <details><summary>tool output</summary>

  ```text
Found 67 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py
  30: # 6. **Feature buffer (embargo)** — preventing backward-looking feature leakage
  32: # 8. **Nested walk-forward** — retuning across multiple test years
  33: # 9. **Combinatorial purged CV (CPCV)** — multiple backtest paths
  55: from ml4t.diagnostic.splitters import CombinatorialCV, WalkForwardCV
  56: from ml4t.diagnostic.splitters.config import WalkForwardConfig
  102: def plot_splits(splits, dates, *, title="", figsize=(12, 3.5)):
  112: # Detect purge gap (more than 1 index between train end and val start)
  279: # We use `WalkForwardCV` from `ml4t.diagnostic.splitters` to generate the
  288: cv_exp = WalkForwardCV(n_splits=5, test_size=252, expanding=True)
  304: cv_roll =
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/06_strategy_definition/exploration.md</path>
<type>file</type>
<content>
1: # Chapter 5: Strategy Definition - Codebase Analysis
2: 
3: **Generated**: 2026-01-25
4: **Analysis Type**: Deep Architecture & Pattern Review
5: 
6: ---
7: 
8: ## Executive Summary
9: 
10: Chapter 5 is a **mature, well-architected** educational codebase demonstrating strategy pre-specification. The code quality is high with consistent patterns, strong documentation, and proper separation of concerns. The architecture follows a **hypothesis-driven exploration** pattern rather than a production trading system pattern.
11: 
12: **Overall Quality**: ★★★★☆ (4/5) - Publication-ready with minor improvements possible
13: 
14: ---
15: 
16: ## Architecture Overview
17: 
18: ```
19: 06_stra
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/01_process_is_edge/factor_regimes.py</path>
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
17: # # Factor-Based Regime Detection
18: #
19: # **Chapter 1 · §1.4 Market Regimes: Change Is the Constant**
20: #
21: # **Docker image**: `ml4t`
22: #
23: # ## Purpose
24: #
25: # Demonstrates unsupervised learning for market regime detection using Gaussian Mixture Models (GMM)
26: # on factor returns
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py</path>
<type>file</type>
<content>
1: """Specification and hashing helpers for the experiment registry."""
2: 
3: from __future__ import annotations
4: 
5: import copy
6: import hashlib
7: import json
8: import logging
9: import math
10: import os
11: from collections.abc import Mapping, Sequence
12: from enum import Enum
13: from pathlib import Path
14: from typing import Any
15: 
16: logger = logging.getLogger(__name__)
17: 
18: # Default seed — must match utils.modeling.RANDOM_SEED.
19: # Duplicated here to avoid importing the full modeling stack (torch, etc.)
20: # into a lightweight registry module.
21: DEFAULT_SEED = 42
22: 
23: # Required fields in every training spec.  ``seed`` is enforced so that
24: # two run
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:58Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/etfs/config/setup.yaml"})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py", "pattern": "^def |^class |quantile|turnover|break_even|breakeven|feasib|IC|ic_|monoton|spread", "head_limit": 80})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/08_causal_sanity_checks.py", "pattern": "^def |^class |permutation|placebo|confound|DAG|backdoor|falsif|mechanism|refut", "head_limit": 80})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/research/decisions.py", "pattern": "^class |^def |@dataclass|holdout|lock|seal|Decision", "head_limit": 80})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/scripts/pre_run_gate.py"})`


> [reasoning] I have a lot. Let me now read the exploration.md is an old analysis. But I need the actual 06 evidence boundary. Let me look at the 06 README again (done) and chapter_06.md sections 6.5 and 6.7. But more concrete: check `case_studies/research/selection_field.py`, `decisions.py`, `workspace.py` (activation tiers), `scripts/pre_run_gate.py`, `scripts/create_experiment.py`, and `docs/running-notebooks.md`. Also the tests around leakage detectors. And 07 signal evaluation + causal sanity checks + ic inference.

Let me look for the "sealed holdout" / lock mechanism, which is key. Search for "holdout" lock, "sealed". Also the "evidence boundary" is likely in chapter 6. Let me grep chapter_06.md for key terms. But the request wants concrete file paths and symbols.

Key things still needed:
1. utils walk-forward done; purged/embargo done. Combinatorial in library; CPCV in 06 notebook via CombinatorialCV.
2. 01_process_is_edge: evidence boundary - probably chapter text plus `case_studies/research` workspace tiers. Need regime detection - factor_regimes.py (GMM). Also macro_regimes.
3. 06: trading protocol spec, universe rules, decision schedule, cost model, evaluation protocol, run logging. Setup.yaml is key. Let me read a setup.yaml.
4. 07: labels done partly; IC/quantile feasibility screens (05_signal_evaluation.py); multiple testing done; causal plausibility (08).
5. run log done.
6. notebook structure done via copilot-instructions; need jupytext sync script + verified-notebooks.

Let me read setup.yaml, 05_signal_evaluation, 08_causal_sanity_checks (grep functions), decisions.py, selection_field.py, and workspace.py. Also scripts/pre_run_gate.py.
Now configuration schema, signal feasibility screens, causal checks, and the holdout lock / activation tier.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/etfs/config/setup.yaml</path>
<type>file</type>
<content>
1: strategy_id: etfs
2: setup_version: v1
3: 
4: universe:
5:   assets:
6:     - ACWI
7:     - ACWX
8:     - AGG
9:     - BIL
10:     - BND
11:     - BNDX
12:     - DBA
13:     - DBC
14:     - DIA
15:     - DVY
16:     - EEM
17:     - EFA
18:     - EMB
19:     - EWA
20:     - EWC
21:     - EWG
22:     - EWH
23:     - EWI
24:     - EWJ
25:     - EWL
26:     - EWN
27:     - EWP
28:     - EWQ
29:     - EWT
30:     - EWU
31:     - EWW
32:     - EWY
33:     - EWZ
34:     - EZA
35:     - FXB
36:     - FXE
37:     - FXI
38:     - FXY
39:     - GLD
40:     - GOVT
41:     - GSG
42:     - HYG
43:     - IAU
44:     - IBB
45:     - IEF
46:     - IEFA
47:     - IEMG
48:     - IJR
49:     - INDA
50:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 80 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py
  17: # # Signal Evaluation: IC, Quantiles, and Spreads
  27: # (IC) analysis, quantile returns, and spread metrics. We answer: "Is this factor
  32: # 1. Compute cross-sectional IC and understand its time series properties
  33: # 2. Interpret IC, ICIR, and HAC-adjusted significance
  34: # 3. Analyze quantile returns, spread, and monotonicity
  36: # 5. Measure turnover and signal half-life
  46: #   underpin fold-aware IC evaluation in §7.
  51: """Signal Evaluation - IC analysis, quintile spreads, and classification diagnostics for alpha signals."""
  233: # ## 3. Information Coefficient (IC) Analysis
  235: # IC measures the **cross-s
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 80 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/08_causal_sanity_checks.py
  26: # This notebook implements **lightweight falsification tests** for feature evaluation.
  28: # whether a feature-outcome association is *consistent* with a proposed mechanism.
  31: # diagnostics guided by mechanism reasoning, testing one feature-outcome pair at
  32: # a time. They cannot detect multivariate confounding. Formal causal
  56: # 2. State a proposed mechanism using DAG vocabulary (confounder, mediator, collider)
  57: # 3. Implement timing placebos (shift features, examine IC half-life)
  99: # A permutation test cannot resolve a p-value finer than 1/(B+1). At B=200 that
  120: # and two are selected for the mechanis
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 9 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/research/decisions.py
  32: @dataclass(frozen=True)
  33: class StateTransitionPolicy:
  43: def _decision_entity_key(decisions: pl.DataFrame) -> str:
  50: def _validate_frame(kind: str, decisions: pl.DataFrame) -> tuple[str, ...]:
  132: def _validate_promotion(
  166: @dataclass(frozen=True)
  167: class DecisionArtifact:
  191: ) -> DecisionArtifact:
  283: def open(cls, study: Study, decision_hash: str) -> DecisionArtifact:
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/scripts/pre_run_gate.py</path>
<type>file</type>
<content>
1: """Everything that must be true before an expensive model run starts.
2: 
3: A canonical model run costs hours. Discovering afterwards that it recorded no runtime, or that
4: the same configuration would have resolved to a different identity on another code path, means
5: paying for it twice. This script states those conditions as executable checks and exits non-zero
6: if any of them fails, so "we verified the preconditions" is something you can see rather than
7: something someone remembers to do.
8: 
9: The substantive checks run a real reduced population end to end in a throwaway workspace and then
10: interrogate what it wrote. A check that reads the source and concludes the code looks rig
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:04Z

- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/research", "pattern": "lock|seal|confirm|explor|holdout", "include": "*.py", "head_limit": 60})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py", "pattern": "turnover|half.life|break|cashflow|feasib|capacity|monoton|spread|cost", "head_limit": 50})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/tests/test_holdout_boundary.py"})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/06_strategy_definition/chapter_06.md", "pattern": "evidence boundary|exploration|confirmation|sealed|trial|run log|nested|combinatorial", "head_limit": 50})`


> [reasoning] Now I need to look at the "evidence boundary" / exploration vs confirmation and the sealed holdout lock. The RUN_LOG mentions "the lock that permits the holdout to be scored once". And the Chapter 6 exploration.md is stale (references Ch5). But the actual mechanisms likely in `case_studies/research/workspace.py`, `selection_field.py`, `decisions.py`, `models.py`, `tests/test_holdout_boundary.py`, `test_holdout_cv_derivation.py`. Let me read workspace.py and selection_field.py, and grep for "lock" / "seal" / "confirm". Also the 06 chapter section 6.5/6.7 text. And check `docs/running-notebooks.md` for the workflow.

Also need `05_signal_evaluation` feasibility screen details (turnover, break-even). Let me grep more specifically for those symbols. And `06_ic_inference` for HAC/block bootstrap.

Let me batch:
- read workspace.py
- grep "lock|seal|confirm|explor" in case_studies/research and registry
- grep chapter_06.md for §6.5/6.7 key terms
- grep 05_signal_evaluation for turnover/breakeven/feasibility functions
- grep tests/test_holdout_boundary.py
- read docs/running-notebooks.md maybe too long; grep.
Now the holdout lock / evidence boundary and feasibility screens.

  <details><summary>tool output</summary>

  ```text
Found 60 match(es) in 7 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/case_studies/research/recovery.py
  22: for block in iter(lambda: source.read(1024 * 1024), b""):
  23: digest.update(block)

/home/georg/projects/ml4t-zh/case_studies/research/cv.py
  49: def require_fold_scoped_temporal_holdout_coverage(
  57: """Require an existing temporal fold to cover the holdout's training and evaluation windows.
  60: the requested geometry. For a holdout that question has no good answer. The holdout fold is
  61: derived when the lock is taken, so the artifact - built during stage 04, before any lock -
  62: never declares it, and the artifact cannot be rebuilt to add it: the lock pins the feature
  64: under. Compatibility therefore refuses every holdout lock on a c
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 50 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py
  27: # (IC) analysis, quantile returns, and spread metrics. We answer: "Is this factor
  34: # 3. Analyze quantile returns, spread, and monotonicity
  36: # 5. Measure turnover and signal half-life
  51: """Signal Evaluation - IC analysis, quintile spreads, and classification diagnostics for alpha signals."""
  364: # | 0.02 – 0.04 | Detectable on 5–10 year samples with the dispersions seen in published studies; net P&L is a separate cost question. |
  467: # Examine returns by signal quantile to assess **monotonicity** (do higher signal
  468: # values lead to higher returns?) and **spread** (what's the return difference
  527: # Spread 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/tests/test_holdout_boundary.py</path>
<type>file</type>
<content>
1: """Gate: feature-selection notebooks must scope development analysis pre-holdout.
2: 
3: Feature selection, robustness sweeps, and feature evaluation are development
4: decisions; the sealed holdout (``case_studies/etfs/config/setup.yaml`` ->
5: ``evaluation.holdout_start``) must not inform them (the rule taught in
6: ``06_strategy_definition/02_cv_foundations``). Regenerating the selection
7: artifacts requires the full data downloads, so this test statically checks the
8: notebook sources instead: each must read the holdout boundary from
9: ``setup.yaml`` and apply the holdout filter *before* its first IC computation.
10: """
11: 
12: from __future__ import annotations
13: 
14: import 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 17 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/06_strategy_definition/chapter_06.md
  14: - **Keep search countable and recoverable** using automatic run logging and a simple trial taxonomy.
  46: 3. **Evaluate under a time-series protocol**. Compare candidates using time-aware validation and reserve a holdout test set for confirmation once the pipeline is stable. This is where we prevent leakage and selection bias from dominating conclusions.
  364: - **Features look backward**: A 20-day momentum feature uses data from the past 20 days. If training *follows* validation (as in k-fold or combinatorial schemes; see Combinatorial methods and path dependence below), a training observation immediately after the validation period computes features using prices from the validation 
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:09Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/workspace.py", "limit": 140})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/__init__.py"})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py", "pattern": "^def |^class |def register|official_population|population", "head_limit": 50})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/scripts/sync_notebooks.py", "limit": 80})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py", "pattern": "deflated_sharpe|compute_pbo|CombinatorialCV|CPCV|pbo|dsr|n_trials|min_trl", "head_limit": 40})`


> [reasoning] I have very comprehensive information. Let me get a few more specifics:

1. The `case_studies/research/workspace.py` for ExecutionTier (preview/canonical) and activation. And the `Study` class.
2. The `decisions.py` DecisionArtifact for trading protocol specification.
3. The 06 section on trading setup / baseline checkpoint details maybe in chapter. But I have enough.
4. Notebook structure: jupytext metadata, provenance stamp, sync_notebooks.py. Let me quickly check scripts/sync_notebooks.py and .verified-notebooks.tsv, and the jupytext config in pyproject.
5. The DSR/CPCV in 16_strategy_simulation/12_dsr_validation.py and 11_ml_pipeline/04_nested_cv_hpo.py.

Let me batch these. Also `case_studies/research/__init__.py` to list exported API. And `selection_field.py`.

Let me prioritize. Given the huge context, I should be efficient. Let me read the key remaining pieces.
Final pieces: workspace tiers, run-log registration API, notebook sync/provenance, and DSR/CPCV validation.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/workspace.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: import hashlib
4: import json
5: import os
6: import shutil
7: import subprocess
8: import uuid
9: from dataclasses import dataclass
10: from datetime import UTC, datetime
11: from pathlib import Path
12: from typing import TYPE_CHECKING
13: 
14: from scripts.create_experiment import create_experiment
15: from utils.paths import REPO_ROOT
16: 
17: from .contracts import ExecutionTier
18: 
19: if TYPE_CHECKING:
20:     from .catalog import BacktestCatalog, PredictionCatalog
21:     from .causal import CausalRequest
22:     from .labels import LabelCatalog
23:     from .models import ModelRequest
24:     from .recovery import ExecutionLedger
25
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/__init__.py</path>
<type>file</type>
<content>
1: from .adapters import AdapterBinding, get_adapter, register_adapter, registered_adapters
2: from .catalog import BacktestCatalog, PredictionCatalog, prediction_rows_at
3: from .causal import (
4:     CausalRequest,
5:     CausalResult,
6:     ResolvedCausalRequest,
7:     causal_supersedes,
8:     supersedes_for,
9: )
10: from .comparison import CandidateSet, candidate_set_supersedes
11: from .configs import (
12:     declared_labels,
13:     load_model_configs,
14:     model_requests,
15:     narrows_declared_catalog,
16:     planned_model_plan,
17:     primary_label,
18:     resolved_model_plan,
19:     sweep_labels,
20: )
21: from .contracts import ExecutionTier
22: from .cv import
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 28 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py
  52: def _atomic_save_json(path: Path, data: dict) -> None:
  61: def _sampling_reduced(spec_json: str | None) -> bool:
  88: def _validate_prediction_dispersion(predictions, *, refuse: bool = True) -> None:
  92: production registries, the largest fold below the failure population was
  188: def clear_prediction_sets(
  287: def register_training_run(
  464: def record_training_runtime(
  528: def register_epoch_checkpoint(
  576: family-specific field population.
  733: def _declared_label_buffer(case_study: str, label: str | None) -> str | None:
  745: def _sibling_direction_labels(case_study: str, case_dir, label: str | None):
  779: def register_prediction_set(
  1084: def _has_f
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/scripts/sync_notebooks.py</path>
<type>file</type>
<content>
1: """Sync paired Jupyter notebooks (.ipynb) from their Jupytext .py sources.
2: 
3: The repository stores notebooks in Jupytext percent format: the `.py` file is
4: the source of truth, the `.ipynb` is a generated artifact. If a reviewer opens
5: an `.ipynb` and finds it out of date relative to the `.py`, they can run this
6: script to regenerate every `.ipynb` from its paired `.py`.
7: 
8: Usage (from the repo root):
9:     uv run python scripts/sync_notebooks.py            # forward sync (.py → .ipynb)
10:     uv run python scripts/sync_notebooks.py --check    # report drift only
11:     uv run python scripts/sync_notebooks.py --safe-only  # sync only doc-only drift
12:     uv run python scri
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 40 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py
  55: compute_pbo,
  56: deflated_sharpe_ratio_from_statistics,
  107: def _expected_max_sharpe(variance_trials: float, n_trials: int) -> float:
  109: if n_trials <= 1 or variance_trials <= 0:
  111: z1 = stats.norm.ppf(1.0 - (1.0 / n_trials))
  112: z2 = stats.norm.ppf(1.0 - (np.exp(-1.0) / n_trials))
  122: def _format_dsr_result(
  133: "dsr": probability,
  152: def deflated_sharpe_ratio(
  157: n_trials: int = 1,
  168: expected_max = _expected_max_sharpe(variance_native, n_trials)
  173: components = _format_dsr_result(
  205: local_probability = deflated_sharpe_ratio(
  210: n_trials=check_trials,
  214: library_result = deflated_sharpe_rati
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:14Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/decisions.py", "limit": 200})`
- **tool**: `grep({"head_limit": 60, "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/06_strategy_definition/01_where_ideas_come_from.py", "pattern": "SLOW|WRONG|RISK|def |classification|quintile|era|stress|turnover|footprint|feasib"})`
- **tool**: `grep({"head_limit": 40, "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py", "pattern": "evaluation|cadence|cost|universe|protocol|holdout|def "})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/research/selection_field.py", "pattern": "^class |^def |\"\"\"|FIELD_STAGES|attest|sweep|plan", "head_limit": 50})`


> [reasoning] I now have enough for all six areas. Let me also grab the `decisions.py` DecisionArtifact and `selection_field.py` briefly to describe the selection/sweep attestation. Also `06_strategy_definition/03_case_study_overview.py` has the evaluation protocol table. And the `06_strategy_definition/01_where_ideas_come_from.py` has SLOW/WRONG/RISK taxonomy and feasibility screen. Let me grep those quickly. Also the causal.py embargo function.

Let me do one final batch to nail down:
- decisions.py lines 1-200 (DecisionArtifact spec)
- 06/01_where_ideas_come_from.py key functions (SLOW/WRONG/RISK, quintile sort, era stress, turnover)
- selection_field.py purpose
- scripts/create_experiment.py

Given token budget, let me read the most important two: decisions.py head, and grep 01_where_ideas_come_from. Also 03_case_study_overview.
One more batch to pin the trading-protocol spec and idea-feasibility taxonomy.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/research/decisions.py</path>
<type>file</type>
<content>
1: from __future__ import annotations
2: 
3: import json
4: import math
5: import os
6: import sqlite3
7: import uuid
8: from dataclasses import asdict, dataclass
9: from importlib.util import find_spec
10: from pathlib import Path
11: from typing import TYPE_CHECKING, Any, Literal
12: 
13: import polars as pl
14: 
15: from case_studies.utils.artifact_digest import value_digest
16: from case_studies.utils.registry.specs import (
17:     IDENTITY_VERSION,
18:     canonical_json,
19:     canonical_value,
20:     compute_hash,
21: )
22: from case_studies.utils.registry.store import _open_registry, _utc_now
23: 
24: if TYPE_CHECKING:
25:     from .workspace import Study
26: 
27: from .resul
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 54 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/06_strategy_definition/01_where_ideas_come_from.py
  23: # footprint in the data. This is the exploratory step that sits between a *story*
  37: # - **SLOW**: macro information diffuses across siloed markets with a lag; capital
  39: # - **WRONG**: investors under-react to news and chase performance, extending trends
  42: # So this is a SLOW/WRONG blend. That also tells us the failure mode in advance:
  51: # - Run the **quintile conditional-return sort** and read it for *monotonicity,
  53: # - Stress the result by **era** — the difference between a footprint and an artifact.
  65: """Cross-asset momentum EDA — from a story to a measured footprint."""
  78: N_QUANTILES = 5  # quintiles
  109: # ago*. Skipping the most recent m
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 40 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py
  26: # - **What datasets we cover**: Asset classes, universes, and time periods
  28: # - **Evaluation protocols**: Walk-forward configurations and holdout policies
  29: # - **Prediction coverage**: Calendar-year spans for training, validation, and holdout
  34: # the trading setup, universe, evaluation protocol, and cost model.
  51: # the slate main series, validation the amber highlight, the sealed holdout a muted neutral.
  66: # Each case study's `config/setup.yaml` defines the trading setup, universe,
  67: # evaluation protocol, and cost model. We load all available configs and build
  98: def _fmt_window(value: Any) -> Any:
  99: """N
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 50 match(es) in 1 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/case_studies/research/selection_field.py
  1: """The field a holdout selection is made over, built one way for every reader of it.
  20: """
  33: from .configs import sweep_labels
  42: FIELD_STAGES: tuple[str, ...] = ("signal", "allocation", "risk_overlay")
  46: #: Reaching it is a floor, not a completion check - what says the baseline sweep finished is
  47: #: its plan, the same as every stage after it.
  52: class SelectionField:
  53: """What a holdout selection may choose from, and what it chose."""
  64: """Whether this came from a recorded candidate set rather than a live ranking."""
  68: def _recorded_set_count(registry: Any, name: str) -> int:
  69: """How many generations of ``n
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:18Z

- **tool**: `grep({"head_limit": 30, "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/pyproject.toml", "pattern": "ml4t-diagnostic|ml4t\\.diagnostic|ml4t-engineer|ml4t-data"})`
- **tool**: `grep({"head_limit": 20, "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/utils/causal.py", "pattern": "^def embargo_from_buffer|^def observation_step"})`


> [reasoning] I now have a thorough understanding. Let me compose the structured report. The user wants concrete file paths, function/class names, mechanisms. I should be technical and dense. Let me organize by the 6 areas.

Let me double check one thing: the `CombinatorialCV` import is from ml4t-diagnostic library, not implemented in repo. The purged/embargoed walk-forward is delegated to ml4t.diagnostic.splitters.WalkForwardCV. So the repo's own implementation is `utils/cv_splits.py` wrapping it, plus `_purge_holdout_touching_validation`. Good.

Also `06_strategy_definition/02_cv_foundations.py` imports `CombinatorialCV, WalkForwardCV` and demonstrates them. That's teaching, not infrastructure.

Now let me note the "evidence boundary" mechanisms concretely:
- `evaluation.holdout_start`/`holdout_end` in setup.yaml = sealed holdout
- `tests/test_holdout_boundary.py` static AST gate: holdout filter must precede first IC computation; label-endpoint purge `_label_end`; reconstruction seal `assert_values_agree`
- `case_studies/research/holdout.py` build_holdout_cv / build_holdout_training_spec / widest_label_buffer - derives the single holdout fold, trains on everything before seal minus widest label buffer
- `case_studies/research/models.py::locked_holdout_split`, `reconstruct_locked_model_request`, `validate_locked_model_run`
- registry "lock that permits the holdout to be scored once" (mentioned RUN_LOG)
- `case_studies/research/selection_field.py` - what holdout selection may choose from
- Experiment tier: `ExecutionTier` PREVIEW vs CANONICAL; preview barred from populations (population.py:211)
- Provenance not in hash: git commit, notebook, timestamps

Run log mechanism:
- `case_studies/utils/registry/specs.py`: canonical_json, compute_hash, training_hash_from_spec, prediction_hash_from_parts, backtest_hash_from_parts, IDENTITY_VERSION=3, project_training_identity (what's in/out)
- `case_studies/utils/registry/registration.py`: register_training_run, register_prediction_set, register_prediction_metrics, register_fold_metrics, register_backtest_run, register_causal_run
- `case_studies/utils/registry/store.py` _open_registry, queries.py, metrics.py
- `RUN_LOG.md` schema
- `case_studies/research/execution.py` run_model_population, populations
- `case_studies/research/population.py` OfficialPopulation, immutable named list

Notebook structure:
- Jupytext percent .py source of truth; .ipynb generated via scripts/sync_notebooks.py; copilot-instructions
- metadata.ml4t_provenance stamped production re-execution; `.verified-notebooks.tsv`
- `.github/scripts/notebook_provenance.py` stamp
- tests via Papermill with `# %% tags=["parameters"]` production defaults; no test branches; ML4T_OUTPUT_DIR isolation
- set_global_seeds in utils/reproducibility.py

01 process is edge:
- README learning objectives: evidence boundary, regime
- factor_regimes.py: GmmFitResult, fit_gmm_grid (GMM on AQR), explicitly documents it is ex-post/descriptive and look-ahead if used as feature
- macro_regimes.py similar
- The actual evidence-boundary machinery lives in research/ and registry, not notebook.

06 strategy definition:
- setup.yaml schema: universe, decision (cadence/snapshot/execution_delay/cadence_by_label), execution, mapping, costs, labels (buffer/variants/rebalance_step), backtest.sweep, evaluation (n_splits/train_size/val_size/holdout/calendar), causal, features register, model_based
- `case_studies/research/strategy.py::Strategy` (resolve/run/identity), `apply_state_transition_policy`, warmup
- `DecisionArtifact.publish` (decisions.py), `StateTransitionPolicy`
- `utils/cv_splits.py::CVSpec.walk_forward` / resolve in research/cv.py
- run logging in RUN_LOG.md / registry

07:
- Labels: `ml4t.engineer.labeling` functions: fixed_time_horizon_labels, rolling_percentile_binary_labels, triple_barrier_labels, atr_triple_barrier_labels, trend_scanning_labels, meta_labels, compute_bet_size, calculate_label_uniqueness, sequential_bootstrap; LabelingConfig
- `case_studies/research/labels.py` LabelDefinition/LabelRef; `utils/artifact_specs.resolve_label_buffer/resolve_label_horizon`
- 05 signal evaluation: cross_sectional_ic / pooled_ic, result.ic, ic_ir, ic_t_stat, spread, monotonicity, turnover, half_life, break-even cost analysis
- 06_ic_inference: compute_ic_hac_stats, block bootstrap, label_horizon
- 07 multiple testing: benjamini_hochberg_fdr, holm_bonferroni, rademacher_complexity, ras_ic_adjustment, deflated_sharpe_ratio, compute_pbo, compute_min_trl, min_trl_fwer, multiple_testing_summary
- 08 causal: block_permutation_null, compute_cross_sectional_ic, run_timing_placebo, run_shared_driver_check, run_regime_heterogeneity; DAG vocabulary
- DSR validation 16/12: deflated_sharpe_ratio, deflated_sharpe_ratio_from_statistics, compute_pbo
- 15 causal: DML, refutation p-value; registry causal_runs table

I should include specific paths as absolute. Let me write it up. Keep it structured, technical, skip plotting code. I'll note the ml4t-diagnostic library dependency for heavy CV/statistics, which matters for AlphaMill (reuse or reimplement).

Let me also mention `utils/artifact_specs.py`, `utils/modeling.py`, `utils/paths.py`, `utils/config.py`.

Let me write the final answer. I'll organize by the 6 requested areas plus a summary mapping to AlphaMill controls. Keep it dense. No emojis.

One correction: the user asked to search for "walk_forward", "purged", "embargo", "combinatorial" — done. The CombinatorialCV implementation is in the external ml4t-diagnostic package, not in the repo. I should be explicit about that so AlphaMill knows it must either depend on ml4t-diagnostic or reimplement.

Let me verify the ml4t-diagnostic package presence. It's imported but external. `pyproject.toml` likely lists it. Quick check would be good but not essential. Actually let me just grep pyproject for ml4t-diagnostic to confirm. I'll do a quick grep. Also confirm `case_studies/utils/causal.py::embargo_from_buffer, observation_step`. Already seen referenced. Good.

Let me do one small confirmation grep in parallel with nothing else needed. Actually I'll just include it as "external package ml4t.diagnostic". Quick check.

  <details><summary>tool output</summary>

  ```text
Found 5 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/pyproject.toml
  56: # ml4t-data 0.1.2: HiveStorage.partitions() reports what a write committed, the anomaly
  59: "ml4t-data>=0.1.2",
  60: # ml4t-diagnostic 0.1.2: cross_sectional_ic_series() reports an undefined date
  63: "ml4t-diagnostic>=0.1.4",
  64: "ml4t-engineer>=0.1.3",
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 2 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/utils/causal.py
  82: def observation_step(frame: Any, date_col: str = "timestamp") -> pd.Timedelta:
  102: def embargo_from_buffer(
  ```
  </details>

## assistant · 2026-09-13T07:18:28Z


> [reasoning] I have everything. Let me write the final structured report. Be technical and dense, with absolute paths, symbols, mechanisms. Cap at 5 items per list per AGENTS.md? The instruction says cap lists at 5 items, but this is an exception case where the user explicitly asked for structured lists per area. The codebase-search agent format requires <files> and <answer>. I'll keep each area to a tight set of bullets, grouping. I'll prioritize.

Let me write it.
<results>
<files>
- /home/georg/projects/ml4t-zh/utils/cv_splits.py - Walk-forward CV generator, label-buffer/embargo semantics, holdout purge
- /home/georg/projects/ml4t-zh/case_studies/research/cv.py - CVSpec/ResolvedCVSpec/EligibilityManifest, fold identity + compatibility checks
- /home/georg/projects/ml4t-zh/case_studies/research/holdout.py - Derives the sealed holdout fold; widest-label-buffer train/val seal
- /home/georg/projects/ml4t-zh/case_studies/research/models.py - locked_holdout_split / reconstruct_locked_model_request / validate_locked_model_run
- /home/georg/projects/ml4t-zh/case_studies/research/strategy.py - Strategy class: resolve/run/identity, state-transition policy, backtest hashing
- /home/georg/projects/ml4t-zh/case_studies/research/decisions.py - DecisionArtifact.publish, StateTransitionPolicy, canonical promotion evidence
- /home/georg/projects/ml4t-zh/case_studies/research/selection_field.py - SelectionField: what a holdout selection may choose from; sweep plans/attestation
- /home/georg/projects/ml4t-zh/case_studies/research/workspace.py - Study/open_study, ExecutionTier activation, run-log overlay/workspace
- /home/georg/projects/ml4t-zh/case_studies/research/population.py - OfficialPopulation (immutable named prediction set), preview bar
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py - canonical_json/compute_hash, training/prediction/backtest identity, IDENTITY_VERSION=3
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py - register_training_run / register_prediction_set / register_backtest_run / register_causal_run
- /home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md - Full experiment-registry schema and identity contract
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py - BH-FDR, Holm, RAS/Rademacher, DSR, PBO, MinTRL
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py - IC/ICIR, quantile spread/monotonicity, turnover, half-life, break-even cost
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/06_ic_inference.py - HAC IC inference + block bootstrap
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/08_causal_sanity_checks.py - Timing placebo, shared-driver check, block-permutation null, regime heterogeneity
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py - Fixed-horizon, triple-barrier, ATR, trend-scanning, meta-labels, uniqueness
- /home/georg/projects/ml4t-zh/tests/test_holdout_boundary.py - Static AST gates that enforce the holdout seal in notebooks
- /home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py - WalkForwardCV/CombinatorialCV pedagogy: purge vs embargo, nested WF, CPCV
- /home/georg/projects/ml4t-zh/06_strategy_definition/01_where_ideas_come_from.py - SLOW/WRONG/RISK edge taxonomy, quintile sort, era stress, turnover screen
- /home/georg/projects/ml4t-zh/scripts/pre_run_gate.py - Pre-flight gate: identity agreement, fold prep, reduced end-to-end run
- /home/georg/projects/ml4t-zh/scripts/sync_notebooks.py - Jupytext .py -> .ipynb drift detection/sync
- /home/georg/projects/ml4t-zh/01_process_is_edge/factor_regimes.py - GMM regime detection (explicitly ex-post, documentedly look-ahead if used predictively)
</files>

<answer>
## 1. Shared config, paths, and cross-validation (utils/)

**Config/paths.** `/home/georg/projects/ml4t-zh/utils/config.py` is fail-fast: it loads `.env`, resolves `ML4T_PATH`, `ML4T_DATA_PATH`, `CASE_STUDIES_DIR`, and raises `FileNotFoundError` if a path is missing (no silent fallbacks). `/home/georg/projects/ml4t-zh/utils/paths.py` holds the chapter registry and `get_case_study_dir`/`get_output_dir`, so notebooks never hard-code locations. Output isolation is via `ML4T_OUTPUT_DIR`.

**Walk-forward / purge / embargo.** The repo does not reimplement these; it wraps the external package `ml4t-diagnostic>=0.1.4` (declared in `/home/georg/projects/ml4t-zh/pyproject.toml`). The real control point is `/home/georg/projects/ml4t-zh/utils/cv_splits.py`:
- `generate_cv_splits(dataset, case_study_id/setup_path/cv_config, label_buffer, outcome_horizon, buffer_unit)` delegates fold generation to `ml4t.diagnostic.splitters.WalkForwardCV` with `fold_direction="backward"`.
- `make_walk_forward_config` / `make_wf_config` bridge `setup.yaml`'s `evaluation` block into the library's `WalkForwardConfig` (`val_size->test_size`, `holdout_start->test_start`).
- `_purge_holdout_touching_validation(...)` excludes validation signal dates whose forward label reaches into the holdout, counting in **sessions** (int) when a calendar exists, not calendar days.
- `_horizon_for_config` / `normalize_label_buffer` / `resolve_label_buffer_unit` convert `"21D"` into an integer session count for session-gridded panels; the label declares whether its buffer is `sessions` or `calendar`.
- `_assert_chronological` hard-fails if folds are not oldest-first with ids `0..n-1`. `most_recent_split` and `earliest_train_start` read boundaries, not list positions.
- `read` of CV request is `/home/georg/projects/ml4t-zh/case_studies/research/cv.py`: `CVSpec.walk_forward(...)` -> `resolve()` returns `ResolvedCVSpec` with a content hash; `EligibilityManifest.resolve(...)` records `(symbol, timestamp, fold)` plus a per-fold `sorted_key_digest`. `require_fold_scoped_temporal_compatibility` and `require_fold_scoped_temporal_holdout_coverage` refuse reuse of an artifact under different fold geometry.

**Purge vs embargo semantics** (taught in `/home/georg/projects/ml4t-zh/06_strategy_definition/02_cv_foundations.py`): label buffer = forward-looking purge (always needed); feature buffer = backward-looking embargo (needed in CPCV/k-fold where training follows validation). It imports `WalkForwardCV` and `CombinatorialCV` and shows `CombinatorialCV(n_groups=6, n_test_groups=2, label_horizon=5, embargo_size=2)`; nested walk-forward is built by an explicit outer 2-fold x inner 5-fold loop. The repo's own enforcement of these values is `case_studies/research/holdout.py` and `utils/cv_splits.py`; the actual splitter algorithm lives in the dependency.

## 2. 01_process_is_edge: workflow concept, evidence boundary, regimes

The chapter README (`/home/georg/projects/ml4t-zh/01_process_is_edge/README.md`) states the framework (point-in-time data infrastructure, scoping invariants, iterative modules, feedback loop) and defines the key concept: **"the evidence boundary between exploration and confirmation"** with trial logging, sealed holdouts, and selection-aware evaluation.

Concrete mechanisms (not prose): the boundary is implemented across `case_studies/research/` and the registry, not in this chapter's notebooks:
- Sealed holdout = `evaluation.holdout_start`/`holdout_end` in each `config/setup.yaml`, derived into a single holdout fold by `build_holdout_cv` (`case_studies/research/holdout.py`). Training ends `buffer_steps` observations before the seal; the buffer is the **widest** label buffer across `labels.primary`+`variants` (`widest_label_buffer`), counted on the panel's own cadence via `embargo_from_buffer`/`observation_step` (`case_studies/utils/causal.py`). `build_holdout_training_spec` re-keys the selected validation spec onto the holdout fold and recomputes `expected_prediction_keys`, `effective_params_by_fold`, etc.
- Execution lock: `case_studies/research/models.py::locked_holdout_split`, `reconstruct_locked_model_request`, `validate_locked_model_run` reconstruct and validate the fitted state from an immutable spec; `RUN_LOG.md` describes a registry lock that "permits the holdout to be scored once."
- Exploration vs confirmation isolation: `Study.activate(ExecutionTier.PREVIEW|CANONICAL)` (`case_studies/research/workspace.py`); preview writes under `.preview/` and `population.py` line ~211 refuses `"exploratory decision backtest ... cannot enter an official population"`. `scripts/pre_run_gate.py` runs a reduced preview end-to-end and inspects the registry before a canonical run.

Regime detection (`/home/georg/projects/ml4t-zh/01_process_is_edge/factor_regimes.py`): `GmmFitResult` dataclass and `fit_gmm_grid(x, n_components_list)` fit `sklearn.mixture.GaussianMixture` over AQR Century-of-Factor-Premia monthly factor returns, scoring BIC/AIC/silhouette. The notebook explicitly documents the scope: the scaler+GMM are fit on the entire history, so labels are **ex-post/descriptive only and would be look-ahead as predictors**; walk-forward regime construction is deferred to Ch6+. `macro_regimes.py` is the analogous FRED/SP500-volatility version. There is no regime state machine or live detector in this chapter.

## 3. 06_strategy_definition: protocol spec, universe, schedule, costs, evaluation, logging

The trading protocol is a versioned YAML, not a notebook. Canonical example: `/home/georg/projects/ml4t-zh/case_studies/etfs/config/setup.yaml`, schema sections:
- `universe`: explicit `assets`, `n_assets`, `eligibility_rule` (e.g. `point_in_time_adv_10m_annual`) plus `eligibility_file: eligibility.csv` (point-in-time membership to counter survivorship bias).
- `decision`: `cadence` (e.g. `monthly_month_end`), `snapshot: close`, `execution_delay: next_bar_open`, and `cadence_by_label` (per-label decision schedule so a 5d label isn't held on a 21d grid).
- `execution`: `initial_cash`, `share_type`, `allocator_lookback` (single source of truth for Ch16-19; changing it invalidates backtest hashes).
- `mapping`: `class: long_only_rank_and_rebalance`, `position_state_space`, `entry_logic: rank_selection_top_n`, `sizing: equal_weight`.
- `costs`: `class: material`, `model: per_share_plus_spread`, `per_share`, `asset_spreads`, `default_half_spread_usd`, `spread_convention: half_spread`, `source`.
- `labels`: `primary`, `buffer`, `variants`, `variant_buffers`, `rebalance_step` (thinning step so holding periods don't overlap).
- `backtest.sweep`: `top_n_predictions`, `checkpoints_per_config`, `top_k_grid`, `allocators`, `cost_grid_bps`, `cost_grid_half_spread_usd`, `risk_controls` (stop/trailing/time-exit grid). This is the declared search grid.
- `evaluation`: `n_splits`, `train_size`, `val_size`, `holdout_start`, `holdout_end`, `calendar: NYSE`, `periods_per_year`.
- `causal`, `features` (a **feature-specification register**: windows, ranked columns, regime threshold, state lookbacks, family pattern/role/hypothesis/lookback/lag/frame/representation/failure_mode), and `model_based` (HMM/GARCH burn-in, refit cadence, restarts).

Execution/reporting classes:
- `case_studies/research/strategy.py::Strategy` (frozen dataclass) enforces that predictions are complete, that `decision` declares exactly the selected prediction hash, and that the split is `validation|holdout`. `resolve()`/`run()` build a canonical strategy spec, compute `identity()`, and refuse if the backtest hash changes during execution (`raise RuntimeError`). `apply_state_transition_policy(...)` implements fold-boundary and temporal-gap resets (`continue|reset|liquidate`) with zero-weight flattening rows.
- `case_studies/research/decisions.py::DecisionArtifact.publish(...)` validates decision frames (`target_weights|target_positions|orders|short_straddles`), requires a `StateTransitionPolicy` for stateful kinds, and for canonical promotion requires `source_identity` evidence (`module`, `source_digest`, `declared_inputs`, `determinism`, `clean_replay_digest`).
- Case-study cross-comparison of protocol is in `/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py` (`_normalize_setup_yaml`, `load_setup_results`, protocol rows).

Run logging is covered in area 5.

## 4. 07_defining_the_learning_task: labels, feasibility screens, multiple testing, causal checks

**Labels.** `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py` is the canonical reference; it uses `ml4t.engineer.labeling`:
- `fixed_time_horizon_labels(df, horizon, method="returns|binary|log_returns")` for fwd returns.
- `LabelingConfig.triple_barrier(upper_barrier, lower_barrier, max_holding_period, side)` + `triple_barrier_labels(..., calculate_uniqueness=True)`; `atr_triple_barrier_labels` with ATR-based per-row barriers.
- `rolling_percentile_binary_labels` (time-series adaptive) and cross-sectional percentile labels built inline (rank over timestamp -> quintile).
- `trend_scanning_labels(min_window, max_window, step)` with an explicit **Bonferroni correction** over the number of horizons tested.
- `calculate_label_uniqueness`, `sequential_bootstrap`, `meta_labels`, `compute_bet_size`. The notebook measures effective sample size $N_{eff}=\sum w$ and the SE inflation $\sqrt{N/N_{eff}}$ from overlapping labels.
- In production these resolve through `case_studies/research/labels.py` (`LabelDefinition`, `LabelRef`) and `utils/artifact_specs.py::resolve_label_buffer` / `resolve_label_horizon`; the label's own spec artifact overrides `setup.yaml`.

**IC/quantile feasibility screen.** `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/05_signal_evaluation.py` and `06_ic_inference.py`. Symbols: `pooled_ic`, `cross_sectional_ic` (per-date Spearman; returns `ic_mean`, `ic_t`, `p_value`), `compute_ic_hac_stats(ics, label_horizon=H)` (HAC t on the overlapping daily IC series), plus `result.ic`, `result.ic_ir`, `result.ic_t_stat`, `result.spread`, `result.spread_t_stat`, `result.monotonicity`, `result.turnover`, `result.half_life`. Feasibility logic: mean daily IC vs its SE $\sigma_{IC}/\sqrt{T}$; ICIR; monotonicity of quantile returns; turnover; signal half-life (with sign-reversal caveat); and a **break-even cost analysis** comparing the 21D top-bottom spread against round-trip costs (`COST_ASSUMPTIONS["spread_bps"]`, `turnover_21d`). A Grinold net-IC approximation is used.

**Multiple-testing control.** `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/07_multiple_testing.py` imports from `ml4t.diagnostic.evaluation.stats`:
- `benjamini_hochberg_fdr(p_values, alpha, return_details=True)` (FDR; returns `rejected`, `adjusted_p_values`), `holm_bonferroni` (FWER).
- `rademacher_complexity` and `ras_ic_adjustment(observed_ic, complexity, n_samples, delta, kappa)`; the notebook carefully separates standardized vs IC-unit scales and uses a distribution-free `KAPPA=1.0` (Spearman support), reporting a data-dependent kappa only as sensitivity.
- `deflated_sharpe_ratio(strategy_returns, frequency)` (Bailey/Lopez de Prado), `compute_pbo(is_performance, oos_performance)` (combinatorial purged CV-based probability of backtest overfitting), `compute_min_trl` / `min_trl_fwer`, and `multiple_testing_summary`.
- Pipeline order: HAC p-values -> BH-FDR -> discoveries -> RAS if correlated; plus two-pass **exploration (80%) / confirmation (20%)** where promotion is by fold stability and BH runs on the reduced set.
- `/home/georg/projects/ml4t-zh/16_strategy_simulation/12_dsr_validation.py` re-implements/validates `deflated_sharpe_ratio`, `deflated_sharpe_ratio_from_statistics`, `_expected_max_sharpe(variance_trials, n_trials)`, and `compute_pbo` against the library; `/home/georg/projects/ml4t-zh/11_ml_pipeline/04_nested_cv_hpo.py` implements nested walk-forward HPO.

**Causal plausibility.** `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/08_causal_sanity_checks.py`: `block_permutation_null(df, feature_col, baseline_ic, seed, n_permutations)` (block permutation at the label horizon; p=(r+1)/(B+1) with stated resolution floor), `compute_cross_sectional_ic`, and reusable falsification functions `run_timing_placebo`, `run_shared_driver_check` (Treasury/common-driver control + permutation), `run_regime_heterogeneity`. It requires stating a mechanism first (confounder/mediator/collider DAG vocabulary) and warns that a failed check does not prove causation; formal DML is in Ch15 and recorded in the `causal_runs` registry table with `dml_effect`, `dml_se_hac`, `p_value_hac`, `naive_effect`, `confounding_bias_pct`, `refutation_p`.

## 5. Run log / experiment registry

`/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md` is the contract. Per case study, `run_log/` contains a SQLite index (`registry.db`) plus `training/`, `predictions/`, `backtest/`, `decisions/` artifact dirs.

Identity scheme (`case_studies/utils/registry/specs.py`):
- `canonical_json` (sorted keys, no whitespace, round-trip validated) and `compute_hash` = truncated SHA-256 to 12 chars. `IDENTITY_VERSION = 3`, `project_training_identity(spec)` defines exactly what enters identity: family, label, seed, execution_tier, and the resolved `computation` block (feature digests/columns, per-fold windows, per-fold estimator params, preprocessing, checkpoint schedule, `expected_prediction_keys` eligibility manifest, runner/library versions). Deliberately excluded (provenance only): notebook entry point, git commit, timestamps, runtime, `preset_path` (path-portability).
- `training_hash_from_spec`, `prediction_hash_from_parts(training_hash, checkpoint, split)`, `backtest_hash_from_parts(prediction_hash, strategy_spec)` form the three-level `training_run -> prediction_set -> backtest_run` graph; `identity_version` is itself hashed so scheme changes don't collide.
- Writer API in `case_studies/utils/registry/registration.py`: `register_training_run`, `record_training_runtime`, `register_epoch_checkpoint`, `register_prediction_set`, `register_prediction_metrics` (IC mean/std/t, HAC `ic_t_hac`+`ic_ci_lo/hi`, coverage counts), `register_fold_metrics`, `register_backtest_run`, `register_backtest_metrics`, `register_backtest_fold_metrics`, `register_paired_metrics`, `register_causal_run`; `_open_registry`/`store.py` handles migration and WAL.
- Population immutability: `case_studies/research/population.py::OfficialPopulation` and `execution.py::run_model_population(study, resolved, population_name=...)` write the full member list before the first fit and verify it after; re-defining a name raises. Re-running a notebook re-derives identities and returns the stored result instead of refitting (interrupt/resume per fold).
- Query API: `case_studies/utils/registry/queries.py` and metrics, re-exported via `case_studies/utils/registry/__init__.py` (`load_training_runs`, `load_prediction_sets`, `load_prediction_metrics`, `read_training_spec`, `read_predictions`, `read_backtest_returns`).
- README rule: `run_log/registry.db` is the **sole source of truth**; `results/*.json` is deprecated.

## 6. Notebook structure and reproducibility

- **Jupytext percent format**: every notebook is a paired `.py` + `.ipynb`; the `.py` (with `# %%` cells and a `jupytext:` header) is the source of truth, the `.ipynb` is generated. `/home/georg/projects/ml4t-zh/scripts/sync_notebooks.py` does content-based drift detection (`find_paired`, `ipynb_code_cells`) with `--check`/`--safe-only`; the `.github/copilot-instructions.md` states never hand-edit the `.ipynb`.
- **Provenance stamp**: committed `.ipynb` files are production re-executions stamped in `metadata.ml4t_provenance`; `.github/scripts/notebook_provenance.py stamp <nb> --executor <env> --production` and CI fails test-mode or stale stamps. `.verified-notebooks.tsv` tracks verified pairs. Output must carry no machine-specific absolute paths.
- **Reproducibility**: `/home/georg/projects/ml4t-zh/utils/reproducibility.py::set_global_seeds(seed=42)` seeds `random`, NumPy, Torch CPU+CUDA, and sets `PYTHONHASHSEED`; the seed is also an identity input (`specs.py` requires `seed`).
- **Tests**: Papermill parameter injection. Each notebook has a `# %% tags=["parameters"]` cell with production defaults; tests override via `tests/overrides.yaml` (no `if TEST:` branches; the same code path runs at reduced scale). `ML4T_OUTPUT_DIR` redirects all writes so production artifacts are never overwritten; `tests/fixtures/seed_results.py` seeds schema-correct registry/parquet fixtures.
- **Static discipline gates**: `/home/georg/projects/ml4t-zh/tests/test_holdout_boundary.py` parses notebook ASTs to require (a) a holdout-boundary comparison before the first IC computation, (b) label-endpoint purge `_label_end = shift(-horizon).over(symbol)` rather than a leaking signal-date filter, and (c) the reconstruction seal (`assert_values_agree`, rebuilding stage-03 features with the holdout withheld). This is the enforcement arm of the "evidence boundary."

## Mapping to AlphaMill's evaluation gate (what is borrowable)

1. **Content-addressed run log with a declared identity projection** (`specs.py::project_training_identity`, 12-char SHA-256, identity_version) is the single highest-value borrow: it makes trials countable (required for DSR/BH) and makes re-runs free/cacheable. AlphaMill should hash exactly the outcome-affecting computation and exclude provenance.
2. **Declared, machine-readable strategy protocol** (`config/setup.yaml`: universe eligibility, decision cadence per label, execution delay, costs, label buffers, sweep grid, evaluation windows) so evaluation is config-driven and hash-stable.
3. **Sealed holdout with a derived fold and a widest-label-buffer seal** (`holdout.py::build_holdout_cv`, `widest_label_buffer`, session-counted `embargo_from_buffer`) plus a one-shot lock and static/AST gate. AlphaMill's gate should refuse any selection artifact whose rows touch the holdout.
4. **Selection-aware multiple testing** on the actual trial count: HAC IC inference, BH-FDR/Holm, RAS for correlated variants, and DSR/PBO/MinTRL at the strategy level. Note the repo delegates CV splitters and much of the stats to `ml4t-diagnostic`; AlphaMill must either depend on it or reimplement `WalkForwardCV`/`CombinatorialCV` and `benjamini_hochberg_fdr`/`deflated_sharpe_ratio`.
5. **Exploration/confirmation phase split** (preview tier barred from official populations; two-pass IC screening; causal falsification before modeling) is the pattern that keeps the confirmatory count honest.
</answer>

<next_steps>
1. Decide whether AlphaMill will depend on `ml4t-diagnostic>=0.1.4` (fastest path to WalkForwardCV/CombinatorialCV/BH/DSR/PBO) or reimplement. This is the single blocking decision - the repo's CV/statistics are wrappers around that package, not local code.
2. If adopting, port two modules first: `case_studies/utils/registry/specs.py` (identity projection + hashing) and `utils/cv_splits.py` (session-counted label buffer + `_purge_holdout_touching_validation`).
3. Read `/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md` end to end before designing AlphaMill's evidence ledger; it is the only document that specifies the identity inclusion/exclusion contract.
</next_steps>
</results>
