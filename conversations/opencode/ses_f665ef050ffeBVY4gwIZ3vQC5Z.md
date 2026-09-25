---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f665ef050ffeBVY4gwIZ3vQC5Z"
title: "ml4t MLOps governance live (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-13T07:17:44Z"
updated_at: "2026-09-13T07:22:35Z"
tokens_input: 96942
tokens_output: 10845
cost: 0.0248
parent_id: "ses_f6664247effe4SLb37r5OF4RZ9"
---

# ml4t MLOps governance live (@explore subagent)

## user · 2026-09-13T07:17:44Z

[CONTEXT] I am analyzing /home/georg/projects/ml4t-zh ("Machine Learning for Trading, 3rd Edition" code). I need to understand its PRODUCTION / MLOps / GOVERNANCE / LIVE-TRADING layer, to compare with AlphaMill, a new crypto quant pipeline with a Freqtrade execution plane.

[GOAL] Precise technical description of ml4t's production track: how strategies are taken live, monitored, and governed. Concrete paths, class/function names, configuration, and lifecycle mechanisms.

[DOWNSTREAM] I will recommend how AlphaMill should design its monitoring/attribution/lifecycle loop (retrain/pause/retire) and its live-execution safety controls.

[REQUEST] Investigate and report paths + symbols + mechanism:
1. 25_live_trading/: the research-to-production bridging framework; broker integrations (IB, Alpaca, QuantConnect); order-lifecycle management; pipeline verification; operational readiness checks. Find the classes/interfaces.
2. 26_mlops_governance/: the failure taxonomy (pipeline divergence vs performance decay), drift detection, safe model rollout, circuit breakers, feature stores, experiment tracking. What tools/libraries (MLflow? Evidently? custom?) and what code implements each.
3. Any kill-switch / circuit-breaker / pause-retire logic anywhere in the repo (search "kill_switch", "circuit_breaker", "retire", "pause", "drift").
4. The ml4t-live library: vendored or installed? What public API do notebooks call?
5. How live monitoring feeds back into retraining (the feedback loop shown in the README workflow diagram).
6. Any operational-readiness checklist or pre-deployment gate code.

Report structured, technical, concrete file paths and symbol names. Skip plotting.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-13T07:17:44Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 2 -type d | sort"})`
- **tool**: `glob({"pattern": "**/README*", "path": "/home/georg/projects/ml4t-zh"})`
- **tool**: `glob({"pattern": "**/*.md", "path": "/home/georg/projects/ml4t-zh"})`


> [reasoning] Let me start by exploring the repository structure. I'll launch parallel searches.
<analysis>
**Literal Request**: Map ml4t's production/MLOps/governance/live-trading layer: directories 25/26, broker integrations, order lifecycle, drift detection, circuit breakers, feature stores, ml4t-live library, feedback loop, readiness gates.
**Actual Need**: Extract concrete mechanism + symbol names from ml4t to inform AlphaMill's monitoring/attribution/lifecycle and live-safety design.
**Success Looks Like**: A structured report with absolute paths, class/function names, config keys, and control-flow mechanisms for each of the 6 areas.
</analysis>

I'll start with broad structural reconnaissance in parallel.

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
/home/georg/projects/ml4t-zh
/home/georg/projects/ml4t-zh/.git
/home/georg/projects/ml4t-zh/.git/gk
/home/georg/projects/ml4t-zh/.git/hooks
/home/georg/projects/ml4t-zh/.git/info
/home/georg/projects/ml4t-zh/.git/logs
/home/georg/projects/ml4t-zh/.git/objects
/home/georg/projects/ml4t-zh/.git/refs
/home/georg/projects/ml4t-zh/.github
/home/georg/projects/ml4t-zh/.github/ci
/home/georg/projects/ml4t-zh/.github/scripts
/home/georg/projects/ml4t-zh/.github/workflows
/home/georg/projects/ml4t-zh/.jupyter
/home/georg/projects/ml4t-zh/.jupyter/nbconvert_templates
/home/georg/projects/ml4t-zh/.omo
/home/georg/projects/ml4t-zh/.omo/run-continuation
/home/georg/projects/ml4t-zh/.workspace
/home/georg/projects/ml4t-zh/.workspace/transitions
/home/georg/projects/ml4t-zh/01_process_is_edge
/home/georg
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

  <details><summary>tool output</summary>

  ```text
Found 100 file(s)

/home/georg/projects/ml4t-zh/ml4t_bilingual.md
/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26_zh.md
/home/georg/projects/ml4t-zh/27_systematic_edge/chapter_27_zh.md
/home/georg/projects/ml4t-zh/25_live_trading/chapter_25_zh.md
/home/georg/projects/ml4t-zh/23_knowledge_graphs/chapter_23_zh.md
/home/georg/projects/ml4t-zh/20_strategy_synthesis/chapter_20_zh.md
/home/georg/projects/ml4t-zh/22_rag_financial_research/chapter_22_zh.md
/home/georg/projects/ml4t-zh/18_transaction_costs/chapter_18_zh.md
/home/georg/projects/ml4t-zh/17_portfolio_construction/chapter_17_zh.md
/home/georg/projects/ml4t-zh/19_risk_management/chapter_19_zh.md
/home/georg/projects/ml4t-zh/14_latent_factors/chapter_14_zh.md
/home/georg/projects/ml4t-zh/11_ml_pipeline/chapter_11_zh.md
/home/
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:55Z

- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/25_live_trading /home/georg/projects/ml4t-zh/26_mlops_governance -type f | sort"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/README.md"})`
- **tool**: `bash({"command": "grep -n -i \"ml4t-live\\|ml4t_live\\|ml4t\\.live\" /home/georg/projects/ml4t-zh/pyproject.toml /home/georg/projects/ml4t-zh/uv.lock | head -50"})`


> [reasoning] Let me look at the directory contents of 25 and 26, plus READMEs and pyproject for ml4t-live.
Step 1 of 6 done. Now examining the two target chapters' full contents and the root README workflow.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/25_live_trading/01_unified_framework_demo.ipynb
/home/georg/projects/ml4t-zh/25_live_trading/01_unified_framework_demo.py
/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.ipynb
/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py
/home/georg/projects/ml4t-zh/25_live_trading/03_ib_paper_trading_demo.ipynb
/home/georg/projects/ml4t-zh/25_live_trading/03_ib_paper_trading_demo.py
/home/georg/projects/ml4t-zh/25_live_trading/04_alpaca_paper_trading_demo.ipynb
/home/georg/projects/ml4t-zh/25_live_trading/04_alpaca_paper_trading_demo.py
/home/georg/projects/ml4t-zh/25_live_trading/05_alpaca_crypto_live_demo.ipynb
/home/georg/projects/ml4t-zh/25_live_trading/05_alpaca_crypto_live_demo.py
/home/georg/projects/ml4t-zh/25_live_tradin
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/README.md</path>
<type>file</type>
<content>
1: # Chapter 25: Live Trading Systems
2: 
3: The transition from profitable backtest to live execution is where most algorithmic trading projects fail. Not because the strategy lacks edge, but because the production system diverges from the research environment in subtle ways that erode returns. This chapter demonstrates how a unified framework eliminates that divergence by running identical strategy code in backtest, paper, and live modes.
4: 
5: ## Learning Objectives
6: 
7: After completing this chapter, you will be able to:
8: 
9: 1. Explain why technical divergence between research and production is a primary failure mode, and how a unified framework reduces that risk
10: 2. Design a dual-m
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/README.md</path>
<type>file</type>
<content>
1: # Chapter 26: MLOps and Governance
2: 
3: A model has cleared every backtest, the deployment verification of Chapter 25 has taken the system live, and real capital is now flowing through it. Keeping it working — and failing safely when it cannot — is the next problem. Every deployed model decays: regimes shift, competitors discover similar signals, and the relationships the model learned gradually erode. The difference between a profitable trading operation and a capital-destroying one often comes down to how quickly that decay is detected and how safely the system responds.
4: 
5: This chapter builds the post-deployment infrastructure that separates production-grade systems from research
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/pyproject.toml:66:    "ml4t-live>=0.1.0",
/home/georg/projects/ml4t-zh/uv.lock:4193:    { name = "ml4t-live" },
/home/georg/projects/ml4t-zh/uv.lock:4357:    { name = "ml4t-live", specifier = ">=0.1.0" },
/home/georg/projects/ml4t-zh/uv.lock:4530:name = "ml4t-live"
/home/georg/projects/ml4t-zh/uv.lock:4541:sdist = { url = "https://files.pythonhosted.org/packages/37/b3/a2bfb095294f78bee709dddb261d8cda81cc5584827e4d35af75a88c2b42/ml4t_live-0.1.0.tar.gz", hash = "sha256:3d527dce062441b83668df7e89b127d4db311ea5bd9d6dfaea469a3a0864a3f2", size = 109594, upload-time = "2026-08-10T19:03:37.41Z" }
/home/georg/projects/ml4t-zh/uv.lock:4543:    { url = "https://files.pythonhosted.org/packages/8b/27/087001b44f9ef821806d120322f20bf46b4d5a8b5d66cdd58a0ab9c9a776/ml4t_live-0.1
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:02Z

- **tool**: `bash({"command": "python3 -c \"import ml4t.live as m; print(m.__file__)\" 2>/dev/null; find / -path /proc -prune -o -type d -name \"ml4t_live*\" -print 2>/dev/null | head; find / -path /proc -prune -o -type d -path \"*ml4t/live*\" -print 2>/dev/null | head"})`
- **tool**: `bash({"command": "cd /home/georg/projects/ml4t-zh && git log --oneline -5 2>/dev/null; ls utils/ scripts/ tests/ 2>/dev/null"})`
- **tool**: `grep({"pattern": "^(from|import)\\s+(ml4t|feast|mlflow|evidently|alibi|river|skmultiflow)", "path": "/home/georg/projects/ml4t-zh/26_mlops_governance", "include": "*.py", "output_mode": "content"})`
- **tool**: `grep({"pattern": "^(from|import)\\s+(ml4t|ib_async|alpaca|okx|quantconnect)", "path": "/home/georg/projects/ml4t-zh/25_live_trading", "include": "*.py", "output_mode": "content"})`


> [reasoning] Now I need to examine the actual notebook .py files to extract concrete symbols. Let me read the key files. First, let me check whether ml4t_live is installed as a package I can inspect (site-packages). Let me also grep for key symbols.

Let me read the .py sources for 25 (01, 02, 07, 08, 10, 13) and 26 (01-06). These may be large. Let me start with grep for imports/symbols across all files, and locate the ml4t_live package.
Step 2 of 6 done: located chapters and confirmed `ml4t-live>=0.1.0` is a PyPI dependency (not vendored). Now inspecting the actual symbols and locating the installed library.

  <details><summary>tool output</summary>

  ```text
(no output)

<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
8d396ba Add WeChat Read indent-diagnosis sample EPUB
c895963 Force text-indent:0 inline on every paragraph and list item
256a91b Rework bilingual alignment: fix heading mispairs, Chinese pile-ups, and reader indent
c65f0b5 Add cover, back cover, and visible contents page to the bilingual EPUB
75f82e3 Add bilingual EPUB edition for e-ink readers
scripts/:
README.md
__init__.py
build_benchmark.py
create_experiment.py
download_artifacts.py
migrate_training_identity.py
pdf_chapter_to_md.py
pre_run_gate.py
probe_latent_identities.py
prove_cme_futures_interface.py
prove_crypto_interface.py
prove_sp500_options_interface.py
prove_us_equities_fold_major.py
prove_us_firm_latent_interface.py
record_artifact_supersession.py
sync_ch16_real_strategy_parity.py
sync_notebooks.py
verify_artifact_sidecars.p
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 6 match(es) in 3 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/06_mlflow_experiments.py
  440: import mlflow

/home/georg/projects/ml4t-zh/26_mlops_governance/05b_feast_live.py
  86: from feast import Entity, FeatureStore, FeatureView, Field, FileSource
  87: from feast.data_format import ParquetFormat
  88: from feast.types import Float64
  89: from feast.value_type import ValueType

/home/georg/projects/ml4t-zh/26_mlops_governance/01_drift_monitoring.py
  59: from ml4t.diagnostic.validation import DataFrameValidator
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 30 match(es) in 10 file(s)

/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py
  74: from ml4t.backtest.types import Order, OrderSide, OrderStatus, OrderType, Position
  75: from ml4t.live import LiveRiskConfig, RiskLimitError, SafeBroker, VirtualPortfolio
  76: from ml4t.live.protocols import ExecutionCapability

/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py
  94: from ml4t.backtest import BacktestConfig, DataFeed, Engine, ExecutionMode, OrderSide, Strategy

/home/georg/projects/ml4t-zh/25_live_trading/01_unified_framework_demo.py
  78: from ml4t.backtest import BacktestConfig, DataFeed, Engine, ExecutionMode, Strategy
  79: from ml4t.backtest.types import Order, OrderSide, OrderStatus, OrderType, Position
  82: from ml4t.live import (

/ho
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:05Z

- **tool**: `bash({"command": "ls -d /home/georg/projects/ml4t-zh/.venv /home/georg/projects/ml4t-zh/envs/ml4t 2>/dev/null; find /home/georg/.cache/uv -maxdepth 6 -type d -name \"ml4t_live*\" 2>/dev/null | head"})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/25_live_trading", "pattern": "^\\s*(class|def)\\s+\\w+"})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/26_mlops_governance", "pattern": "^\\s*(class|def)\\s+\\w+"})`


> [reasoning] The find command timed out. Let me locate ml4t_live package more efficiently - likely in a uv venv. Let me check .venv. Also read the key .py files. Let me focus.

Let me read the critical notebook sources. They're likely 300-700 lines. Let me read key ones with grep for class/function defs and important symbols first.
Step 3 of 6: reading the concrete implementation symbols. Let me pull class/function definitions and key API calls across both chapters.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/envs/ml4t


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 186 match(es) in 16 file(s)

/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py
  103: def _temporary_state_path(prefix: str = "nb10_state_") -> str:
  121: class MockBrokerQueries:
  136: def execution_capabilities(self):
  139: def assert_paper_trading(self) -> None:
  143: def positions(self) -> dict[str, Position]:
  147: def pending_orders(self) -> list[Order]:
  150: def get_position(self, asset: str) -> Position | None:
  177: def make_filled_order(
  209: def apply_mock_fill(broker: Any, order: Order) -> None:
  238: class MockBroker(MockBrokerQueries):
  241: def __init__(self, initial_cash: float = 100_000.0):
  288: def run_async_demo(awaitable):
  304: def run_demo(coro, expect_error: bool = False):

/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_de
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 89 match(es) in 7 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/06_mlflow_experiments.py
  130: def query_table(query: str, params: tuple[object, ...] = ()) -> pd.DataFrame:
  477: def log_catalog_to_mlflow(catalog: pd.DataFrame, max_runs: int = 50) -> int:

/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py
  81: class BreakerState(Enum):
  96: class BreakerEvent:
  114: def transition_breaker(
  152: def advance_breaker_state(
  189: class CircuitBreaker(ABC):
  190: def __init__(
  208: def check_condition(
  213: def update(self, event_time: datetime | None = None, **kwargs: object) -> BreakerState:
  216: def _transition(self, new_state, reason, value=None, threshold=None, event_time=None):
  219: def reset(self, event_time: datetime | None = Non
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:35Z

- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/envs/ml4t -maxdepth 7 -type d \\( -name \"ml4t\" -o -name \"ml4t_live*\" -o -name \"live\" \\) 2>/dev/null | head -20; echo \"---SITE---\"; find /home/georg/projects/ml4t-zh/envs/ml4t -maxdepth 6 -type d -name \"site-packages\" 2>/dev/null | head"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/13_runtime_safety_showcase.py", "offset": 1, "limit": 120})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py", "offset": 1, "limit": 120})`


> [reasoning] This is good. Now let me locate the ml4t_live package in envs/ml4t (likely a venv). Let me check its lib path. Also need to read key notebook sources to understand mechanisms: 02_etfs_deployment_loop, 08_pipeline_verification, 10_safety_risk_demo, 13_runtime_safety_showcase, 03_safe_model_rollout, 04_circuit_breakers, 01_drift_monitoring.

Let me find ml4t_live in envs/ml4t.
Step 3 of 6 done. Locating the installed `ml4t_live` package source (in envs/ml4t) and reading key notebook implementations.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/envs/ml4t
---SITE---


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/13_runtime_safety_showcase.py</path>
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
17: # # Runtime Safety Showcase: Stale Data, Kill Switch, Reconciliation, Health
18: #
19: # **Docker image**: `ml4t`
20: #
21: # **Section Reference**: 25.7 (Operational Readiness)
22: #
23: # **Implementation Skills**:
24: # - `ml4t.live.safety`: enforced `max_data_staleness_seconds` and `max
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py</path>
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
17: # # SafeBroker Risk Controls Demo
18: #
19: # **Docker image**: `ml4t`
20: #
21: # **Section Reference**: 25.7 (Operational Readiness)
22: #
23: # **Implementation Skills**:
24: # - ml4t.live.safety: SafeBroker, LiveRiskConfig, RiskState, RiskLimitError
25: # - ml4t.live.safety: VirtualPortfolio f
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:38Z

- **tool**: `bash({"command": "find /home/georg/.cache/uv /home/georg/.local /home/georg/.venv* -maxdepth 12 -type d -name \"ml4t\" 2>/dev/null | head; echo \"===LIVE===\"; find /home/georg/.cache/uv -maxdepth 8 -type d -name \"live\" -path \"*ml4t*\" 2>/dev/null | head; echo \"===ENVSML4T===\"; ls -la /home/georg/projects/ml4t-zh/envs/ml4t/"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py", "limit": 180, "offset": 240})`


> [reasoning] envs/ml4t seems empty (it's a placeholder dir). The library is installed somewhere in uv cache. Let me find it in the uv cache correctly. The earlier find on / timed out. Let me search specific likely locations: ~/.cache/uv, ~/.venv, /tmp, the conda envs. Let me do a targeted find with timeout.

Actually the .venv wasn't there. Let me check `which python` and site-packages via uv. Let me try `uv run python -c ...` but that might be slow. Let me just find in ~/.cache/uv with maxdepth.

  <details><summary>tool output</summary>

  ```text
===LIVE===
===ENVSML4T===
total 24
drwxr-xr-x 2 georg georg  4096 Sep 10 00:21 .
drwxr-xr-x 6 georg georg  4096 Sep 10 00:21 ..
-rw-r--r-- 1 georg georg 14407 Sep 10 00:21 Dockerfile


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py</path>
<type>file</type>
<content>
240: 
241:     def __init__(self, initial_cash: float = 100_000.0):
242:         self._cash = initial_cash
243:         self._positions: dict[str, Position] = {}
244:         self._pending_orders: list[Order] = []
245:         self._connected = False
246:         self._order_counter = 0
247: 
248:     async def submit_order_async(
249:         self,
250:         asset: str,
251:         quantity: int,
252:         side: OrderSide | None = None,
253:         order_type: OrderType = OrderType.MARKET,
254:         limit_price: float | None = None,
255:         stop_price: float | None = None,
256:         **_: Any,
257:     ) -> Order:
258:         """Fill one order immediately and upd
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:41Z

- **tool**: `grep({"output_mode": "files_with_matches", "path": "/home/georg/projects/ml4t-zh", "pattern": "kill_switch|circuit_breaker|circuit breaker|retire|pause", "include": "*.{py,md,yml,yaml,toml}"})`
- **tool**: `grep({"output_mode": "content", "path": "/home/georg/projects/ml4t-zh", "pattern": "retire|retirement|paused|pause_trading|halt", "include": "*.py", "head_limit": 60})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py", "limit": 160, "offset": 1})`


> [reasoning] The ml4t_live package is not installed locally in a discoverable dir (this repo appears to be just notebooks, deps not installed). I should rely on the notebooks and the lock/PyPI metadata. I can also fetch the ml4t-live package source from PyPI if needed? Possibly. But the notebooks themselves document the API extensively. Let me focus on reading the key notebook docs/mechanisms.

Let me now read:
- 25/13 rest (kill switch, reconciliation, runtime_status)
- 25/08 pipeline verification (gates)
- 25/02 deployment loop (run record / feedback)
- 26/04 circuit breakers (full)
- 26/03 safe rollout (PromotionCriteria)
- 26/01 drift monitoring (PSI, KS)
- 26/06 mlflow

Let me read these in parallel, focusing on markdown headers and code. I'll read selected ranges.

First grep for key terms across whole repo to answer Q3.
Step 4 of 6: running the repo-wide kill-switch/drift/retire search and reading the core mechanisms.

  <details><summary>tool output</summary>

  ```text
Found 132 match(es) in 132 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py

/home/georg/projects/ml4t-zh/26_mlops_governance/03_safe_model_rollout.py

/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md

/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26_zh.md

/home/georg/projects/ml4t-zh/26_mlops_governance/README.md

/home/georg/projects/ml4t-zh/case_studies/research/causal.py

/home/georg/projects/ml4t-zh/case_studies/research/comparison.py

/home/georg/projects/ml4t-zh/ml4t_bilingual.md

/home/georg/projects/ml4t-zh/19_risk_management/chapter_19.md

/home/georg/projects/ml4t-zh/case_studies/research/__init__.py

/home/georg/projects/ml4t-zh/case_studies/research/population.py

/home/georg/projects/ml4t-zh/12_gradient_boosting/chapte
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 60 match(es) in 7 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/utils/style.py
  386: # a single pass, and nothing warned. Wrapping here retires the whole class:

/home/georg/projects/ml4t-zh/case_studies/research/causal.py
  95: "them says which it retires - re-register the newer with SUPERSEDES_CAUSAL "
  250: # and which earlier identity this run retires is a statement about the registry.
  362: retires, or ``_enforce_causal_supersedes`` refuses the write - after the DML fit and every
  418: identity it retires. Papermill passes parameters as strings, so the declaration is
  419: one of three things: empty, meaning nothing is being retired and the fit must leave
  424: no-op - the run would proceed, retire nothing, and fail at registration - so it
  45
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py</path>
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
17: # # Circuit Breakers for Trading Systems
18: #
19: # **Chapter 26: MLOps and Governance**
20: # **Docker image**: `ml4t`
21: # **Book Reference**: Chapter 26, Section 26.5
22: # **Prerequisites**: Chapter 25 deployment verification and the Chapter 26 monitoring sections.
23: #
24: # **Learning
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:44Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py", "limit": 380, "offset": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/03_safe_model_rollout.py", "limit": 200, "offset": 420})`


> [reasoning] Now let me read the rest of circuit breakers critical parts (BreakerManager, breakers conditions), the safe rollout PromotionCriteria, drift monitoring PSI/KS, and pipeline verification gates, and the deployment loop run record. Let me read in parallel.
Step 5 of 6: extracting the readiness/rollout/drift mechanisms. Reading the critical sections in parallel.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py</path>
<type>file</type>
<content>
180:     return breaker.state
181: 
182: 
183: # %% [markdown]
184: # The abstract base class now delegates the mechanics to helper functions and
185: # keeps only the public interface shared across breaker types.
186: 
187: 
188: # %%
189: class CircuitBreaker(ABC):
190:     def __init__(
191:         self,
192:         name: str,
193:         recovery_timeout: timedelta = timedelta(hours=1),
194:         on_trip: Callable[[BreakerEvent], None] | None = None,
195:         on_transition: Callable[[BreakerEvent], None] | None = None,
196:     ):
197:         self.name = name
198:         self.recovery_timeout = recovery_timeout
199:         self.on_trip = on_trip
200:         sel
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/03_safe_model_rollout.py</path>
<type>file</type>
<content>
420:         shadow_positions.loc[timestamp, ("long_assets", incumbent)]
421:         | shadow_positions.loc[timestamp, ("short_assets", incumbent)]
422:     )
423:     candidate_assets = (
424:         shadow_positions.loc[timestamp, ("long_assets", candidate)]
425:         | shadow_positions.loc[timestamp, ("short_assets", candidate)]
426:     )
427:     position_agreement.append(
428:         len(incumbent_assets & candidate_assets) / len(incumbent_assets | candidate_assets)
429:     )
430: 
431: 
432: # %% [markdown]
433: # The shadow summary contains only hypothetical returns. No allocation or capital path is computed.
434: 
435: 
436: # %%
437: shadow_stats = pd.DataFram
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:46Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/01_drift_monitoring.py", "limit": 180, "offset": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/08_pipeline_verification.py", "limit": 140, "offset": 90})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/25_live_trading", "pattern": "run_record|run record|monitor|registry|retrain|feedback|drift|manifest", "head_limit": 80})`


> [reasoning] Excellent. Now let me read the drift monitoring PSI/KS implementation and the pipeline verification gates + deployment loop run record + ml4t-live CLI. Also the chapter_25.md and chapter_26.md contains conceptual detail. Let me grep for the CLI `ml4t-live status` and `run record`, `monitoring`, `registry.db` feedback loop.

Let me read:
- 26/01 drift monitoring lines 300-420 (PSI, DriftMetric, thresholds)
- 25/08 pipeline verification lines 100-220 and 820-960
- 25/02 deployment loop lines around run record persisting (grep "run record"/"monitor"/"registry")
- chapter_25.md section 25.7 for operational readiness checklist
- chapter_26.md sections

Let me do targeted greps plus reads.
Step 5 of 6 (continued): drift metrics, verification gates, and the monitoring feedback loop.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/01_drift_monitoring.py</path>
<type>file</type>
<content>
300: validate_feature_data(current_features, FEATURE_COLUMNS)
301: validate_feature_data(reference_features, FEATURE_COLUMNS)
302: 
303: print(f"Reference feature rows: {reference_features.height:,}")
304: print(f"Current feature rows:   {current_features.height:,}")
305: 
306: 
307: # %% [markdown]
308: # ## 3. Feature and prediction drift diagnostics
309: #
310: # The reference set is the last pre-holdout year. The current slice is the most
311: # recent 63 trading days inside the holdout. PSI flags material shifts, while
312: # the K-S test checks whether the two samples plausibly come from the same
313: # distribution.
314: 
315: 
316: # %%
317: def compute_psi(
318:     ref
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/08_pipeline_verification.py</path>
<type>file</type>
<content>
90: # If the infrastructure cannot coexist in a single environment, the chapter's unified-framework claim has
91: # already broken down before any strategy logic runs.
92: 
93: # %% [markdown]
94: # ## 1. Define Test Strategy
95: #
96: # The strategy is intentionally deterministic so any mismatch between backtest and live outputs is a
97: # technical bug, not a statistical fluctuation.
98: 
99: 
100: # %%
101: @dataclass
102: class VerificationResult:
103:     """Result of a single verification test."""
104: 
105:     test_name: str
106:     passed: bool
107:     expected: Any
108:     actual: Any
109:     message: str = ""
110:     skipped: bool = False
111:     expected_diffe
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 69 match(es) in 11 file(s)

/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py
  26: # - Kill switch, position limits, order limits, drawdown monitoring
  40: # and daily-loss monitoring - are available through `LiveRiskConfig` but are

/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py
  60: # - Chapter 26: Repeated model serving and monitoring
  63: # - Run a full retrain-and-deploy cycle on real ETF data with no mock
  65: # - Persist deployment artefacts separately from research registry runs.
  165: # GARCH refit per symbol on every retrain; the deployment trade is to
  200: # highest-validation-IC Ridge configuration in the ETFs registry); we adopt it here
  202: # (registry-stored, CV-evaluated, IC-reported) from the *deployment
  255: # T
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:49Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py", "limit": 180, "offset": 590})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/08_pipeline_verification.py", "limit": 170, "offset": 815})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/25_live_trading/chapter_25.md", "pattern": "^#|checklist|pre-flight|preflight|readiness|kill switch|shadow|golive|go-live|staged|rollout", "head_limit": 100})`


> [reasoning] Now I have a clear picture. Let me read the deployment loop run_record block (25/02 lines 500-760) which is the feedback contract; the pipeline verification gate at end (25/08 lines 820-982); and the chapter_25/26 markdown for the operational readiness checklist and §26.4/26.5 concepts. Also the ml4t-live CLI. Let me check if there's a CLI entry point in the repo (probably in installed package). Search repo for "ml4t-live status" and CLI docs. Also read chapter_25.md §25.7 and chapter_26.md.

Let me do parallel reads.
Step 6 of 6: reading the deployment-loop run record contract, verification gate, and chapter operational-readiness sections.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py</path>
<type>file</type>
<content>
590: status_counts: dict[str, int] = {}
591: for r in exec_results:
592:     status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
593: print("Execution summary:", dict(sorted(status_counts.items())))
594: print(
595:     f"intended={len(intended_basket)} / attempted={len(attempted_basket)} / "
596:     f"accepted={len(accepted_basket)} / failed={len(failed_basket)}"
597: )
598: 
599: # %%
600: exec_summary = pl.DataFrame(
601:     [
602:         {
603:             "symbol": r["symbol"],
604:             "predicted_return": round(r["predicted_return"], 6),
605:             "status": r["status"],
606:             "qty": r.get("qty"),
607:             "order_id": (str
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/08_pipeline_verification.py</path>
<type>file</type>
<content>
815:     ]
816: 
817: 
818: # %% [markdown]
819: # The release gate composes both result groups and fails closed when either replay was skipped.
820: 
821: 
822: # %%
823: def run_verification_tests() -> list[VerificationResult]:
824:     """Run the complete parity contract."""
825:     if not (backtest_executed and live_executed):
826:         return skipped_results()
827:     return pipeline_results(backtest_strategy, live_strategy) + execution_results(
828:         backtest_strategy, live_strategy
829:     )
830: 
831: 
832: # %% [markdown]
833: # The human-readable report shows every check, including skipped and intentionally different stages.
834: 
835: 
836: # %%
837: pri
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 71 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/25_live_trading/chapter_25.md
  1: # Chapter 25: Live Trading Systems
  14: - Plan a staged live rollout using pre-flight checks, shadow or paper trading, kill switches, reconciliation procedures, and awareness of venue and jurisdictional constraints.
  16: *Section 25.1* introduces the unified framework that lets identical strategy code run in both backtest and live modes. *Sections 25.2–25.3* integrate two broker APIs - Interactive Brokers for global multi-asset access and Alpaca for developer-friendly US equity and crypto trading - while *Section 25.4* evaluates managed platforms as an alternative path. *Section 25.5* models the order lifecycle as an explicit state machine, and *Section 25.6* establishes pipeline verification
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:52Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/chapter_25.md", "limit": 120, "offset": 483})`
- **tool**: `grep({"head_limit": 80, "include": "chapter_26.md", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/26_mlops_governance", "pattern": "pause|retire|decommission|rollback|promot|circuit|kill|feedback|retrain|three-layer|three layer"})`
- **tool**: `grep({"head_limit": 60, "include": "README.md", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh", "pattern": "feedback|retrain|monitor|lifecycle|deploy|production|MLOps"})`


> [reasoning] I have enough for most areas. Let me read the chapter_25.md §25.7 preflight checklist section (lines 483-592) and §25.5 order state machine, plus chapter_26 §26.4/26.5 for pause-retire/governance. Also the ml4t-live CLI docs. Let me read chapter_25.md lines 483-592 and chapter_26.md relevant sections.

Also need to answer Q5 feedback loop from README workflow diagram. Let me grep README for the workflow diagram and "feedback".

Let me do parallel.
Reading the operational checklist and governance lifecycle sections, plus the README feedback loop.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/chapter_25.md</path>
<type>file</type>
<content>
483: ## 25.7 Operational readiness
484: 
485: A system that passes all verification tests can still fail in production due to operational gaps. This section covers the pre-launch requirements and ongoing practices that separate reliable trading from catastrophic surprises.
486: 
487: ### Preflight checklist
488: 
489: Operational readiness begins with a startup gate, not with the first signal. Before the strategy is allowed to trade, several checks need to pass:
490: 
491: 1. The **runtime environment** must demonstrate that the container or server is healthy, network paths to the broker are open, data feeds are current, and that supporting services, such as databases and monitoring, are ava
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 39 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md
  7: This chapter builds the post-deployment infrastructure that separates production-grade trading systems from research prototypes. Where *Chapter 25* ensured the system launched correctly, the task now is to keep it correct, or to fail gracefully when it cannot. The governance model has three layers: detection through data validation gates, rolling metrics, and drift analysis; response through shadow evaluation and staged rollouts; and automated safety through circuit breakers that halt trading when losses or conditions breach limits. The supporting MLOps infrastructure, including feature stores, model registries, and CI/CD, should be right-sized to the team’s maturity rather than adopted who
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 60 match(es) in 15 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/10_text_feature_engineering/README.md
  12: - Use token-level attribution and related diagnostics to audit, debug, and stress-test NLP features before deployment
  34: This is the chapter's real practical core. It explains that a strong text model is not yet a tradable signal unless timestamps, entity resolution, revisions, aggregation rules, model training cutoffs, and evaluation protocols are all made point-in-time safe. It also connects representation models to real feature families such as sentiment, narrative surprise, topic exposure, structured event extraction, and interpretable diagnostics. Readers should care because this section is what turns NLP from a benchmark exercise into a re
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:56Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/25_live_trading/07_order_state_machine.py", "limit": 240, "offset": 68})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/25_live_trading", "pattern": "ml4t\\.live[\\w.]*|from ml4t\\.live import[\\s\\S]{0,300}"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/scripts/pre_run_gate.py"})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh", "pattern": "shap|SHAP|feature_importance|Evidently|evidently", "head_limit": 30})`


> [reasoning] I now have a comprehensive picture. Let me fill remaining gaps:
1. Order state machine details (10 states, 19 transitions) - read 07 file states/events
2. `ml4t-live` public API - list imported names across notebooks. Already have: LiveEngine, LiveRiskConfig, RiskLimitError, RiskState, SafeBroker, VirtualPortfolio, IBBroker, BarAggregator, IBDataFeed, ExecutionCapability, protocols. Let me grep all ml4t.live imports.
3. Pre-loaded operational ready checks in scripts/pre_run_gate.py (this is the repo's own pre-deployment gate, not ml4t-live). Interesting - "pre_run_gate.py". Might be relevant to Q6. Let me read it.
4. The failure taxonomy §26.1 table - read chapter_26 lines 30-60.
5. Drift monitoring model/feature SHAP - chapter mentions but code? grep SHAP.

Let me do these in parallel.
Filling final gaps: order state machine states, full `ml4t.live` API surface, and the repo's own pre-run gate.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/25_live_trading/07_order_state_machine.py</path>
<type>file</type>
<content>
68: # %%
69: # compliance: skip cell_size - one Enum definition with three property helpers
70: class OrderState(Enum):
71:     """All possible order states in the lifecycle."""
72: 
73:     # Initial states
74:     PENDING_NEW = auto()  # Order submitted, awaiting broker acknowledgment
75:     NEW = auto()  # Order acknowledged by broker
76: 
77:     # Active states
78:     ACCEPTED = auto()  # Order accepted by exchange
79:     PARTIALLY_FILLED = auto()  # Some quantity executed
80: 
81:     # Modification states
82:     PENDING_CANCEL = auto()  # Cancel request submitted
83: 
84:     # Terminal states (no further transitions)
85:     FILLED = auto()  # Fully executed
86:     C
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 43 match(es) in 12 file(s)

/home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py
  24: # - ml4t.live.safety: SafeBroker, LiveRiskConfig, RiskState, RiskLimitError
  25: # - ml4t.live.safety: VirtualPortfolio for shadow mode position tracking
  75: from ml4t.live import LiveRiskConfig, RiskLimitError, SafeBroker, VirtualPortfolio
  76: from ml4t.live.protocols import ExecutionCapability
  80: print("[OK] ml4t.live risk controls imported")

/home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py
  490: from ml4t.live.brokers.alpaca import AlpacaBroker

/home/georg/projects/ml4t-zh/25_live_trading/09_crypto_funding_deployment_loop.py
  501: from ml4t.live.brokers.alpaca import AlpacaBroker

/home/georg/projects/ml4t-zh/25_live_trading/01_unified_framework_
…[truncated]
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

  <details><summary>tool output</summary>

  ```text
Found 30 match(es) in 4 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/06_strategy_definition/03_case_study_overview.py
  281: #   Panel 3,199) - a span that reshapes cross-sectional signal construction

/home/georg/projects/ml4t-zh/06_strategy_definition/01_where_ideas_come_from.py
  52: #   magnitude, and shape*.

/home/georg/projects/ml4t-zh/05_synthetic_data/01_timegan.py
  184: n_features = all_data.shape[1]  # Actual number of stocks found (may differ from TICKERS)
  185: print(f"Shape: {all_data.shape} (days × stocks)")
  525: batch_size_actual = batch.shape[0]
  571: batch_size_actual = batch.shape[0]
  780: _pca = PCA(n_components=min(2, _real_flat.shape[1], _n_viz))
  787: n_components=min(2, _real_flat.shape[1]),

/home/georg/projects/ml4t-zh/05_synth
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:59Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md", "limit": 70, "offset": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md", "limit": 70, "offset": 320})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/README.md", "limit": 45, "offset": 20})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/case_studies/research", "pattern": "^def (retired_prediction_hashes|split_retired_members|superseded_members)|^class RetirementSplit|^def .*retire"})`


> [reasoning] SHAP is only mentioned in chapter prose, not implemented in the notebooks (grep found only "shape"). Let me confirm by searching chapter 26 for SHAP code. Actually the grep on *.py found only "shape" matches, meaning no shap implementation in Python files. The chapter says SHAP is discussed but NB01 implements PSI/KS only. Let me note that.

Now let me check the README workflow diagram description and the failure taxonomy table. Let me read README lines 30-60 and chapter_26 lines 30-60. Also the guard "drift" tests. Also the `04_circuit_breakers` recovery protocol section (lines 560-818) for pause/resume discipline. Let me read those.

Also, need to confirm: is there any actual "retire" logic in the ML live layer? The repo has "retire/supersede" in the research registry (case_studies/utils/registry, population.py) — this is model lifecycle governance at the research/registry level (candidate index retirement, retired prediction hashes). That's relevant: model retirement is implemented in the registry, not in the live plane. Let me capture symbols: `retired_prediction_hashes`, `split_retired_members`, `RetirementSplit`, `superseded_members`. And tests like test_candidate_index_retirement, test_carrier_retired_generations, test_retired_prediction_hashes. This is a governance mechanism worth reporting.

Let me read chapter_26 lines 30-60 (failure taxonomy) and 320-430 (circuit levels + recovery), plus README workflow lines 30-60. And grep registry retirement API.
Final reads: failure taxonomy, breaker recovery protocol, README workflow loop, and the registry-level model retirement mechanism.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md</path>
<type>file</type>
<content>
30: Technical failures are *verification problems*. *Chapter 25* addressed these: reconciliation between backtest and live systems should catch pipeline divergence. When a live system produces different outputs for identical inputs, the cause is a bug to fix.
31: 
32: ### Statistical failure caused by performance decay
33: 
34: *Statistical* failure occurs when the system works exactly as designed (the same inputs produce the same outputs), but the outputs no longer predict returns. The implementation is correct; the model has decayed.
35: 
36: Four mechanisms cause statistical decay:
37: 
38: - *Overfitting*: The model learned patterns from the training data that do not generalize to ne
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md</path>
<type>file</type>
<content>
320: ## 26.5 Circuit breakers and safety
321: 
322: Monitoring and safe updates address gradual decay. Circuit breakers address sudden failure: when something goes catastrophically wrong, and speed matters more than nuance. These are your automated safety nets: simple, hard-coded rules that protect capital when sophisticated systems fail.
323: 
324: ### Multi-level protection
325: 
326: Defense in depth: multiple independent safety layers, each catching different failure modes. The circuit breaker architecture implements four hierarchical levels:
327: 
328: - *Per-trade* (individual order validation)
329: - *Per-strategy* (exposure limits for a single strategy)
330: - *Portfolio* (aggreg
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/README.md</path>
<type>file</type>
<content>
20: machine to a running notebook, prerequisites included. The short version is under
21: [Quick Start](#quick-start) below.
22: 
23: <!-- offerings:next start -->
24: > **Next free session:** [How to Be Productive with Coding Agents, Beyond Code](https://maven.com/p/efe730), a 30-minute live session on **Wednesday, September 30, 2026, 11:00 AM ET / 15:00 UTC**. [All courses, workshops, and free lessons](https://ml4trading.io/courses/?utm_source=github&utm_medium=readme&utm_campaign=ml4t3e&utm_content=offerings).
25: <!-- offerings:next end -->
26: 
27: <p align="center">
28:   <a href="https://amzn.to/4eigy2F"><img src="assets/cover.png" width="45%" alt="Machine Learning for Trading, 3rd Edition"></a>
29: </p>
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 6 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/case_studies/research/population.py
  37: def retired_prediction_hashes(connection: sqlite3.Connection) -> set[str]:
  482: class RetirementSplit:
  494: def split_retired_members(
  576: def superseded_members(study: Study, *, member_kind: str = "prediction") -> frozenset[str]:
  648: def _retired(
  743: def superseded_members_at(
  ```
  </details>

## assistant · 2026-09-13T07:22:04Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md", "limit": 45, "offset": 390})`
- **tool**: `grep({"include": "03_safe_model_rollout.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/26_mlops_governance", "pattern": "capital|allocation|staged|A/B|ab_test|share|HALF_OPEN|recovery|reset"})`
- **tool**: `grep({"include": "*.py", "output_mode": "content", "path": "/home/georg/projects/ml4t-zh/26_mlops_governance", "pattern": "registry\\.db|training_runs|prediction_sets|backtest_runs|cohort_metrics|mlflow\\."})`


> [reasoning] I now have comprehensive material. Let me also check the circuit breaker recovery protocol (lines 390-430 of chapter 26) and the ml4t-live install in pyproject. Also confirm the failure taxonomy table. I have enough.

One more thing: the `ml4t-live` CLI subcommands: status, shadow. And public API. I have that. The library is a PyPI dep (not vendored); uv.lock has ml4t_live-0.1.0 sdist/whl.

Let me also check if there's a `data.py` load_etfs reference and `ml4t.diagnostic` usage. Not needed.

Let me quickly verify the circuit breaker recovery section lines 390-430. Also let me check the `04_circuit_breakers.py` end summary for recovery discipline. Actually I have the manager reset_all and recovery_timeout. Good enough.

Let me also verify whether there's any actual `pause`/`retire` code in 25/26 (there isn't - those are conceptual). The repo's `retire` code is in the research registry (supersession), not the live layer. Important distinction for downstream.

Let me now check the "model registry" / experiment tracking with registry.db schema. Already know: training_runs, prediction_sets, backtest_runs, cohort_metrics, official_populations, prediction_coverage. Good.

Now I have all 6 areas. Let me compose the structured report. I should be technical and concrete.

Let me quickly read chapter_26 lines 390-430 for recovery protocol to complete circuit breaker lifecycle. And check 05_feast for FeatureViewSpec / lineage. I already have symbols. Let me do one final read of circuit recovery + safe rollout A/B/staged gates lines 620-666. Actually I have enough from 03 file: PromotionCriteria, shadow, promotion_checks, REJECT. The A/B and staged are in the notebook before line 420 likely. Let me grep the staged allocation.

I'll do a final parallel grep for staged allocation / capital_cap / A/B and read breaker recovery.
One final pass: breaker recovery protocol and the A/B / staged-rollout gate code.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md</path>
<type>file</type>
<content>
390: 
391: ### Recovery procedures
392: 
393: Tripping a circuit breaker is the beginning, not the end. You need clear recovery protocols, grouped as the immediate response, investigating the problem, and resuming trade.
394: 
395: **Immediate actions**:
396: 
397: 1. **Acknowledge the alert**, using PagerDuty, Slack, or whichever platform you use.
398: 2. **Assess the situation**: What triggered the breaker? What’s the current exposure?
399: 3. **Secure the position**: If you are partially exposed, decide whether to close or hedge.
400: 
401: **Diagnostic questions**:
402: 
403: - Was this a technical failure (data feed, execution system) or model failure (wrong predictions)?
404: - Is 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 13 match(es) in 1 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/03_safe_model_rollout.py
  29: # - Reject a challenger that misses a fixed promotion hurdle without exposing capital.
  36: # This example deliberately ends at rejection. A safe rollout does not owe every challenger an A/B
  37: # test or staged capital. Those steps become eligible only after every shadow criterion passes.
  319: return pd.DataFrame(rows).sort_values(["model", "timestamp"]).reset_index(drop=True)
  350: .reset_index(drop=True)
  356: # ## 3. Observe the challenger without capital
  372: ).reset_index()
  433: # The shadow summary contains only hypothetical returns. No allocation or capital path is computed.
  548: {criteria.min_sharpe_improvement:.2f} promotion threshold. The challenger recei
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 41 match(es) in 5 file(s)

/home/georg/projects/ml4t-zh/26_mlops_governance/06_mlflow_experiments.py
  27: # - Reconstruct a searchable run catalog from `training_runs`,
  28: #   `prediction_sets`, and `backtest_runs`.
  70: REGISTRY_PATH = CASE_DIR / "run_log" / "registry.db"
  125: # tables: `training_runs`, `prediction_sets`, `prediction_metrics`,
  126: # `backtest_runs`, and `backtest_metrics`.
  136: training_runs = query_table(
  139: FROM training_runs
  145: backtest_runs = query_table(
  149: FROM backtest_runs br
  150: JOIN prediction_sets ps ON br.prediction_hash = ps.prediction_hash
  151: JOIN training_runs tr ON ps.training_hash = tr.training_hash
  157: print(f"Training runs loaded: {len(training_runs):,}")
  158: print(f"Backtest runs loaded: {len(backtest_runs):,}
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:22:09Z


> [reasoning] I now have everything needed. Let me compose the final structured technical report. I should be concrete, path/symbol focused, and address the 6 requests. Note key nuances:

- `ml4t-live` is a PyPI package (not vendored); uv.lock lists ml4t_live-0.1.0. Public API documented through notebook imports.
- The "retrain/pause/retire" feedback loop is a README conceptual diagram; code implements pieces: drift detection, promotion gates, circuit breakers (pause/halt), but no unified retrain/pause/retire orchestrator. Model retirement exists only at the research registry level (supersession), not the live plane.
- No SHAP implementation in Ch26 py; PSI/KS manual.
- Evidently not used; Feast + MLflow used; custom drift/breakers.
- Pre-deployment gates: 25/08 pipeline verification (test_parity_gate, exit codes), scripts/pre_run_gate.py (research run gate), safe rollout PromotionCriteria (model promotion gate), SafeBroker.connect() reconciliation (startup gate).

Let me write the report. Keep under ADHD-friendly but this is a technical investigation so thorough is fine. Use the required <results> block. Cap lists at 5 per AGENTS.md - but this is a search specialist report; I'll use sections and keep lists manageable. The instructions say cap lists at 5; I'll try to respect but the content demands more. I'll organize by the 6 questions.

Let me write it.
<analysis>
**Literal Request**: Map ml4t's production/MLOps/governance/live layer with concrete paths and symbols.
**Actual Need**: A mechanism inventory to port into AlphaMill's monitoring/attribution/lifecycle + Freqtrade safety controls.
**Success Looks Like**: Absolute paths, class/function names, config keys, and a clear statement of what is code vs. conceptual.
</analysis>

# ml4t Production Track — Technical Map

Key framing fact up front: **Ch25/26 are notebook chapters built on the external PyPI package `ml4t-live` (declared in `pyproject.toml:66`, pinned in `uv.lock:4530`, `ml4t_live-0.1.0`).** The package source is **not vendored** in this repo (no `ml4t/live` tree exists locally; `envs/ml4t/` contains only a Dockerfile). Everything below is either (a) notebook code that calls `ml4t.live`, or (b) teaching implementations of concepts the library is stated to productionize.

---

## 1. `25_live_trading/` — research-to-production bridge

All paths under `/home/georg/projects/ml4t-zh/25_live_trading/`.

**Unified engine / broker integrations**
- `01_unified_framework_demo.py` — same `DualMAStrategy` run through `ml4t.backtest.Engine` and `ml4t.live.LiveEngine`; asserts 9/9 signal parity. Imports `LiveEngine, SafeBroker, LiveRiskConfig, VirtualPortfolio` (`:82`).
- `03_ib_paper_trading_demo.py` — IB path: `from ml4t.live.brokers.ib import IBBroker` (`:96`), `from ml4t.live.feeds import BarAggregator, IBDataFeed` (`:97`), `from ml4t.live.safety import SafeBroker` (`:98`); `build_live_stack()` at `:411`.
- `04_alpaca_paper_trading_demo.py` — `AlpacaBroker, AlpacaDataFeed, LiveEngine, LiveRiskConfig` (`:71`); `create_safe_broker()` `:366`, `create_alpaca_engine()` `:516`.
- `05_alpaca_crypto_live_demo.py` — same Alpaca API, crypto subset; `CryptoPremiumStrategy` `:271`, `create_alpaca_crypto_engine()` `:509`.
- `09_crypto_funding_deployment_loop.py` — split venue: OKX data (public REST, `fetch_okx_candles_1h` `:325`, `fetch_okx_funding_history` `:428`), Alpaca execution (`AlpacaBroker` `:501`).
- `11_fx_deployment_loop.py` / `12_ib_basket_rebalance_demo.py` — IB as data+execution plane; `reconcile()` `:534`, `dry_run_basket()` `:581`, `execution_summary()` `:715`.
- `06_quantconnect_case_study.py` — prediction-bridge export only (no live API); LEAN class methods `initialize`/`_select_assets`/`_rebalance` (`:346`+). Registry hash guard at `:90-176`.

**Order lifecycle management** — `07_order_state_machine.py`
- `OrderState(Enum)` (`:70`): 10 states `PENDING_NEW, NEW, ACCEPTED, PARTIALLY_FILLED, PENDING_CANCEL, FILLED, CANCELED, REJECTED, EXPIRED, SUSPENDED`; property helpers `is_terminal`, `is_active`, `can_cancel`.
- `OrderEvent(Enum)` (`:149`): 9 events.
- `VALID_TRANSITIONS: dict[OrderState, dict[OrderEvent, OrderState]]` (`:178`) — 19 edges. Notable: `PENDING_CANCEL → FILLED` and `→ ACCEPTED` model the cancel/fill race; `SUSPENDED → ACCEPTED`.
- `StateTransition` dataclass (`:272`), `Order` dataclass with `apply_event()` (`:318`), `_validate_fill()` (`:381`), `log_transition()` (`:427`). Uses idempotent client order IDs. **Replace/modify flows are explicitly deferred to `ml4t.live.safety`** (`:172`).

**Pipeline verification / pre-deployment gate** — `08_pipeline_verification.py`
- `VerificationResult` dataclass (`:102`) with `skipped` / `expected_difference` flags; `EXPECTED_DIFFERENCE: set[str] = set()` (`:116`).
- Pure deterministic decision functions: `compute_features` `:126`, `compute_prediction` `:145`, `compute_signal` `:161`, `compute_size` `:175`, `fill_record` `:188`, `process_symbol` `:220`.
- Staged parity checks: `pipeline_results()` (`:761`) and `execution_results()` (`:792`) → `run_verification_tests()` (`:823`).
- **Release gate** `test_parity_gate(results)` (`:931`): all-skipped ⇒ raises (cannot promote); `EXPECTED_DIFFERENCE` informational; any gated failure raises. CI summary computes `exit_code` and prints `[FAIL] LIVE PIPELINE NOT EXECUTED` vs `[OK] ALL GATED VERIFICATION TESTS PASSED` (`:898-914`).

**Operational readiness** — `10_safety_risk_demo.py`, `13_runtime_safety_showcase.py`
- `10_`: exercises `SafeBroker` + `LiveRiskConfig` + `RiskLimitError` + `VirtualPortfolio` (`:75`); `MockBroker` with `execution_capabilities` / `assert_paper_trading` query surface (`:121-150`). Config keys seen: `execution_mode`, `max_order_shares`, `max_order_value`, `max_position_value`, `max_position_shares`, `max_total_exposure`, `state_file`.
- `13_`: stale-data rejection via `max_data_staleness_seconds`; kill-switch latch across `SafeBroker` reconstruction; `SafeBroker.connect()` startup reconciliation; `LiveEngine.runtime_status()` health states `stopped / ok / waiting_for_data / feed_silent / idle_market_closed / broker_disconnected`. Uses `RiskState` (`:78`). `_DummyStrategy`/`_ToyFeed` harness `:512+`.

There is **no operational-readiness checklist class**. The checklist is prose in `chapter_25.md:487-497` (5 startup gates: runtime env, auth, algo state coherence, market context, config/risk limits) and the executable gate is `08_pipeline_verification.py` plus the library runtime contract.

---

## 2. `26_mlops_governance/` — failure taxonomy, drift, rollout, breakers, infra

**Failure taxonomy** — prose only, `chapter_26.md:30-54`. Table 26.1:
- Technical (same inputs → different outputs) → fix bug (verification, Ch25).
- Statistical (same inputs → same outputs → poor returns) → retrain / redesign / retire.
Four decay mechanisms enumerated: overfitting, look-ahead bias, regime change, alpha decay.

**Drift detection** — `01_drift_monitoring.py`, `02_online_drift_detection.py`
- Manual, no Evidently. `compute_psi(reference, current, n_bins, epsilon)` (`:317`), `DriftMetric` dataclass `name/psi/ks_stat/ks_pvalue/.../status` (`:346`), `summarize_feature_drift()` (`:373`) with thresholds **PSI ≥ 0.25 = ALERT, ≥ 0.10 (or ≥0.02 + K-S p < `KS_WATCH_PVALUE`) = WATCH, else OK** and `scipy.stats.ks_2samp`.
- Rolling IC / hit-rate / MSE on the holdout stream (`:450-479`), 63-day window, backtest-vs-live realization ratios.
- Online concept drift: `ADWINStyle` (`:312`, two-window mean shift), `DDM` (`:349`), `DetectorSummary` (`:388`), `run_adwin_stream` (`:426`), `run_ddm_stream` (`:449`). `ml4t.diagnostic.validation.DataFrameValidator` used at `01:59`.
- SHAP feature-drift is discussed in `chapter_26.md:24,520` but **not implemented in any `.py`** (grep for `shap` hits only `.shape`). No Evidently/Alibi/river.

**Safe model rollout** — `03_safe_model_rollout.py`
- `PredictionIdentity` (`:90`), registry readers `open_registry_readonly`, `load_fixed_prediction_identity`, `load_predictions`.
- Shadow mode: `build_portfolio_stream` (`:268`), `annualized_sharpe` (`:383`), `max_drawdown` (`:396`).
- **Promotion gate** `@dataclass(frozen=True) PromotionCriteria` (`:460`): `min_sharpe_improvement=0.20`, `min_observation_days=63`, `min_signal_correlation=0.30`, `min_position_agreement=0.30`, `max_drawdown_ratio=1.25`. `promotion_checks` DataFrame (`:492`) is a conjunction; `rollout_decision = "PROMOTE" if ... else "REJECT"` (`:537`) and the notebook deliberately asserts `REJECT`. A/B and staged capital are **eligibility steps after all shadow criteria pass** (`:36-37`, `:660-663`) — not executed in the notebook.

**Circuit breakers** — `04_circuit_breakers.py` (custom state machine; `pybreaker` only recommended for infra)
- `BreakerState(Enum)`: `CLOSED / OPEN / HALF_OPEN` (`:81`).
- `BreakerEvent` dataclass (audit trail: `timestamp, breaker_name, old_state, new_state, reason, value, threshold`) (`:96`).
- `transition_breaker()` (`:114`) and `advance_breaker_state()` (`:152`) — OPEN→HALF_OPEN after `recovery_timeout`.
- `CircuitBreaker(ABC)` (`:189`) with `update`, `reset`, `is_open`, `allows_trading`, abstract `check_condition`.
- Concrete: `DrawdownBreaker` (`:251`, default 10%), `DailyLossBreaker` (`:290`, 2%, `reset_day`), `ConsecutiveLossBreaker` (`:338`, N=5, `record_trade`), `LatencyBreaker` (`:381`, 100 ms, `record_latency`, rolling last-10 mean).
- `BreakerManager` (`:463`): `add_breaker`, `check_all` (AND of `allows_trading`), `get_status`, `reset_all`, `event_log`; `on_any_trip` wiring at `:431-454`; `alert_handler` (`:511`) emits first trip per breaker.
- Configured set at `:525-558`: `drawdown_10pct` (4h recovery), `daily_loss_2pct` (1h), `consecutive_5` (30m), `latency_100ms` (5m).
- Recovery discipline is prose only (`chapter_26.md:391-424`): acknowledge/assess/secure → diagnose technical vs model → resume criteria → gradual restart → logged, time-limited manual overrides.

**Feature store** — `05_feast_feature_store.py`, `05b_feast_live.py`
- Manual implementation first: `FeatureViewSpec` (`:82`), `offline_join()` (`:218`), `latest_model_snapshot()` (`:305`), `leaked_snapshot()` (`:335`) to quantify training-serving skew.
- `05b_`: real Feast (`from feast import Entity, FeatureStore, FeatureView, Field, FileSource` `:86`), `polars_offline_join()` (`:364`), temp registry, offline/online parity vs manual (6/7 exact). Requires `feast>=0.40`.

**Experiment tracking / registry** — `06_mlflow_experiments.py`
- Reads the SQLite case-study registry `run_log/registry.db` tables `training_runs`, `prediction_sets`, `prediction_metrics`, `backtest_runs`, `backtest_metrics` (`:125-151`).
- `query_table()` (`:130`); MLflow at `:440+`: `mlflow.set_tracking_uri("sqlite:///.../mlflow.db")`, `set_experiment`, `start_run`, `log_params`, `log_metrics`, `log_artifact`, `mlflow.search_runs`. `log_catalog_to_mlflow()` (`:477`) logs 50 runs and verifies ranking parity.

---

## 3. Kill-switch / circuit-breaker / retire / pause logic repo-wide

Searched `kill_switch|circuit_breaker|retire|pause` across the repo.

- **Live kill switch**: `SafeBroker` in `ml4t-live` (external), surfaced in `25/10_safety_risk_demo.py`, `25/13_runtime_safety_showcase.py`, and `chapter_25.md:516` — daily-loss latch persisted to a state file and reloaded on reconnect. This is the only true live kill switch.
- **Circuit breakers**: only `26/04_circuit_breakers.py` (custom, per notebook). Ch19 risk overlays (`19_risk_management/10_ml4t_backtest_risk_demo.py`) have `MaxPositionsLimit`, `GrossExposureLimit` that `halts` new trading — a backtest-time analogue.
- **Pause/retire**: there is **no pause/retire controller in the live or MLOps layer.** "Retire" as executable code lives only in the **research registry supersession** system:
  - `/home/georg/projects/ml4t-zh/case_studies/research/population.py` — `retired_prediction_hashes(connection)` (`:37`), `RetirementSplit` (`:482`), `split_retired_members()` (`:494`), `superseded_members()` (`:576`), `_retired()` (`:648`), `superseded_members_at()` (`:743`).
  - Tests: `tests/test_candidate_index_retirement.py`, `tests/test_carrier_retired_generations.py`, `tests/test_retired_prediction_hashes.py`, `tests/test_superseded_members_registries.py`.
- `retrain` cadence is a config decision (monthly refit in `25/02_etfs_deployment_loop.py:~752`), not an automated trigger. `chapter_26.md:252-259` describes scheduled vs triggered retraining, but no code wires drift alerts to retraining.

---

## 4. `ml4t-live` library: vendored vs installed + public API

- **Installed, not vendored.** `pyproject.toml:66` → `ml4t-live>=0.1.0`; `uv.lock:4530-4543` resolves `ml4t_live-0.1.0` (wheel + sdist from PyPI). No local package tree.
- **Public API called by notebooks** (`ml4t.live` root): `LiveEngine`, `LiveRiskConfig`, `SafeBroker`, `VirtualPortfolio`, `RiskState`, `RiskLimitError`, `AlpacaBroker`, `AlpacaDataFeed`.
- **Submodules**: `ml4t.live.brokers.ib.IBBroker`, `ml4t.live.brokers.alpaca.AlpacaBroker`, `ml4t.live.feeds.{BarAggregator, IBDataFeed}`, `ml4t.live.safety.{SafeBroker, VirtualPortfolio}`, `ml4t.live.engine.LiveEngine`, `ml4t.live.protocols.ExecutionCapability`, `ml4t.live.wrappers.ThreadSafeBrokerWrapper`.
- **CLI** (`chapter_25.md:525-535`): `ml4t-live status` (reads persisted state: daily-loss counter, kill-switch latch, positions, pending orders) and `ml4t-live shadow <strategy>` (bounded shadow run reporting `ok/waiting_for_data/feed_silent/idle_market_closed/broker_disconnected`).

---

## 5. Live monitoring → retraining feedback loop

The README diagram (`README.md:35-41`) advertises a "retrain/pause/retire" loop, but the **code is a contract, not an orchestrator**:

1. Each deployment loop writes a **run record JSON** — `25/02_etfs_deployment_loop.py:685-723` (`run_record`), also `25/09` and `25/11`. Fields include `data_range`, `artefact_dir`, config, `backtest_*`, `execution_plane`, and the **four-bucket disposition** `intended_basket / attempted_basket / accepted_basket / failed_basket` (`:711-714`). The code explicitly calls this "the Ch26 monitoring contract" (`:739`).
2. Ch26 monitors those artifacts: PSI/K-S drift (`01_`), ADWIN/DDM (`02_`), rolling IC/hit-rate, prediction PSI.
3. Response is manual/notebook-gated: shadow → `PromotionCriteria` (`03_`) → (optional) A/B → staged 10%→25% allocation. Retraining is a schedule decision (`chapter_26.md:256-259`), not wired to drift alerts.
4. `scripts/pre_run_gate.py` is the **pre-retrain execution gate** (see §6), and `case_studies/research/population.py` retires superseded prediction generations.

So the loop is: deployment run-record → drift/perf monitoring → promotion gate → operator-triggered refit; retirement is registry supersession. There is **no automated retrain trigger or unified lifecycle state machine**.

---

## 6. Pre-deployment / operational-readiness gate code

Two concrete gates plus a promote gate:

- **Technical parity gate** — `25_live_trading/08_pipeline_verification.py`, `test_parity_gate()` (`:931`) / `run_verification_tests()` (`:823`); fails closed on skip; emits CI `exit_code`.
- **Research pre-run gate** — `/home/georg/projects/ml4t-zh/scripts/pre_run_gate.py`: `Report`/`Check` dataclasses (`:39-66`), `check_configurations` (`:74`, resolve-path identity agreement), `check_fold_preparation` (`:118`), `check_preview_run` (`:191`), `_inspect_registry` (`:255`), `check_the_run_is_costed` (`:361`), `check_registry_ready` (`:466`), `check_notebook_is_current/`_prose` (`:520`,`:535`); `main()` returns 0/1 with `--json` report.
- **Model promotion gate** — `26_mlops_governance/03_safe_model_rollout.py`, `PromotionCriteria` (`:460`) + `promotion_checks` conjunction (`:492`).
- **Startup runtime gate** — `SafeBroker.connect()` reconciliation report (`chapter_25.md:521`, driven in `25/13_runtime_safety_showcase.py`); launcher must refuse to start on a non-clean report.

<results>
<files>
- /home/georg/projects/ml4t-zh/25_live_trading/07_order_state_machine.py - OrderState/OrderEvent/VALID_TRANSITIONS: the 10-state, 19-edge lifecycle to mirror in the execution plane
- /home/georg/projects/ml4t-zh/25_live_trading/08_pipeline_verification.py - fail-closed parity gate (test_parity_gate) for backtest-vs-live technical divergence
- /home/georg/projects/ml4t-zh/25_live_trading/13_runtime_safety_showcase.py - stale-data, persisted kill-switch latch, startup reconciliation, LiveEngine health states
- /home/georg/projects/ml4t-zh/25_live_trading/02_etfs_deployment_loop.py - run_record contract and four-bucket basket disposition feeding Ch26
- /home/georg/projects/ml4t-zh/25_live_trading/10_safety_risk_demo.py - SafeBroker risk-control surface (order/position/rate/asset/kill-switch/shadow)
- /home/georg/projects/ml4t-zh/26_mlops_governance/04_circuit_breakers.py - CLOSED/OPEN/HALF_OPEN breakers + BreakerManager audit log
- /home/georg/projects/ml4t-zh/26_mlops_governance/03_safe_model_rollout.py - PromotionCriteria promotion gate; shadow-first rollout
- /home/georg/projects/ml4t-zh/26_mlops_governance/01_drift_monitoring.py - PSI/K-S + rolling IC/hit-rate; PSI thresholds 0.10/0.25
- /home/georg/projects/ml4t-zh/26_mlops_governance/02_online_drift_detection.py - ADWINStyle and DDM online concept-drift detectors
- /home/georg/projects/ml4t-zh/26_mlops_governance/05_feast_feature_store.py - point-in-time join, training-serving skew, lineage
- /home/georg/projects/ml4t-zh/26_mlops_governance/06_mlflow_experiments.py - MLflow logging over the registry.db run catalog
- /home/georg/projects/ml4t-zh/scripts/pre_run_gate.py - executable pre-retrain gate (config/fold/preview/cost/registry)
- /home/georg/projects/ml4t-zh/case_studies/research/population.py - the only retire mechanism (prediction-generation supersession)
- /home/georg/projects/ml4t-zh/25_live_trading/chapter_25.md - preflight checklist and 4-level kill-switch discipline (prose)
- /home/georg/projects/ml4t-zh/26_mlops_governance/chapter_26.md - failure taxonomy, breaker recovery, retrain cadence (prose)
</files>

<answer>
ml4t's production track is a notebook-and-library teaching stack, not a deployed system. The live plane is the external `ml4t-live` PyPI package (`SafeBroker`, `LiveRiskConfig`, `RiskState`, `VirtualPortfolio`, `LiveEngine`, `IBBroker`, `AlpacaBroker`) plus an `ml4t-live status|shadow` CLI. Its safety model is: (1) 8+ enforced pre-trade checks in `SafeBroker` with `RiskLimitError`; (2) a daily-loss kill switch persisted to a state file so it survives restarts; (3) `max_data_staleness_seconds` reject-on-stale; (4) `SafeBroker.connect()` startup reconciliation against a persisted snapshot; (5) `LiveEngine.runtime_status()` health states a watchdog can consume; (6) a fail-closed backtest/live parity gate (`test_parity_gate`) as the release check.

The MLOps plane is self-contained notebook code, not a platform. Detection = manual PSI/K-S + rolling IC/hit-rate + custom ADWIN-style/DDM (SHAP discussed, never coded; Evidently not used). Response = shadow mode then an all-must-pass `PromotionCriteria` gate (Sharpe lift >=0.20, >=63 days, signal corr >=0.30, position agreement >=0.30, DD ratio <=1.25); A/B and staged 10%->25% capital are described but not executed. Automated safety = a custom `CLOSED/OPEN/HALF_OPEN` breaker framework with Drawdown/DailyLoss/ConsecutiveLoss/Latency breakers and a `BreakerManager` event log; recovery and manual-override discipline are prose only. Supporting infra = hand-rolled feature-store joins plus real Feast, and MLflow layered over a local SQLite registry (`training_runs`, `prediction_sets`, `backtest_runs`, `cohort_metrics`).

Critical gap to note for AlphaMill: the README's "retrain/pause/retire" feedback loop is a diagram. Code implements drift detection, a promotion gate, and circuit-breaker halts, but the only *retire* mechanism lives in the research registry (prediction-generation supersession in `case_studies/research/population.py`), and no component automatically wires a drift/IC alert to retraining or strategy retirement. The "feedback loop" is the deployment `run_record` JSON (with its intended/attempted/accepted/failed basket disposition) as the monitoring contract, with a human closing the loop.
</answer>

<next_steps>
For AlphaMill design, reuse these concrete patterns and fill the gap:
1. Persistent latch state (mirror `SafeBroker` state file) so a kill switch survives a Freqtrade/process restart — never reset loss counters on reconnect.
2. Fail-closed parity gate as a CI promotion barrier (`test_parity_gate` semantics: skip == fail).
3. Multi-breaker manager with an append-only audit log and explicit `recovery_timeout` per breaker (`BreakerManager.event_log`).
4. `PromotionCriteria`-style fixed all-must-pass promotion gate, shadow-first, capital staged only after full pass.
5. Add the missing orchestrator: a drift/IC alert -> auto-pause vs auto-retrain trigger state machine, plus a registry-supersession retire step (ml4t has the retire primitive but no live trigger).

Ready to proceed — no follow-up needed.
</next_steps>
</results>
