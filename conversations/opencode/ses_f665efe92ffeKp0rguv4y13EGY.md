---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f665efe92ffeKp0rguv4y13EGY"
title: "ml4t case study structure (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-13T07:17:40Z"
updated_at: "2026-09-13T07:19:02Z"
tokens_input: 125207
tokens_output: 11307
cost: 0.0308
parent_id: "ses_f6664247effe4SLb37r5OF4RZ9"
---

# ml4t case study structure (@explore subagent)

## user · 2026-09-13T07:17:40Z

[CONTEXT] I am analyzing /home/georg/projects/ml4t-zh, the code for "Machine Learning for Trading, 3rd Edition". It contains nine case studies under case_studies/ that each carry one dataset through the SAME end-to-end pipeline. I am comparing against AlphaMill, a new AI-factor-factory-led crypto quant pipeline, and want to borrow the case-study organization and experiment-tracking design.

[GOAL] Describe precisely how ONE case study is structured end-to-end, using crypto_perps_funding (closest analog to crypto) as the primary example and comparing with one equity case study (us_equities_panel or etfs). I need directory layout, config files, stage-by-stage pipeline, and especially the run_log/registry.db experiment registry.

[DOWNSTREAM] I will recommend how AlphaMill should structure its own experiment tracking / artifact registry and its "run one pipeline across many datasets/markets" discipline.

[REQUEST] Investigate and report with concrete paths + schema:
1. case_studies/ top-level layout: what each case study folder contains (config, data, notebooks, run_log, results, models, artifacts).
2. The run_log/registry.db: what is it (SQLite?), its schema (tables/columns), what gets recorded per run (params, metrics, artifacts, git hash, timestamps?), and which code writes/reads it. Find the writer/reader functions.
3. How case studies share code: do they import the same library functions, or copy notebooks? Identify the shared modules.
4. crypto_perps_funding specifics: frequency (8-hourly), funding-rate arbitrage, feature/label construction, model, backtest, cost model.
5. Any configuration/registry that enumerates the nine case studies and their metadata.
6. How results/ differs from run_log/registry.db, and any docs saying registry.db is the source of truth.

Report structured: area -> mechanism, file paths, key symbols/schema. Be technical and concrete; skip plotting.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-13T07:17:40Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/case_studies"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 2 -name \"*.md\" -o -maxdepth 2 -name \"*.toml\" -o -maxdepth 2 -name \"*.yaml\" -o -maxdepth 2 -name \"*.yml\" | sort"})`
- **tool**: `glob({"pattern": "**/registry.db", "path": "/home/georg/projects/ml4t-zh"})`
- **tool**: `glob({"pattern": "**/*.{yaml,yml,toml}", "path": "/home/georg/projects/ml4t-zh/case_studies"})`


> [reasoning] Let me start by exploring the ml4t-zh directory structure. I'll launch parallel searches.

Note this is a different directory than the working directory. Let me investigate.

Let me start with parallel tool calls.
<analysis>
**Literal Request**: Map one ml4t-zh case study end-to-end, focusing on crypto_perps_funding vs an equities case, especially run_log/registry.db schema and writers/readers.

**Actual Need**: Extract a reusable experiment-tracking + artifact-registry + "one pipeline across many datasets" architecture to adapt into AlphaMill.

**Success Looks Like**: Absolute paths for directory layout, config files, shared libs, pipeline stages; exact SQLite schema of registry.db with columns and writer/reader symbols; crypto_perps_funding specifics (8h frequency, funding arb, labels, model, costs).
</analysis>

Launching parallel reconnaissance.

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
total 104
drwxr-xr-x 14 georg georg  4096 Sep 10 00:21 .
drwxr-xr-x 42 georg georg  4096 Sep 12 01:44 ..
-rw-r--r--  1 georg georg  4653 Sep 10 00:21 README.md
-rw-r--r--  1 georg georg 37630 Sep 10 00:21 RUN_LOG.md
-rw-r--r--  1 georg georg     0 Sep 10 00:21 __init__.py
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 cme_futures
drwxr-xr-x 21 georg georg  4096 Sep 10 00:21 config
drwxr-xr-x  5 georg georg  4096 Sep 10 00:21 crypto_perps_funding
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 etfs
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 fx_pairs
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 nasdaq100_microstructure
drwxr-xr-x  2 georg georg  4096 Sep 10 00:21 research
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 sp500_equity_option_analytics
drwxr-xr-x  4 georg georg  4096 Sep 10 00:21 sp50
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/.github/copilot-instructions.md
/home/georg/projects/ml4t-zh/.github/dependabot.yml
/home/georg/projects/ml4t-zh/.pre-commit-config.yaml
/home/georg/projects/ml4t-zh/01_process_is_edge/README.md
/home/georg/projects/ml4t-zh/01_process_is_edge/chapter_01.md
/home/georg/projects/ml4t-zh/01_process_is_edge/chapter_01_zh.md
/home/georg/projects/ml4t-zh/02_financial_data_universe/README.md
/home/georg/projects/ml4t-zh/02_financial_data_universe/chapter_02.md
/home/georg/projects/ml4t-zh/02_financial_data_universe/chapter_02_zh.md
/home/georg/projects/ml4t-zh/03_market_microstructure/README.md
/home/georg/projects/ml4t-zh/03_market_microstructure/chapter_03.md
/home/georg/projects/ml4t-zh/03_market_microstructure/chapter_03_zh.md
/home/georg/projects/ml4t-zh/04_funda
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 100 file(s)

/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/config/backtest/base.yaml
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/config/training/fwd_ret_5d.yaml
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/config/training/fwd_ret_1d.yaml
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/config/training/fwd_ret_21d.yaml
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/config/setup.yaml
/home/georg/projects/ml4t-zh/case_studies/sp500_options/config/backtest/base.yaml
/home/georg/projects/ml4t-zh/case_studies/sp500_options/config/training/fwd_ret_dh_10d.yaml
/home/georg/projects/ml4t-zh/case_studies/sp500_options/config/training/fwd_ret_5d.yaml
/home/georg/projects/ml4t-zh/case_studies/sp500_options/config/training/ret_to
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:44Z

- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding -type f | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/case_studies/us_equities_panel -type f | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/case_studies -iname \"*run_log*\" -o -iname \"*.db\" -o -iname \"*.sqlite*\" | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/case_studies -maxdepth 2 -type d | sort"})`
- **tool**: `grep({"pattern": "registry\\.db|run_log|registry", "path": "/home/georg/projects/ml4t-zh/case_studies", "output_mode": "files_with_matches"})`


> [reasoning] Let me dig into case_studies structure. No registry.db found in glob — maybe it's in run_log directory with different name, or .gitignored. Let me look.

Let me explore crypto_perps_funding, us_equities_panel, etfs directory trees, and find run_log.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/01_feasibility_analysis.ipynb
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/01_feasibility_analysis.py
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/02_labels.ipynb
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/02_labels.py
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/03_financial_features.ipynb
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/03_financial_features.py
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/04_model_based_features.ipynb
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/04_model_based_features.py
/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/05_evaluation.ipynb
/home/georg/proje
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/01_feasibility_analysis.ipynb
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/01_feasibility_analysis.py
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/02_labels.ipynb
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/02_labels.py
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/03_financial_features.ipynb
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/03_financial_features.py
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/04_model_based_features.ipynb
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/04_model_based_features.py
/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/05_evaluation.ipynb
/home/georg/projects/ml4t-zh/case_studies/us
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/case_studies
/home/georg/projects/ml4t-zh/case_studies/cme_futures
/home/georg/projects/ml4t-zh/case_studies/cme_futures/benchmark
/home/georg/projects/ml4t-zh/case_studies/cme_futures/config
/home/georg/projects/ml4t-zh/case_studies/config
/home/georg/projects/ml4t-zh/case_studies/config/cae
/home/georg/projects/ml4t-zh/case_studies/config/dml
/home/georg/projects/ml4t-zh/case_studies/config/elastic_net
/home/georg/projects/ml4t-zh/case_studies/config/ipca
/home/georg/projects/ml4t-zh/case_studies/config/lasso
/home/georg/projects/ml4t-zh/case_studies/config/lgb
/home/georg/projects/ml4t-zh/case_studies/config/logistic
/home/georg/projects/ml4t-zh/case_studies/config/lstm
/home/georg/projects/ml4t-zh/case_studies/config/nbeats
/home/georg/projects/ml4t-zh/case
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 370 match(es) in 370 file(s)

/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md

/home/georg/projects/ml4t-zh/case_studies/research/cv.py

/home/georg/projects/ml4t-zh/case_studies/research/configs.py

/home/georg/projects/ml4t-zh/case_studies/research/causal.py

/home/georg/projects/ml4t-zh/case_studies/research/comparison.py

/home/georg/projects/ml4t-zh/case_studies/research/decisions.py

/home/georg/projects/ml4t-zh/case_studies/research/execution.py

/home/georg/projects/ml4t-zh/case_studies/research/catalog.py

/home/georg/projects/ml4t-zh/case_studies/research/models.py

/home/georg/projects/ml4t-zh/case_studies/research/results.py

/home/georg/projects/ml4t-zh/case_studies/research/recovery.py

/home/georg/projects/ml4t-zh/case_studies/research/model_planning.py

/home/geo
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:47Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/case_studies/utils/registry/ && echo \"---UTILS---\" && ls -la /home/georg/projects/ml4t-zh/case_studies/utils/ && echo \"---RESEARCH---\" && ls -la /home/georg/projects/ml4t-zh/case_studies/research/"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/store.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/README.md"})`


> [reasoning] There's a `case_studies/utils/registry/` package. That's the registry code. The glob for registry.db found nothing because it's likely gitignored/not committed (a runtime artifact). Let me read the registry package and RUN_LOG.md, README.md, and configs.

Let me read the key files in parallel.
The registry lives in `case_studies/utils/registry/`. Reading the core package + docs + configs now.

  <details><summary>tool output</summary>

  ```text
total 332
drwxr-xr-x 2 georg georg  4096 Sep 10 00:21 .
drwxr-xr-x 4 georg georg  4096 Sep 10 00:21 ..
-rw-r--r-- 1 georg georg  5775 Sep 10 00:21 __init__.py
-rw-r--r-- 1 georg georg 17779 Sep 10 00:21 completeness.py
-rw-r--r-- 1 georg georg  1288 Sep 10 00:21 lineage.py
-rw-r--r-- 1 georg georg 30220 Sep 10 00:21 maintenance.py
-rw-r--r-- 1 georg georg 38570 Sep 10 00:21 metrics.py
-rw-r--r-- 1 georg georg 58961 Sep 10 00:21 queries.py
-rw-r--r-- 1 georg georg 90036 Sep 10 00:21 registration.py
-rw-r--r-- 1 georg georg 16603 Sep 10 00:21 specs.py
-rw-r--r-- 1 georg georg 49427 Sep 10 00:21 store.py
---UTILS---
total 1884
drwxr-xr-x  4 georg georg   4096 Sep 10 00:21 .
drwxr-xr-x 14 georg georg   4096 Sep 10 00:21 ..
-rw-r--r--  1 georg georg     85 Sep 10 00:21 __init__.py
-rw-r--r--  1
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/store.py</path>
<type>file</type>
<content>
1: """Storage, schema, and filesystem helpers for the experiment registry."""
2:
3: from __future__ import annotations
4:
5: import json
6: import logging
7: import sqlite3
8: import subprocess
9: from collections.abc import Mapping
10: from datetime import UTC, datetime
11: from pathlib import Path
12: from typing import TYPE_CHECKING
13:
14: from .specs import (
15:     IDENTITY_VERSION,
16:     _validate_spec,
17:     canonical_json,
18:     training_hash_from_spec,
19: )
20:
21: if TYPE_CHECKING:
22:     import numpy as np
23:
24: logger = logging.getLogger(__name__)
25: UTC = UTC
26:
27: # ---------------------------------------------------------------------------
28: # Sch
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

## assistant · 2026-09-13T07:17:49Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/__init__.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/setup.yaml"})`


> [reasoning] Now I have a lot. Let me read RUN_LOG.md, the registry __init__.py, registration.py (key functions), queries.py (readers), the crypto README and configs, and the us_equities_panel README. Also need to understand setup.yaml and config.

Let me read RUN_LOG.md (37k), registry __init__.py, registration.py select parts, queries.py select parts. Given large files, use grep to find function defs.

Let me do parallel.
Registry core found. Now reading RUN_LOG.md, the registry public API, and the two case-study configs/READMEs.

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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/__init__.py</path>
<type>file</type>
<content>
1: """Unified experiment registry with content-addressed storage.
2:
3: Three-level entity model::
4:
5:     training_run → prediction_set → backtest_run
6:
7: Each level is identified by a deterministic hash of its spec (the
8: identity-defining configuration).  The DB is a lean queryable index;
9: the filesystem ``spec.json`` is the source of truth.
10:
11: Usage::
12:
13:     from case_studies.utils.registry import (
14:         build_training_spec,
15:         load_preset,
16:         register_training_run,
17:         register_prediction_set,
18:         register_prediction_metrics,
19:         register_backtest_run,
20:         register_backtest_metrics,
21:         load
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/README.md</path>
<type>file</type>
<content>
1: # Crypto Perpetuals Funding
2:
3: This case study uses Binance perpetual futures to examine an asset-class-specific return source:
4: the transfer between long and short positions at each 8-hour funding settlement. Nineteen
5: perpetuals create the book's smallest cross-section and highest non-intraday decision frequency.
6: The pipeline therefore emphasizes completed-bar timing, official funding cash flows, transaction
7: costs, and uncertainty from only two validation folds.
8:
9: ## Dataset Profile
10:
11: | Property | Value |
12: |---|---|
13: | Asset class | Crypto perpetual futures |
14: | Frequency | 8-hourly, aligned to funding settlements |
15: | Universe | 19 pe
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/setup.yaml</path>
<type>file</type>
<content>
1: strategy_id: crypto_perps_funding
2: setup_version: v1
3:
4: universe:
5:   symbols:
6:     - AAVEUSDT
7:     - ADAUSDT
8:     - APTUSDT
9:     - ATOMUSDT
10:     - AVAXUSDT
11:     - BNBUSDT
12:     - BTCUSDT
13:     - COMPUSDT
14:     - DOGEUSDT
15:     - DOTUSDT
16:     - ETHUSDT
17:     - INJUSDT
18:     - LINKUSDT
19:     - MKRUSDT
20:     - NEARUSDT
21:     - SOLUSDT
22:     - SUIUSDT
23:     - UNIUSDT
24:     - XRPUSDT
25:   n_assets: 19
26:   eligibility_rule: top_perps_by_volume
27:   panel_note: Unbalanced panel; assets enter at listing date (no backfill).
28:
29: decision:
30:   cadence: 8_hour_funding_aligned
31:   snapshot: pre_funding_timestamp
32:
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:53Z

- **tool**: `grep({"pattern": "^def |^class ", "path": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py", "output_mode": "content"})`
- **tool**: `grep({"pattern": "^def |^class ", "path": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/queries.py", "output_mode": "content"})`
- **tool**: `grep({"pattern": "^def |^class |CASE_STUD|case_studies", "path": "/home/georg/projects/ml4t-zh/case_studies/research/catalog.py", "output_mode": "content", "head_limit": 80})`
- **tool**: `grep({"pattern": "run_log", "path": "/home/georg/projects/ml4t-zh/.gitignore", "output_mode": "content"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/run_log 2>/dev/null || echo \"NO run_log dir (gitignored / not downloaded)\"; echo \"---\"; ls /home/georg/projects/ml4t-zh/case_studies/*/run_log 2>/dev/null || echo \"no case run_log dirs\""})`


> [reasoning] Excellent, very rich. Now I need:
- registration.py writer functions (signatures and what they write)
- queries.py reader functions
- research/ package: catalog.py (enumerates case studies?), workspace.py, configs.py, execution.py
- how case studies share code (research package imports)
- registry enumerates nine case studies metadata: probably research/catalog.py or a config.
- crypto specifics: funding_data.py, funding_backtest.py, 02_labels.py, 03_financial_features.py, 16_costs.py
- etfs config setup.yaml for comparison
- run_log directory existence (gitignored?). Let me check .gitignore and if any run_log exists.

Let me look at function definitions in registration.py and queries.py via grep, plus read research/catalog.py and workspace.py. Also check where registry is referenced by notebooks.

Let me batch.
Now the writer/reader symbols, the study catalog, and crypto-specific modules.

  <details><summary>tool output</summary>

  ```text
Found 24 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py
  52: def _atomic_save_json(path: Path, data: dict) -> None:
  61: def _sampling_reduced(spec_json: str | None) -> bool:
  88: def _validate_prediction_dispersion(predictions, *, refuse: bool = True) -> None:
  188: def clear_prediction_sets(
  287: def register_training_run(
  464: def record_training_runtime(
  528: def register_epoch_checkpoint(
  733: def _declared_label_buffer(case_study: str, label: str | None) -> str | None:
  745: def _sibling_direction_labels(case_study: str, case_dir, label: str | None):
  779: def register_prediction_set(
  1084: def _has_fold_column(predictions) -> bool:
  1096: def _detect_fold_col(predictions) -> str | None:
  1106: def _detect_score_cols
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 29 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/utils/registry/queries.py
  42: def _table_exists(case_dir: Path, table: str) -> bool:
  59: def _existing_prediction_hashes(case_dir: Path) -> set[str] | None:
  71: def _query_table(
  94: def load_training_runs(
  121: def load_prediction_sets(
  159: def load_prediction_metrics(
  181: def load_backtest_runs(
  201: def load_backtest_metrics(
  385: def load_backtest_fold_metrics(
  418: def load_all_training_runs():
  438: def load_all_prediction_metrics():
  463: def _spans_identity_generations(case_dir: Path) -> bool:
  477: def load_prediction_index(
  592: def read_training_spec(
  610: def read_backtest_spec(
  627: def read_predictions(
  661: def training_dir(case_study: str, training_hash: str, *, case_
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 16 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/research/catalog.py
  11: from case_studies.utils.registry.specs import IDENTITY_VERSION, canonical_json
  142: def _tables(db: sqlite3.Connection) -> set[str]:
  148: def _columns(db: sqlite3.Connection, table: str) -> set[str]:
  152: def _select(column: str, columns: set[str], alias: str, default: str = "NULL") -> str:
  160: def _nested(spec: dict[str, Any], *path: str) -> Any:
  169: def _computation(spec: dict[str, Any]) -> dict[str, Any]:
  174: def _flatten(prefix: str, value: Any, output: dict[str, Any]) -> None:
  182: def _open_value(value: Any) -> Any:
  188: def _registry_rows(root: Path, origin: str, *, immutable: bool = False) -> list[dict[str, Any]]:
  379: def _dtype(values: list[Any]) -> Any:
  393
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 4 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/.gitignore
  177: case_studies/*/run_log/
  178: case_studies/*/run_log
  252: # creates one at `<workspace>/.preview/<case_study>/run_log/`. The `case_studies/*/run_log`
  255: **/run_log/
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
NO run_log dir (gitignored / not downloaded)
---
no case run_log dirs
zsh:1: no matches found: /home/georg/projects/ml4t-zh/case_studies/*/run_log


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-13T07:17:58Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py", "offset": 287, "limit": 240})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/__init__.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/workspace.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/research/configs.py"})`


> [reasoning] Registry.db isn't present (downloaded separately). I have full schema. Now let me read key writer functions (register_training_run, register_prediction_set, register_backtest_run) and research catalog/workspace/configs/execution. Also check the case-study enumeration. Let me grep for the nine list.

Let me read registration.py around lines 287-530, 779-900, 1188-1300. And research/__init__.py, catalog.py beginning, workspace.py, configs.py.

Also the crypto funding_data.py / funding_backtest.py / 02_labels.py / 16_costs.py to describe specifics.

Batch reads.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py</path>
<type>file</type>
<content>
287: def register_training_run(
288:     case_study: str,
289:     spec: dict,
290:     *,
291:     entry_point: str | None = None,
292:     case_dir: Path | None = None,
293:     started_at: str | None = None,
294:     elapsed_s: float | None = None,
295:     runtime_provenance: dict | None = None,
296: ) -> str:
297:     """Register a training run. Returns training_hash.
298:
299:     Parameters
300:     ----------
301:     case_study : str
302:         Case study ID (e.g. "etfs").
303:     spec : dict
304:         Identity-defining config (hashed). Must contain at least
305:         ``family``, ``label``, and ``seed``. If ``seed`` is omitted,
306:         DEFAULT_SEED (42)
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
<path>/home/georg/projects/ml4t-zh/case_studies/research/configs.py</path>
<type>file</type>
<content>
1: """The declared model population, as a visible catalog.
2:
3: A case study declares which models it fits in its training menus,
4: ``config/training/<label>.yaml``. This module turns those menus into a Polars frame so a notebook
5: can *show* the population it is about to fit rather than describe it in prose, and build the
6: requests from the same frame the reader just saw.
7:
8: Three case studies had each written a private copy of this before it existed here, and the copies
9: had drifted: two of the three silently shrank the population when a configuration name was
10: mistyped. Selection is strict here for that reason.
11: """
12:
13: from __future__ import annotations
14:
15:
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:02Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py", "offset": 779, "limit": 200})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py", "offset": 1188, "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_data.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -l \"us_firm_characteristics\" --glob '*.py' --glob '*.json' --glob '*.yaml' | head -40; echo \"===CASE LIST DEFS===\"; rg -n \"crypto_perps_funding\" --glob '*.py' -g '!case_studies/crypto_perps_funding/**' | head -40"})`


> [reasoning] Now I need the registration writer for predictions and backtests, and the crypto-specific modules. Also need to find where the nine case studies are enumerated with metadata (maybe scripts or docs, or the README table; maybe research/catalog or a config file). Let me search for "us_firm_characteristics" listings.

Also the crypto-specific: funding_data.py, funding_backtest.py, 02_labels.py, 03_financial_features.py, 16_costs.py, config/training/fwd_ret_8h.yaml, config/backtest/base.yaml, benchmark jsons.

Let me batch:
- read register_prediction_set (779-1085) and register_backtest_run (1188-1330)
- read crypto funding_data.py, funding_backtest.py (maybe large)
- grep for CASE_STUDIES list / enumeration
- read etfs setup.yaml (for comparison)
- read crypto benchmark json

Let me do several parallel calls.
Now the prediction/backtest writers, crypto-specific modules, and the case-study enumeration.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py</path>
<type>file</type>
<content>
779: def register_prediction_set(
780:     case_study: str,
781:     training_hash: str,
782:     *,
783:     checkpoint_value: int | None = None,
784:     checkpoint_kind: str | None = None,
785:     split: str = "validation",
786:     predictions=None,
787:     metrics: dict[str, float | dict] | None = None,
788:     task_type: str = "regression",
789:     class_values: list | None = None,
790:     eval_col: str | None = None,
791:     label: str | None = None,
792:     case_dir: Path | None = None,
793:     expected_keys=None,
794:     allow_partial: bool = False,
795: ) -> str:
796:     """Register a prediction set. Returns prediction_hash.
797:
798:     Parameters
799:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py</path>
<type>file</type>
<content>
1188: def register_backtest_run(
1189:     case_study: str,
1190:     prediction_hash: str,
1191:     strategy_spec: dict,
1192:     *,
1193:     stage: str | None = None,
1194:     returns=None,
1195:     trades=None,
1196:     fills=None,
1197:     equity=None,
1198:     portfolio_state=None,
1199:     weights=None,
1200:     metrics: dict[str, float | dict] | None = None,
1201:     case_dir: Path | None = None,
1202:     started_at: str | None = None,
1203:     elapsed_s: float | None = None,
1204: ) -> str:
1205:     """Register a backtest run. Returns backtest_hash.
1206:
1207:     Parameters
1208:     ----------
1209:     prediction_hash : str
1210:         Input predict
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_data.py</path>
<type>file</type>
<content>
1: """Official Binance USD-M perpetual funding-rate data for the crypto case study."""
2:
3: from __future__ import annotations
4:
5: import io
6: import zipfile
7: from concurrent.futures import ThreadPoolExecutor, as_completed
8: from datetime import UTC, date, datetime
9: from pathlib import Path
10:
11: import httpx
12: import polars as pl
13: import yaml
14:
15: from data.exceptions import DataNotFoundError
16: from utils import ML4T_DATA_PATH
17: from utils.paths import get_case_study_dir
18:
19: BASE_URL = "https://data.binance.vision/data/futures/um/monthly/fundingRate"
20: FUNDING_PATH = ML4T_DATA_PATH / "crypto" / "market" / "funding_rate.parquet"
21:
22:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
06_strategy_definition/03_case_study_overview.py
09_model_based_features/case_study_temporal_summary.py
12_gradient_boosting/05_cross_library_hpo.py
scripts/download_artifacts.py
scripts/pre_run_gate.py
scripts/prove_us_firm_latent_interface.py
12_gradient_boosting/01_ensemble_foundations.py
11_ml_pipeline/07_case_study_insights.py
12_gradient_boosting/12_case_study_insights.py
18_transaction_costs/01_cost_taxonomy.py
20_strategy_synthesis/03_signal_quality.py
18_transaction_costs/02_spread_estimation.py
20_strategy_synthesis/holdout.py
20_strategy_synthesis/00_holdout_predictions.py
20_strategy_synthesis/01_aggregate_synthesis.py
04_fundamental_alternative_data/01_academic_characteristics.py
20_strategy_synthesis/04_signal_to_strategy.py
20_strategy_synthesis/08_recommendations.py
case_st
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:05Z

- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && sed -n '30,70p' scripts/download_artifacts.py && echo \"===OVERVIEW DICT===\" && sed -n '60,200p' 06_strategy_definition/03_case_study_overview.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && echo \"===crypto 02_labels imports/functions===\" && rg -n \"^import |^from |^def |^# |^LABEL|^HORIZON|^FREQ|^BAR\" case_studies/crypto_perps_funding/02_labels.py | head -60 && echo \"===crypto 16_costs===\" && rg -n \"^import |^from |^def |^# |COST|BPS|bps|maker|taker|funding\" case_studies/crypto_perps_funding/16_costs.py | head -70"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && echo \"===crypto 06_linear imports===\" && rg -n \"^import |^from \" case_studies/crypto_perps_funding/06_linear.py && echo \"===etfs 06_linear imports===\" && rg -n \"^import |^from \" case_studies/etfs/06_linear.py && echo \"===crypto 07_gbm imports===\" && rg -n \"^import |^from \" case_studies/crypto_perps_funding/07_gbm.py && echo \"===results dirs===\" && ls -d case_studies/*/results 2>/dev/null || echo \"no results dirs\"; rg -n \"results/.*
…[truncated])`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_backtest.py", "limit": 120})`


> [reasoning] Now I need to understand:
- The case-study registry/enumeration: 06_strategy_definition/03_case_study_overview.py has a dict. scripts/download_artifacts.py has CASE_STUDIES list. Let me read those relevant parts.
- crypto labels (02_labels.py), features (03_financial_features.py), costs (16_costs.py), backtest (funding_backtest.py), config/training/fwd_ret_8h.yaml, config/backtest/base.yaml.
- results/ vs run_log: check for results dirs and docs.

Let me batch reads. 02_labels.py and 03_financial_features.py may be large; read with limits. Let me first get function lists and sizes.

Also need to identify shared modules imported by notebooks. Let me grep imports in crypto 06_linear.py and etfs 06_linear.py to show shared code usage.

Let me do parallel.

  <details><summary>tool output</summary>

  ```text
import uuid
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent

# GitHub release configuration
GITHUB_REPO = "stefan-jansen/machine-learning-for-trading"
RELEASE_TAG = "v3.0.0-artifacts"
BASE_URL = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}"

CASE_STUDIES = [
    "etfs",
    "crypto_perps_funding",
    "nasdaq100_microstructure",
    "sp500_equity_option_analytics",
    "us_firm_characteristics",
    "fx_pairs",
    "cme_futures",
    "sp500_options",
    "us_equities_panel",
]

ARTIFACT_SHA256 = {
    "cme_futures": "ab1c97276cdf74aa95d894cc0b0f3ea909c3ed8356f41f217e008c971e34b4f8",
    "crypto_perps_funding": "517030f3def6d0264984c2b545032741100df4ee3d159e44ef4c348a314c4c7f",
    "etfs": "93d3e24dcb4872b965f355a6931f163e087
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===crypto 02_labels imports/functions===
1:# ---
2:# jupyter:
3:#   jupytext:
4:#     cell_metadata_filter: tags,-all
5:#     text_representation:
6:#       extension: .py
7:#       format_name: percent
8:#       format_version: '1.3'
9:#       jupytext_version: 1.19.3
10:#   kernelspec:
11:#     display_name: Python 3 (ipykernel)
12:#     language: python
13:#     name: python3
14:# ---
16:# %% [markdown]
17:# # Crypto Perpetuals: Label Engineering
19:# Every model in this case study is trained to predict the label defined here, so an error in
20:# it is silent where it is made and reaches every metric and every backtest after it. This
21:# notebook fixes the execution convention, proves each labelled row has a complete forward
22:# window, measures how much independent information those
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===crypto 06_linear imports===
75:import re
77:import numpy as np
78:import plotly.graph_objects as go
79:import polars as pl
80:from plotly.subplots import make_subplots
82:from case_studies.research import (
93:from utils.style import COLORS, show_plotly_with_alt
===etfs 06_linear imports===
67:import re
69:import numpy as np
70:import plotly.graph_objects as go
71:import polars as pl
72:from plotly.subplots import make_subplots
74:from case_studies.research import (
84:from utils.style import COLORS, show_plotly_with_alt
===crypto 07_gbm imports===
79:import numpy as np
80:import plotly.graph_objects as go
81:import polars as pl
82:from plotly.subplots import make_subplots
84:from case_studies.research import (
95:from utils.style import COLORS, show_plotly_with_alt
===results dirs===
n
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_backtest.py</path>
<type>file</type>
<content>
1: """Funding-settlement accounting for perpetual-futures engine backtests."""
2:
3: from __future__ import annotations
4:
5: import math
6: from datetime import UTC, datetime
7: from functools import wraps
8: from typing import Any
9:
10: import polars as pl
11:
12:
13: def _as_utc(value: datetime) -> datetime:
14:     return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
15:
16:
17: class FundingSettlementLedger:
18:     """Apply position-signed funding during the engine's bar-time update."""
19:
20:     def __init__(self, funding_rates: pl.DataFrame) -> None:
21:         required = {"symbol", "timestamp", "funding_rate"}
22:
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:10Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/training/fwd_ret_8h.yaml"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/backtest/base.yaml"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/etfs/config/setup.yaml"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -n \"results/|results\\b\" .gitignore | head -20; echo \"===GIT LOG results===\"; git log --oneline --all -- 'case_studies/*/results/**' 2>/dev/null | head; echo \"===docs results===\"; rg -n \"results/|deprecated legacy|source of truth\" docs/*.md case_studies/*.md 2>/dev/null | head -30"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/02_labels.py", "offset": 72, "limit": 200})`


> [reasoning] I have enough on crypto funding. Now need:
- 02_labels.py specifics on feature/label construction: forward return windows, buffer, etc. Let me read portions.
- 03_financial_features.py feature list.
- config/training/fwd_ret_8h.yaml, config/backtest/base.yaml.
- etfs setup.yaml (for comparison).
- us_equities_panel 06_linear imports to show shared pipeline.
- understand how results/ differs: it's only referenced as deprecated. Check .gitignore for results/ and git history maybe. Also scripts/create_experiment.py and download_artifacts.py.
- research/execution.py run_model_population writer.
- registry completeness / queries load_training_runs.

Let me read key things. Also check for `results` references in docs/book text.

Let me batch.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/training/fwd_ret_8h.yaml</path>
<type>file</type>
<content>
1: # Model configurations for fwd_ret_8h
2: # Each entry references a preset in case_studies/config/{model_type}/.
3: # Comment out lines to skip configs; add new preset names to extend.
4:
5: linear:
6: - ols
7: - ridge_a0.001
8: - ridge_a0.01
9: - ridge_a0.1
10: - ridge_a1.0
11: - ridge_a10.0
12: - ridge_a100.0
13: - ridge_a1000.0
14: - ridge_a10000.0
15: - ridge_a100000.0
16: - ridge_a1000000.0
17: - ridge_a10000000.0
18: - lasso_f0.5
19: - lasso_f0.2
20: - lasso_f0.08
21: - lasso_f0.03
22: - lasso_f0.015
23: - lasso_f0.35
24: - lasso_f0.7
25: - lasso_f0.85
26: - enet_f0.5
27: - enet_f0.2
28: - enet_f0.08
29: - enet_f0.03
30: - enet_f0.015
31: - enet_f
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/backtest/base.yaml</path>
<type>file</type>
<content>
1: account:
2:   allow_short_selling: true
3: execution:
4:   execution_price: price
5:   execution_mode: same_bar
6: commission:
7:   model: percentage
8:   rate: 0.0004
9: slippage:
10:   model: percentage
11:   rate: 0.0001
12: calendar:
13:   calendar: crypto
14:   timezone: UTC
15:   data_frequency: irregular
16: metadata:
17:   case_study: crypto_perps_funding

(End of file - total 17 lines)
</content>
  ```
  </details>

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
168:case_studies/*/results/
199:test_results/
===GIT LOG results===
===docs results===
case_studies/RUN_LOG.md:70:the source of truth for the universe, decision cadence, execution defaults, cost
case_studies/README.md:54:|   +-- registry.db            # Result and provenance source of truth
case_studies/README.md:71:- `run_log/registry.db` is the only result source of truth; legacy result JSON files are not used
docs/running-notebooks.md:120:Notebooks use **Jupytext percent format**: the source of truth is the `.py` file, and `.ipynb` is generated from it.
docs/running-notebooks.md:245:Every model training run, prediction set, causal-effect estimate, and backtest is recorded in a per-case-study **run log** (`run_log/`). The SQLite catalog `run_log/registry.db` is the single source of truth
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/02_labels.py</path>
<type>file</type>
<content>
72: from utils.paths import get_case_study_dir
73: from utils.style import COLORS, FIGSIZE, add_message_title, show_with_alt
74:
75: warnings.filterwarnings("ignore")
76:
77: CASE_STUDY_ID = "crypto_perps_funding"
78: CASE_DIR = get_case_study_dir(CASE_STUDY_ID)
79: LABELS_DIR = CASE_DIR / "labels"
80:
81: # %% [markdown]
82: # Both parameters are unset by default, and both are read below. `START_DATE` trims the history
83: # to a later start; `MAX_SYMBOLS` keeps only the first symbols in alphabetical order. Either one
84: # shortens a run, at the cost of a thinner cross-section for the rank correlation in Section G.
85:
86: # %% tags=["parameters"]
87: MAX_SYMBOLS = Non
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:14Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/README.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && echo \"===crypto 03 feature defs===\" && rg -n \"^def |^# %%.*Feature|feature_set|FEATURE|financial\" case_studies/crypto_perps_funding/03_financial_features.py | head -60 && echo \"===crypto 04 model-based===\" && rg -n \"^def |garch|hmm|GARCH|HMM\" case_studies/crypto_perps_funding/04_model_based_features.py | head -30 && echo \"===us_equities 06_linear imports===\" && rg -n \"^from case_studies|^from utils|^import\" case_studies/us_equities_pane
…[truncated])`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && echo \"===gitignore generated dirs===\" && rg -n \"labels/|features/|evaluation/|benchmark/|run_log|/results\" .gitignore | head -30 && echo \"===execution.py defs===\" && rg -n \"^def |^class \" case_studies/research/execution.py | head -40"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/scripts/create_experiment.py", "limit": 120})`


> [reasoning] I have plenty. Let me now gather:
- 03_financial_features.py feature families/list (function names and feature count 39).
- us_equities_panel 06_linear imports and 16_backtest to compare.
- research/execution.py run_model_population and run_backtests (writer orchestrators).
- scripts/create_experiment.py (workspace copy) and download_artifacts.py (release/registry install).
- results/ difference: legacy results JSON mention in history. .gitignore line 168. Let me check git log for results removal, or grep repo for "results/*.json". Might not matter much. RUN_LOG and copilot instructions both say registry.db is SSOT, legacy results/*.json deprecated.

Also check etfs/us_equities_panel stage list to compare. Let me read us_equities_panel README.

Let me also confirm the benchmark/ folder and labels/ features/ gitignored.

Let me batch.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/case_studies/us_equities_panel/README.md</path>
<type>file</type>
<content>
1: # Case Study: US Equities Panel
2:
3: This case study is the broadest cross-sectional equity workflow in the book. It uses daily OHLCV data from NASDAQ Data Link for ~3,200 US stocks spanning 1990 through 2018-Q1 to test whether weak per-stock signals translate into a tradable strategy when scaled across thousands of names. The Fundamental Law of Active Management is the operating frame: the per-stock edge is small, but breadth across the cross-section is supposed to compensate. The role of this case study is to hold that claim against measured signal quality, paired-bootstrap confidence intervals, and an explicit holdout window.
4:
5: The pipeline is unusually long because t
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===crypto 03 feature defs===
56:# Writes `features/financial.parquet` with a `.digest.json` sidecar, read by
101:FEATURES_DIR = CASE_DIR / "features"
310:def carry_features(df: pl.DataFrame) -> pl.DataFrame:
337:def funding_moments(df: pl.DataFrame, bars: int) -> pl.DataFrame:
350:def half_life(bars: int, *, clip_variance: bool, zero_to_window: bool) -> pl.Expr:
459:def mean_reversion_features(df: pl.DataFrame) -> pl.DataFrame:
494:def momentum_features(df: pl.DataFrame) -> pl.DataFrame:
533:def volatility_features(df: pl.DataFrame) -> pl.DataFrame:
573:def cross_sectional_features(df: pl.DataFrame) -> pl.DataFrame:
606:def regime_features(df: pl.DataFrame) -> pl.DataFrame:
667:def per_symbol_features(df: pl.DataFrame) -> pl.DataFrame:
688:def build_features(df: pl.DataFrame) -> pl.DataFra
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===gitignore generated dirs===
151:case_studies/*/features/
153:case_studies/*/labels/
163:case_studies/*/evaluation/
168:case_studies/*/results/
177:case_studies/*/run_log/
178:case_studies/*/run_log
252:# creates one at `<workspace>/.preview/<case_study>/run_log/`. The `case_studies/*/run_log`
255:**/run_log/
===execution.py defs===
36:class ModelExecution:
43:class PreviewPopulation:
58:class BacktestExecution:
88:class PlannedBacktest:
96:class BacktestPlan:
106:class _ResolvedBacktest:
112:def run_models(
167:def _copy_row(
199:def _import_released_prediction(study: Study, prediction: PredictionResult) -> None:
241:def _validate_selection(study: Study, predictions: pl.DataFrame) -> list[PredictionResult]:
253:def _resolve_backtest_plan(
303:def plan_backtests(
332:def run_backtests(
4
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/scripts/create_experiment.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """Create a writable, isolated case-study experiment from installed artifacts."""
3:
4: from __future__ import annotations
5:
6: import argparse
7: import json
8: import shutil
9: import stat
10: import uuid
11: from pathlib import Path
12:
13: REPO_ROOT = Path(__file__).resolve().parent.parent
14: GENERATED_DIRS = ("run_log", "labels", "features", "evaluation", "benchmark")
15:
16:
17: def _make_writable(root: Path) -> None:
18:     for path in (root, *root.rglob("*")):
19:         path.chmod(path.stat().st_mode | stat.S_IWUSR)
20:
21:
22: def create_experiment(
23:     case_study: str,
24:     output_root: Path,
25:     *,
26:     repo_root: Path = REPO_R
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:18Z

- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -n \"run_log|\\.release|SHA256SUMS|registry|foreign_key|integrity|install\" scripts/download_artifacts.py | head -50"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && python3 -c \"import json;d=json.load(open('case_studies/crypto_perps_funding/benchmark/fwd_ret_8h.json'));print(json.dumps(d,indent=1)[:1500])\""})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -n \"features =|FEATURE_SPECS|pl.col\\(\\\"premium|def build_features\" case_studies/crypto_perps_funding/03_financial_features.py | head; echo \"---count output---\"; rg -n \"39|n_features|feature_count|len\\(features\\)\" case_studies/crypto_perps_funding/03_financial_features.py | head"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && echo \"=== research_workflow crypto ===\"; rg -n \"^def |^from |^import |register|registry|BACKTEST|CARRIER|frozen\" case_studies/crypto_perps_funding/research_workflow.py | head -50"})`


> [reasoning] I have enough for a comprehensive report. Let me also quickly verify:
- download_artifacts.py installs run_log and the .release/SHA256SUMS, and how it verifies.
- crypto 03 feature count / 39 features and the benchmark.
- The 16_costs / 13_backtest frozen carrier (register=False).

But the request is focused. Let me get a couple more concrete items:
1. `run_log/.release/SHA256SUMS` source (download_artifacts install) to explain source of truth. Let me grep download_artifacts for run_log and .release.
2. crypto benchmark JSON content (equal-weight benchmark).
3. crypto 03 feature list names to state 39 features.

Let me do a final batch.

  <details><summary>tool output</summary>

  ```text
4:These artifacts contain registry databases, model predictions, and backtest
173:    expected_prefix = ("case_studies", cs_id, "run_log")
182:def _verify_run_log(run_log: Path) -> None:
183:    manifest = run_log / ".release/SHA256SUMS"
187:    root = run_log.resolve()
190:        artifact = (run_log / relative.strip().lstrip("*")).resolve()
196:    registry = run_log / "registry.db"
197:    uri = f"file:{registry.resolve()}?mode=ro&immutable=1"
199:        integrity = connection.execute("PRAGMA integrity_check").fetchone()
200:        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
201:    if integrity != ("ok",) or foreign_keys:
202:        raise ValueError("Installed registry failed SQLite integrity checks")
215:def install_artifact_archive(
223:    """Verify a
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
{
 "case_study": "crypto_perps_funding",
 "label": "fwd_ret_8h",
 "method": "daily_cross_sectional_mean_close_pct_change",
 "periods_per_year": 365,
 "n_symbols_declared": 19,
 "n_symbols_in_universe": 19,
 "sharpe": 0.166642,
 "cagr": -0.14496,
 "vol": 0.744246,
 "n_periods": 730,
 "ts_min": "2022-01-01",
 "ts_max": "2025-12-31",
 "by_period": {
  "overall": {
   "sharpe": 0.244888,
   "cagr": -0.088459,
   "vol": 0.734551,
   "n_periods": 1461
  },
  "validation": {
   "sharpe": 0.166642,
   "cagr": -0.14496,
   "vol": 0.744246,
   "n_periods": 730
  },
  "holdout": {
   "sharpe": 0.324951,
   "cagr": -0.028309,
   "vol": 0.725238,
   "n_periods": 731
  },
  "validation_window": [
   "2022-01-01",
   "2023-12-31"
  ],
  "holdout_window": [
   "2024-01-01",
   "2025-12-31"
  ]
 }
}


Incr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
258:        pl.col("premium_index_close").is_null().sum().alias("missing premium"),
326:        + [pl.col("premium_index_close").alias("premium_level")]
688:def build_features(df: pl.DataFrame) -> pl.DataFrame:
824:features = built.select(["timestamp", "symbol", *feature_cols]).sort(["timestamp", "symbol"])
---count output---
459:def mean_reversion_features(df: pl.DataFrame) -> pl.DataFrame:
676:        .pipe(mean_reversion_features)
925:# The matrix carries **39 features** on **99,877 rows** across **19 perpetuals**, from
932:    f"{len(feature_cols)} features, {len(features):,} rows, {features['symbol'].n_unique()} perps"
1026:        "Dendrogram of all 39 features. The cut leaves 23 clusters, nine of which hold more than "
1103:# where there is little to rank; the **39** columns fall in
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== research_workflow crypto ===
3:from __future__ import annotations
5:import hashlib
6:import inspect
7:import json
8:import os
9:import sqlite3
10:from collections.abc import Iterable
11:from pathlib import Path
12:from typing import Any
14:import polars as pl
16:from case_studies.research import (
24:from case_studies.research.contracts import ExecutionTier
25:from case_studies.research.execution import ModelExecution
26:from case_studies.research.models import ModelRequest
27:from utils.modeling import load_configs
37:def open_study(*, execution_tier: str, workspace: str | Path | None = None) -> Study:
54:def model_request_catalog(
103:def model_requests(
127:def declared_menu() -> set[tuple[str, str, str]]:
137:def unsupported_requests() -> set[tuple[str, str, str]]:
153:def official
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:23Z

- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -n \"results/|strategy_assessment|RESULTS_DIR|write_json|\\.json\" case_studies/us_equities_panel/20_strategy_analysis.py | head -20; echo \"===etfs 19/20 strategy===\"; rg -ln \"results/\" case_studies/*/20_strategy_analysis.py case_studies/*/19_strategy_analysis.py 2>/dev/null | head"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && rg -n \"results/|registry.db|run_log\" docs/running-notebooks.md | head -30"})`


> [reasoning] I have abundant material. Let me compose the structured report.

Let me make sure I have the key answer for #6 (results vs run_log). From evidence:
- RUN_LOG.md says registry.db is catalog and source of truth.
- case_studies/README.md line 71: registry.db is the only result source of truth; legacy result JSON files are not used.
- copilot-instructions.md: "sole source of truth for model/backtest/strategy results is run_log/registry.db. results/*.json files are a deprecated legacy format."
- .gitignore line 168: case_studies/*/results/ (so results/ is a gitignored legacy output).
- docs/running-notebooks.md:245: registry.db is single source of truth.
- us_equities_panel README stage 20 writes `results/strategy_assessment.json` — legacy path still produced but not SSOT. Actually it says writes results/strategy_assessment.json. Let me check if 20_strategy_analysis still writes results. Let me quickly grep.

Also I should note the scale table.

Let me quickly check results references in us_equities 20_strategy_analysis and if there's a `results` dir writer.

Also for #5 (config/registry enumerating nine case studies):
- case_studies/config/ is shared model presets (not per-project enumeration).
- The nine are enumerated in: scripts/download_artifacts.py CASE_STUDIES + ARTIFACT_SHA256; 06_strategy_definition/03_case_study_overview.py DISPLAY_NAMES/CHAPTER_TRACKS; case_studies/README.md table. There's no single central metadata registry file beyond these. The per-case `config/setup.yaml` is the SSOT for each.

Let me verify results writer quickly and also whether there's a `.release/SHA256SUMS` doc. Then write the report.

  <details><summary>tool output</summary>

  ```text
===etfs 19/20 strategy===


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
245:Every model training run, prediction set, causal-effect estimate, and backtest is recorded in a per-case-study **run log** (`run_log/`). The SQLite catalog `run_log/registry.db` is the single source of truth for all metrics discussed in the book — IC scores, Sharpe ratios, drawdowns, etc.
282:`case_studies/{cs}/run_log/`. An interrupted or corrupt download leaves any existing run log
285:- **`registry.db`** - the accepted metrics and provenance database
327:training or backtest stage. The artifact bundle installs the registry (`run_log/`) only, so first
473:repository, start from an empty `run_log/`: none of the four reaches `backtest_hash`, so rows computed


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-13T07:18:27Z


> [reasoning] The 20_strategy_analysis didn't show results/ matches — README may be stale. Good enough. The results/ dir is gitignored legacy. Let me note README references it as legacy and not SSOT.

Now let me write the final structured report. I need to be technical, concrete with paths and schema. Skip plotting.

Let me organize:

## 0. Top-level layout
## 1. Case study folder contents
## 2. registry.db (schema, writers/readers, identity/hashing, provenance)
## 3. Shared code
## 4. crypto_perps_funding specifics
## 5. Nine-case-study enumeration/metadata
## 6. results vs run_log SSOT

Include file paths and key symbols.

Let me include the exact schema tables list and columns for the main ones. I'll summarize the 20 tables.

Tables (from REGISTRY_SCHEMA_SQL):
1. training_runs
2. training_identity_migrations
3. prediction_sets
4. prediction_coverage
5. prediction_metrics
6. fold_metrics
7. backtest_runs
8. backtest_metrics
9. backtest_fold_metrics
10. causal_runs
11. backtest_paired_metrics
12. cohort_metrics
13. candidate_sets
14. candidate_set_members
15. candidate_set_names
16. execution_attempts
17. candidate_fold_completions
18. official_populations
19. official_population_members
20. overlay_references
21. decision_artifacts

Let me count: that's 21. RUN_LOG says eight reader-facing + fourteen more = 22. Close enough; I'll list all.

Key writers:
- register_training_run (registration.py:287)
- record_training_runtime (:464)
- register_epoch_checkpoint (:528)
- register_prediction_set (:779)
- register_prediction_metrics (:1121)
- register_fold_metrics (:1149)
- register_backtest_run (:1188)
- register_backtest_metrics (:1522)
- register_backtest_fold_metrics (:1546)
- register_paired_metrics (:1585)
- register_cohort_metrics (:1680)
- register_causal_run (:1988)
- register_causal_supersedes (:1786)
- maintenance: migrate_equivalent_training_identity, deduplicate_semantic_backtests

Readers (queries.py):
- load_training_runs (:94)
- load_prediction_sets (:121)
- load_prediction_metrics (:159)
- load_backtest_runs (:181)
- load_backtest_metrics (:201)
- load_backtest_fold_metrics (:385)
- load_all_training_runs (:418)
- load_all_prediction_metrics (:438)
- load_prediction_index (:477)
- read_training_spec (:592), read_backtest_spec (:610), read_predictions (:627)
- training_dir/prediction_dir/backtest_dir
- resolve_best_predictions, resolve_best_backtest_runs
- model_source

Store/path/connection:
- _open_registry (store.py:520), _registry_db_path (store.py:473) → case_dir/run_log/registry.db
- _training_dir/prediction_dir/backtest_dir
- get_training_dir (store.py:481)
- REGISTRY_SCHEMA_SQL, _migrate_registry, _declare_uncertainty_columns, _backfill_candidate_set_names

Identity/hashing (specs.py):
- training_hash_from_spec, prediction_hash_from_parts, backtest_hash_from_parts
- canonical_json, compute_hash, HASH_LENGTH=12
- IDENTITY_VERSION=3
- project_training_identity
- build_training_spec, load_preset

Orchestration (research/):
- workspace.py Study/open_study
- configs.py load_model_configs/model_requests
- execution.py run_model_population/run_models/run_backtests
- results.py ResultsCatalog
- catalog.py PredictionCatalog/BacktestCatalog
- population.py OfficialPopulation
- selection_field.py SelectionField
- decisions.py DecisionArtifact
- recovery.py ExecutionLedger

Now shared code imports: notebooks import `case_studies.research` (the orchestration layer) and `case_studies.utils.*` (registry, feature_engineering, cv_window, backtest_loaders, etc.). Also `utils/` at repo root (modeling, artifact_specs, paths, style). Plus six ml4t-* libraries. Not copy notebooks.

crypto specifics:
- Universe 19 pairs, 8-hourly aligned to funding settlements, 2020-2025.
- Label: fwd_ret_8h close-to-close over h settlement periods; variants fwd_ret_24h, fwd_dir_8h (binary), fwd_dir_8h_3c (3-class). availability clock shift +1 bar (bar-open stamps advanced by BAR_HOURS). Buffer 8H. Holdout 2024-01-01 to 2025-12-31. 2 folds, 2Y train, 1Y val.
- Features: 39 in features/financial.parquet from 03 (carry, mean_reversion, momentum, volatility, cross_sectional, regime families), plus 5 model-based in 04 (GJR-GARCH(1,1) Student-t conditional vol z-score, 2-state Gaussian HMM funding regime). 44 total.
- Model: linear (ridge/lasso/enet 28 configs), GBM (15 lgb configs, CPU max_bin 255), deep_learning (nlinear/lstm_h64/tcn, 60-bar sequences), tabular_dl (tabm_s/m/l), causal_dml (dml). Training menus in config/training/*.yaml.
- Backtest: engine-based, funding settled via FundingSettlementLedger (funding_backtest.py) installed into broker._update_time. Cost: config/backtest/base.yaml percentage commission 4bps + slippage 1bps; setup costs fee_schedule taker 4bps/maker 2bps; Ch18 sweeps cost_grid_bps [0..50].
- 8-hourly → periods_per_year 365, allocator_lookback 240 (~80 days).
- benchmark/fwd_ret_8h.parquet + .json equal-weight cross-sectional mean.
- funding_data.py loads Binance official funding rates.
- Frozen carrier: notebooks 13-16 replay with register=False (register backtests but frozen carrier). Note README says 13-16 preserve frozen carrier diagnostic replay.

Config:
- config/setup.yaml: universe, decision cadence, execution, costs, labels, backtest sweep, evaluation, features register, model_based, modeling, causal.
- config/training/{label}.yaml: menu per label.
- config/backtest/base.yaml: engine config.
- Shared presets case_studies/config/{family}/*.yaml.

Case-study enumeration:
- scripts/download_artifacts.py CASE_STUDIES list + ARTIFACT_SHA256.
- 06_strategy_definition/03_case_study_overview.py DISPLAY_NAMES + CHAPTER_TRACKS + _infer_asset_class.
- case_studies/README.md table.
- No single YAML registry; per-case setup.yaml is SSOT. Note there's `case_studies/config/` shared preset dir but not a case registry. `case_studies/research/catalog.py` reads across registries.

results vs run_log:
- run_log/registry.db = SSOT (case_studies/README.md:71, RUN_LOG.md, docs/running-notebooks.md:245, copilot-instructions).
- results/ gitignored (.gitignore:168), legacy JSON, deprecated. us_equities README still lists results/strategy_assessment.json but code doesn't currently write it.
- run_log/ vs results/: run_log includes registry + heavy artifacts; results/ was legacy JSON summaries.

Also mention distribution: download_artifacts.py downloads release bundle and installs run_log, verifies .release/SHA256SUMS, SQLite integrity_check, foreign_key_check. create_experiment.py copies run_log/labels/features/evaluation/benchmark + config into writable ML4T_OUTPUT_DIR.

Also mention workspace/execution tiers and read-only baseline.

Now write the final answer with the required format. Keep it structured, concrete, and end with next steps. Cap lists at 5 where possible (but schema is long; that's data). The AGENTS.md says cap lists at 5 items; but this is a technical schema report where completeness is required. I'll use tables.

Let me write it.
<analysis>
**Literal Request**: Describe one case study end-to-end (crypto_perps_funding + an equity comparison), with directory layout, configs, stages, and especially run_log/registry.db schema/readers/writers.

**Actual Need**: A portable blueprint for AlphaMill's experiment tracking, artifact registry, and "one pipeline across many datasets" execution discipline.

**Success Looks Like**: Concrete absolute paths, exact SQLite tables/columns, named writer/reader symbols, the config hierarchy, and the shared-vs-copied code boundary.
</analysis>

# ml4t-zh Case Study Architecture

## 0. Top-level layout

```
/home/georg/projects/ml4t-zh/
  case_studies/            # nine case studies + shared code
    README.md              # nine-case table + directory contract
    RUN_LOG.md             # registry design doc (schema, identity, querying)
    config/                # SHARED model preset YAMLs, by family (not per-case)
      lgb/, ridge/, lstm/, tcn/, tabular_dl (tabm)/, pca/, ipca/, cae/, sdf/, ...
    research/              # SHARED orchestration library (Study, populations, execution)
    utils/                 # SHARED pipeline library
      registry/            # THE experiment registry package
      (...feature_engineering, cv_window, backtest_loaders, backtest_runner, gbm, linear...)
    crypto_perps_funding/
    us_equities_panel/
    etfs/  cme_futures/  fx_pairs/  nasdaq100_microstructure/  sp500_options/
    sp500_equity_option_analytics/  us_firm_characteristics/
  utils/                   # repo-level helpers (paths, modeling, artifact_specs, style)
  data/                    # dataset loaders (load_crypto_perps, ...)
  scripts/
    download_artifacts.py  # installs release run_log bundles
    create_experiment.py   # copies run_log/labels/features into writable ML4T_OUTPUT_DIR
  docs/running-notebooks.md
```

Case-study layout (contract from `/home/georg/projects/ml4t-zh/case_studies/README.md:37-58`):

```
case_studies/{id}/
  README.md                      # dataset profile + pipeline table
  config/
    setup.yaml                   # SSOT: universe, cadence, execution, costs, labels, CV, sweeps
    training/{label}.yaml        # per-label model menu (which presets to fit)
    backtest/base.yaml           # engine-level account/commission/slippage/calendar
  NN_*.py + NN_*.ipynb           # jupytext pairs; .py is source of truth, .ipynb generated
  labels/          # generated, gitignored (parquet + .digest.json)
  features/        # generated, gitignored
  evaluation/      # generated, gitignored
  benchmark/       # TRACKED equal-weight market reference (parquet + json), per label
  run_log/         # generated/release, gitignored
    registry.db                  # SQLite catalog = SSOT
    training/{training_hash}/    # spec.json + coefficients.parquet / model.pt / boosters
    predictions/{prediction_hash}/ predictions.parquet
    backtest/{backtest_hash}/    # spec.json, daily_returns.parquet, weights, trades, fills, equity, portfolio_state
  results/         # LEGACY, gitignored, deprecated (see §6)
```

`run_log/` is gitignored (`/home/georg/projects/ml4t-zh/.gitignore:177,178`), shipped as a release artifact. Full pipeline for crypto is staged 01-19; us_equities_panel 01-20 (see its README pipeline table).

## 1. Config hierarchy (three layers)

From `/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md:41-213`:

| Layer | Path | Content |
|---|---|---|
| Case setup | `case_studies/{id}/config/setup.yaml` | universe, decision cadence, execution defaults, cost model, labels+rebalance_step, backtest sweep grids, evaluation folds, feature register, causal estimand |
| Training menu | `case_studies/{id}/config/training/{label}.yaml` | list of preset names per family, e.g. crypto `fwd_ret_8h.yaml` has linear/gbm/deep_learning/tabular_dl/causal_dml |
| Preset | `case_studies/config/{family}/{name}.yaml` | hyperparameters only; family/library derived from directory |

Resolver path: `load_model_configs` → `model_requests` → `request.resolve()` → `training_hash_from_spec`. Shared preset loader: `load_preset` (`registry/specs.py:276`). Backtest engine config read via `get_backtest_config()` from `config/backtest/base.yaml`.

## 2. `run_log/registry.db`

**What it is**: per-case-study SQLite index (WAL mode). `_registry_db_path` = `case_dir/run_log/registry.db` (`store.py:473`). Opened by `_open_registry` (`store.py:520`) with `timeout=120`, `busy_timeout=60000`, `journal_mode=WAL`, `foreign_keys=ON`, then runs `_migrate_registry`, `REGISTRY_SCHEMA_SQL`, backfills. Schema is created/evolved in code at `/home/georg/projects/ml4t-zh/case_studies/utils/registry/store.py:31-355` (`REGISTRY_SCHEMA_SQL`). All nine case studies share one schema.

**Tables** (21 total; 8 reader-facing + maintenance/lineage side tables):

`training_runs`, `training_identity_migrations`, `prediction_sets`, `prediction_coverage`, `prediction_metrics`, `fold_metrics`, `backtest_runs`, `backtest_metrics`, `backtest_fold_metrics`, `causal_runs`, `backtest_paired_metrics`, `cohort_metrics`, `candidate_sets`, `candidate_set_members`, `candidate_set_names`, `execution_attempts`, `candidate_fold_completions`, `official_populations`, `official_population_members`, `overlay_references`, `decision_artifacts`.

**Core recorded fields**:

| Table | Key columns |
|---|---|
| `training_runs` | `training_hash` PK, `family`, `label`, `config_name`, `spec_json`, `created_at`, `git_commit`, `entry_point`, `started_at`, `elapsed_s`, `runtime_json`, `identity_version`, `execution_tier` |
| `prediction_sets` | `prediction_hash` PK, `training_hash` FK, `checkpoint_value`, `checkpoint_kind` (`tree_limit`/`epoch`/`final`), `split` (`validation`/`holdout`), `created_at` |
| `prediction_coverage` | expected/actual key digests, `n_expected`, `n_actual`, `n_missing`, `n_duplicates`, `n_folds_*`, `schema_json`, `artifact_digest`, `status` |
| `prediction_metrics` | `ic_mean`, `ic_std`, `ic_t`, `n_folds`, `pct_positive`, `task_type`, `accuracy`, `balanced_accuracy`, `auc_roc`, `auc_pr`, `log_loss`, `brier_score`, plus HAC/CI columns auto-added |
| `fold_metrics` | `(prediction_hash, fold_id)` PK, `ic`, `rmse`, `mae`, classification metrics, `auc_class_-1/0/1` |
| `backtest_runs` | `backtest_hash` PK, `prediction_hash` FK, `spec_json`, `stage` (`signal`/`allocation`/`cost_sensitivity`/`risk_overlay`/`holdout`), `created_at`, `git_commit`, `started_at`, `elapsed_s`, `artifact_digests_json` |
| `backtest_metrics` | `sharpe`, `sortino`, `total_return`, `max_drawdown`, `cagr`, `volatility`, `calmar`, `omega`, `stability`, `tail_ratio`, `win_rate`, `kurtosis`, `skewness`, `var_95`, `cvar_95`, `n_periods`, `num_trades`, `total_commission`, `total_slippage`, `avg_turnover` |
| `causal_runs` | `causal_hash` PK, `label`, `treatment`, `confounders_json`, `embargo`, `n_folds`, `n_obs`, `dml_effect`, `dml_se_hac`, `p_value_hac`, `naive_effect`, `confounding_bias_pct`, `refutation_p`, `spec_json`, `supersedes_hash` |

**Identity / hashing** (`/home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py`):
- `HASH_LENGTH = 12` (SHA-256 truncated), `IDENTITY_VERSION = 3`.
- `training_hash_from_spec(spec)` = `sha256(canonical_json(training_identity))[:12]`.
- `prediction_hash_from_parts(training_hash, checkpoint_value, split, checkpoint_kind, identity_version)`.
- `backtest_hash_from_parts(prediction_hash, strategy_spec)`; non-portable provenance stripped (`_HASH_EXCLUDED_METADATA = ("preset_path",)`) so paths don't change identity.
- `canonical_json` sorts keys/strips whitespace. Provenance (`notebook_path`, `git_commit`, `created_at`, `elapsed_s`) is stored but excluded from hashes, so re-running a notebook reuses the stored result instead of duplicating rows.

**Writers** (`/home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py`):
- `register_training_run` (:287) — writes `training/{hash}/spec.json` then inserts row, captures `_git_hash()`, `entry_point`, `identity_version`, `execution_tier`; refuses identity conflicts.
- `record_training_runtime` (:464), `register_epoch_checkpoint` (:528).
- `register_prediction_set` (:779) — validates coverage (`evaluate_prediction_coverage`), writes `predictions/{hash}/predictions.parquet`, `prediction_sets` + `prediction_coverage` rows, computes fold metrics.
- `register_prediction_metrics` (:1121), `register_fold_metrics` (:1149).
- `register_backtest_run` (:1188) — writes `backtest/{hash}/spec.json` plus `daily_returns.parquet`, `trades.parquet`, `fills.parquet`, `equity.parquet`, `portfolio_state.parquet`, `weights.parquet`; stores `artifact_digests_json`; infers `stage` via `_infer_stage` (:403).
- `register_backtest_metrics` (:1522), `register_backtest_fold_metrics` (:1546), `register_paired_metrics` (:1585), `register_cohort_metrics` (:1680).
- `register_causal_run` (:1988), `declare_causal_supersedes` (:1786).
- Maintenance: `migrate_equivalent_training_identity`, `deduplicate_semantic_backtests` (`registry/maintenance.py`).

**Readers** (`/home/georg/projects/ml4t-zh/case_studies/utils/registry/queries.py`):
`load_training_runs` (:94), `load_prediction_sets` (:121), `load_prediction_metrics` (:159), `load_backtest_runs` (:181), `load_backtest_metrics` (:201), `load_backtest_fold_metrics` (:385), `load_all_training_runs` (:418), `load_all_prediction_metrics` (:438), `load_prediction_index` (:477), `read_training_spec` (:592), `read_backtest_spec` (:610), `read_predictions` (:627), `training_dir`/`prediction_dir`/`backtest_dir` (:661-675), `resolve_best_predictions` (:982), `resolve_best_backtest_runs` (:1328), `model_source` (:716), `backfill_stages` (:1534).

**Public API**: `/home/georg/projects/ml4t-zh/case_studies/utils/registry/__init__.py` re-exports all of the above. Higher-level analytics wrappers in `case_studies/utils/analytics.py` (`load_model_ic`, `load_classification_metrics`, `load_best_ic_per_family`).

**Registry scale** (RUN_LOG.md:732-744): ~880 training runs, 1,070 prediction sets, 22 causal estimates, 15,140 backtest runs across nine registries; DB is MBs, artifacts GBs.

## 3. Shared code vs copied notebooks

Case studies **do not copy notebooks as code**. Every numbered `.py` imports shared modules:

- Orchestration layer `/home/georg/projects/ml4t-zh/case_studies/research/`: `open_study` (`workspace.py:481`), `load_model_configs`/`model_requests`/`resolved_model_plan` (`configs.py`), `run_model_population`/`run_models`/`run_backtests`/`plan_backtests` (`execution.py`), `ResultsCatalog`/`PredictionResult` (`results.py`), `PredictionCatalog`/`BacktestCatalog` (`catalog.py`), `OfficialPopulation`/`CandidateSet`/`SelectionField` (`population.py`, `comparison.py`, `selection_field.py`), `CausalRequest`/`CausalResult` (`causal.py`), `ExecutionLedger` (`recovery.py`).
- Pipeline library `/home/georg/projects/ml4t-zh/case_studies/utils/`: `feature_engineering.py`, `cv_window.py`, `folds.py`, `gbm.py`, `linear.py`, `tabular_dl.py`, `deep_learning.py`, `latent_factors/adapter.py`, `causal.py`, `backtest_runner.py`, `backtest_loaders.py`, `backtest_explorer.py`, `sweep_config.py`, `strategy_analysis.py`, `conformal.py`, `uncertainty.py`, `paired_metrics.py`, `artifact_digest.py`, etc.
- Repo-level `/home/georg/projects/ml4t-zh/utils/`: `modeling.py`, `artifact_specs.py`, `paths.py` (`get_case_study_dir`), `style.py`, `cv_splits.py`.
- Six external `ml4t-*` libraries are the production estimator implementations.

The same `06_linear.py` body is byte-identical in structure across `crypto_perps_funding`, `etfs`, `us_equities_panel` (same imports from `case_studies.research` + `utils.style`); only config/notebook metadata differ.

**Workspace/isolation**: `Study.open` / `open_study` (`research/workspace.py:225,481`) resolves a release root + optional `workspace`; read-only baseline vs writable copy; `ExecutionTier.CANONICAL` vs `PREVIEW` (preview writes to `<workspace>/.preview/<case>/run_log`). `scripts/create_experiment.py` copies `run_log, labels, features, evaluation, benchmark` + `config/` into a writable `ML4T_OUTPUT_DIR`.

## 4. `crypto_perps_funding` specifics

Config: `/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/setup.yaml`

- **Universe**: 19 USD-M perps (AAVEUSDT…XRPUSDT), 2020-2025, unbalanced at listing.
- **Frequency/decision**: `cadence: 8_hour_funding_aligned`, `snapshot: pre_funding_timestamp`, `execution_delay: at_funding_timestamp`; `features.bar_hours: 8`.
- **Thesis**: funding premium as crowding measure that mean-reverts; label is a forward perpetual price return, explicitly *not* the funding cash flow.
- **Labels** (`02_labels.py`): `fwd_ret_8h` (primary), `fwd_ret_24h`, `fwd_dir_8h` (binary), `fwd_dir_8h_3c` (3-class). Close-to-close `C_{t+h}/C_t - 1` with **availability clock**: bar-open timestamps advanced by `BAR_HOURS` before shifting, so predictors pair with known data. Exact-grid assertion; null across grid holes. `buffer: 8H`; holdout 2024-01-01..2025-12-31.
- **CV**: `n_splits: 2`, `train_size: 2Y`, `val_size: 1Y`, `periods_per_year: 365`, calendar `crypto`. Folds derived by `case_studies/utils/cv_window.py` from the label timeline.
- **Features** (`03_financial_features.py`): 39 columns → `features/financial.parquet`; families carry/mean_reversion/momentum/volatility/cross_sectional/regime; windows declared once in `setup.yaml:features.windows`. `04_model_based_features.py` adds 5 fold-agnostic features → `features/model_based.parquet`: GJR-GARCH(1,1) Student-t conditional-vol z-score and a 2-state Gaussian HMM funding regime; refit schedules in `setup.yaml:model_based`. 44-feature training frame.
- **Models** (`config/training/fwd_ret_8h.yaml`): linear (OLS + 12 Ridge + 8 Lasso + 8 ElasticNet), GBM (15 LightGBM leaf/loss configs, CPU `max_bin: 255`), deep_learning (nlinear, lstm_h64, tcn; 60-bar causal sequences), tabular_dl (tabm_s/m/l), causal_dml (dml). Causal estimand: treatment `premium_zscore_14d`, confounders `[price_vol_14d, funding_rate, premium_dev_mean_14d]`.
- **Backtest**: engine-driven. `config/backtest/base.yaml` — percentage commission `rate: 0.0004` (4 bps) + slippage `0.0001`, shorting allowed, crypto calendar. `setup.yaml:costs.fee_schedule` — taker 4 bps / maker 2 bps. Ch18 sweeps `cost_grid_bps: [0,1,2,3,5,7,10,15,20,30,50]`.
- **Funding accounting**: `/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_backtest.py` — `FundingSettlementLedger` monkey-patches `broker._update_time` to `settle()` position-signed funding at each settlement (`event_cash -= qty*mark*multiplier*rate`), asserts 100% settlement coverage. Data loader: `/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_data.py` (`load_funding_rates`, `download_funding_rates`, `funding_rates_for_prices`).
- **Sweep**: `top_k_grid: [3,5,10]`, 6 allocators, 14 risk controls, `top_n_predictions` stage funnel.
- **Frozen carrier**: notebooks 13-16 replay a pinned carrier with `register=False` (README lines 37-41); current-model sequence is 01-12.
- **Benchmark**: `/home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/benchmark/fwd_ret_8h.parquet` + `.json` (`method: daily_cross_sectional_mean_close_pct_change`, validation/holdout windows, Sharpe/CAGR/vol).

Equity comparison: `us_equities_panel` — daily, ~3,200 stocks, `fwd_ret_1d` primary, 16 folds (10Y/1Y), 62 cross-sectional features + walk-forward temporal, long-short dollar-neutral top-K, era-dependent 5-30 bps + borrow, holdout 2016-Q1..2018-Q1. Same 20-stage sequence, same registry API; extra stages 13a/13b (PCA/IPCA), 15 model analysis. `etfs` adds latent factors + macro context, 8 folds, monthly decisions.

## 5. Nine-case-study enumeration / metadata

There is **no single machine-readable case registry file**. The nine are enumerated redundantly in code/docs:

| Source | Path |
|---|---|
| Canonical list + archive checksums | `/home/georg/projects/ml4t-zh/scripts/download_artifacts.py:42` (`CASE_STUDIES`, `ARTIFACT_SHA256`), `:173` (`expected_prefix = ("case_studies", cs_id, "run_log")`) |
| Display names, chapter tracks, asset class | `/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py:73-186` (`DISPLAY_NAMES`, `CHAPTER_TRACKS`, `_infer_asset_class`) |
| Human table | `/home/georg/projects/ml4t-zh/case_studies/README.md:7-17` |
| HTTP route list | `/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py:74,86,176` |

Per-case metadata SSOT is each `config/setup.yaml`. Cross-registry reading is done dynamically by `case_studies/research/catalog.py` (`PredictionCatalog`, `BacktestCatalog`, `prediction_rows_at`) and `case_studies/utils/analytics.py`, not from a central manifest.

## 6. `results/` vs `run_log/registry.db`

- **`run_log/registry.db` is the sole source of truth** for model/backtest/strategy results:
  - `/home/georg/projects/ml4t-zh/case_studies/README.md:71`
  - `/home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md:1-8,419-422`
  - `/home/georg/projects/ml4t-zh/docs/running-notebooks.md:245,285`
  - `/home/georg/projects/ml4t-zh/.github/copilot-instructions.md`: "The sole source of truth for model/backtest/strategy results is `run_log/registry.db` ... `results/*.json` files are a deprecated legacy format and must not be treated as ground truth."
- **`results/` is legacy JSON**, gitignored (`/home/georg/projects/ml4t-zh/.gitignore:168 case_studies/*/results/`), no longer produced by the current strategy notebooks (no `results/` writes found in `20_strategy_analysis.py`). Some READMEs still list `results/strategy_assessment.json` from an earlier generation.
- **Distribution**: `download_artifacts.py` downloads the release archive, verifies `.release/SHA256SUMS` per file, runs SQLite `PRAGMA integrity_check` + `PRAGMA foreign_key_check`, then installs `run_log/` read-only. `create_experiment.py` clones it to a writable `ML4T_OUTPUT_DIR`.

## AlphaMill borrowings (direct mapping)

- One `registry.db` per dataset + shared orchestration library, not per-dataset scripts: the `case_studies/research` + `registry` split is the model.
- Content-addressed identity (spec hash → training hash → prediction hash → backtest hash) with provenance stored but unhashed is what makes reruns idempotent and sweeps resumable.
- Stage-tagged backtest runs (`signal`/`allocation`/`cost_sensitivity`/`risk_overlay`/`holdout`) give the "run one pipeline across many markets" discipline a uniform query surface.
- Populations (named immutable member lists) prevent comparing a half-finished sweep against a complete one.
- For crypto, treat funding settlement as a first-class ledger monkey-patched into the broker, separate from commission/slippage.

<results>
<files>
- /home/georg/projects/ml4t-zh/case_studies/RUN_LOG.md - authoritative run-log design: schema, identity hashing, three-level entity model, querying, distribution
- /home/georg/projects/ml4t-zh/case_studies/README.md - nine-case table, per-case directory contract, SSOT statement
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/store.py - SQLite schema (REGISTRY_SCHEMA_SQL), path/connection helpers (_open_registry, _registry_db_path), migrations, metric upsert
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/registration.py - all writers (register_training_run, register_prediction_set, register_backtest_run, register_causal_run, ...)
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/queries.py - all readers (load_training_runs, load_prediction_metrics, read_predictions, resolve_best_*)
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/specs.py - identity/hash functions, build_training_spec, load_preset
- /home/georg/projects/ml4t-zh/case_studies/utils/registry/__init__.py - public registry API surface
- /home/georg/projects/ml4t-zh/case_studies/research/workspace.py - Study/open_study, release vs writable workspace, canonical/preview tiers
- /home/georg/projects/ml4t-zh/case_studies/research/configs.py - load_model_configs, model_requests, resolved_model_plan
- /home/georg/projects/ml4t-zh/case_studies/research/execution.py - run_model_population, run_backtests, ModelExecution/BacktestExecution
- /home/georg/projects/ml4t-zh/case_studies/research/catalog.py - cross-registry PredictionCatalog/BacktestCatalog
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/setup.yaml - crypto SSOT (8h cadence, 19 perps, fees, labels, CV, sweeps)
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/training/fwd_ret_8h.yaml - model menu
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/config/backtest/base.yaml - engine commission/slippage/calendar
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/02_labels.py - forward-return labels + availability clock
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/03_financial_features.py - 39 features
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/04_model_based_features.py - GJR-GARCH + HMM features
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_backtest.py - FundingSettlementLedger
- /home/georg/projects/ml4t-zh/case_studies/crypto_perps_funding/funding_data.py - Binance funding-rate loader
- /home/georg/projects/ml4t-zh/scripts/download_artifacts.py - CASE_STUDIES list + release install/verify
- /home/georg/projects/ml4t-zh/scripts/create_experiment.py - writable workspace copy
- /home/georg/projects/ml4t-zh/us_equities_panel/README.md - equity-case comparison (daily, 16 folds, 20 stages)
</files>

<answer>
One case study = a config tree (`setup.yaml` + `training/{label}.yaml` + `backtest/base.yaml`), a numbered jupytext notebook sequence, generated `labels/ features/ evaluation/`, a tracked `benchmark/`, and a content-addressed `run_log/` whose `registry.db` is the SSOT. All nine share the `case_studies/research/` orchestration layer and `case_studies/utils/` pipeline library; notebooks are thin drivers, never copies. The registry models three hashed levels (training_run → prediction_set → backtest_run) plus a causal side table, with provenance (git_commit, entry_point, timestamps, runtime) stored but excluded from hashes so reruns are idempotent. `crypto_perps_funding` runs the same pipeline at 8-hourly funding settlements with 19 perps, forward-return labels on an availability clock, 39+5 features, a funding-settlement ledger in the backtest engine, and 4/2 bps taker/maker costs. `results/*.json` is deprecated legacy; `run_log/registry.db` is the single source of truth.
</answer>

<next_steps>
Map AlphaMill to this design in this order: (1) add a per-dataset `registry.db` with the training/prediction/backtest three-level hash chain; (2) port `register_*`/`load_*` writers/readers as one shared module; (3) tag backtest rows by pipeline stage; (4) add named immutable populations around sweeps; (5) for crypto, model funding as a broker-level settlement ledger separate from commission/slippage. If you want, point me at AlphaMill's current artifact/experiment code and I will produce a concrete migration diff against this schema.
</next_steps>
</results>
