---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f665ee612ffewlPli8XiMXca5y"
title: "ml4t AI agents and data layer (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-13T07:17:47Z"
updated_at: "2026-09-13T07:22:30Z"
tokens_input: 131533
tokens_output: 14893
cost: 0.0353
parent_id: "ses_f6664247effe4SLb37r5OF4RZ9"
---

# ml4t AI agents and data layer (@explore subagent)

## user · 2026-09-13T07:17:47Z

[CONTEXT] I am analyzing /home/georg/projects/ml4t-zh ("Machine Learning for Trading, 3rd Edition" code). It has a Generative-AI / agent track (Ch22 RAG, Ch23 knowledge graphs, Ch24 autonomous agents) and a data-engineering layer (Ch2 data universe, Ch3 microstructure, ml4t-data / ml4t-engineer libraries). I am comparing with AlphaMill, a new AI-factor-factory-led crypto quant pipeline that uses agents to generate factor hypotheses and a DuckDB/Parquet lake for data.

[GOAL] Two things: (A) how ml4t designs AUTONOMOUS / MULTI-AGENT financial research systems and agent "skills" (task recipes with guards); (B) how ml4t handles DATA ENGINEERING and leakage-safe feature/label preparation. Concrete paths, function/class names, schemas, protocols.

[DOWNSTREAM] I will recommend (A) how AlphaMill should structure its AI factor-generation agents, tool contracts, memory, and auditability; (B) what data-quality and leakage guards AlphaMill's data bridge should enforce.

[REQUEST] Investigate and report paths + symbols + mechanism:
A. Agents:
1. 24_autonomous_agents/: ReAct / Tree-of-Thoughts / Reflexion, memory systems, tool contracts, LangGraph/Claude SDK stack, a stateful equity-research agent, multi-agent forecasting with adversarial debate, production reliability. Find the actual agent classes, state schemas, tool definitions.
2. 22_rag_financial_research/ and 23_knowledge_graphs/: retrieval architecture, embeddings, hybrid retrieval + re-rank, graph RAG, temporal-leakage prevention. Key components.
3. The "61 agent skills" concept: is there any skills directory or skill-template code in the repo (search for skill, SKILL.md, agent recipe)? How are guards (lookahead, leakage, multiple testing) encoded into skills?
B. Data:
4. 02_financial_data_universe/: data-quality framework, storage benchmarks (Parquet/DuckDB/TimescaleDB), survivorship bias quantification.
5. ml4t-data and ml4t-engineer libraries: vendored or installed? Public API notebooks call; especially leakage-safe dataset preparation, alternative bars (dollar/volume bars), point-in-time handling.
6. Any point-in-time / bitemporal / lookahead-prevention utilities shared across the repo.

Report structured, technical, with concrete file paths and symbol names. Skip plotting.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-13T07:17:47Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 2 -type d 2>/dev/null | sort"})`
- **tool**: `glob({"pattern": "**/*.md", "path": "/home/georg/projects/ml4t-zh"})`


> [reasoning] The user wants me to investigate a repository at /home/georg/projects/ml4t-zh. This is outside my working directory (/home/georg/projects/alphamill), but I can read files. Let me start exploring.

Let me launch parallel searches.
<analysis>
**Literal Request**: Map concrete paths, symbols, and mechanisms in ml4t-zh for (A) autonomous/multi-agent systems + RAG/KG + "agent skills" guards, and (B) data engineering + leakage-safe feature/label prep (Ch2, ml4t-data, ml4t-engineer).

**Actual Need**: Extract design patterns AlphaMill can copy: agent architecture, tool contracts, memory, auditability from ml4t; and data-quality/leakage guards for its DuckDB/Parquet bridge.

**Success Looks Like**: Absolute paths + class/function names + schemas/protocols for each of the 6 sub-questions, so AlphaMill recommendations can cite real ml4t mechanisms.
</analysis>

I'll investigate in parallel. First, orient on the repo structure.

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
Found 100 file(s)

/home/georg/projects/ml4t-zh/24_autonomous_agents/chapter_24_zh.md
/home/georg/projects/ml4t-zh/25_live_trading/chapter_25_zh.md
/home/georg/projects/ml4t-zh/20_strategy_synthesis/chapter_20_zh.md
/home/georg/projects/ml4t-zh/22_rag_financial_research/chapter_22_zh.md
/home/georg/projects/ml4t-zh/18_transaction_costs/chapter_18_zh.md
/home/georg/projects/ml4t-zh/17_portfolio_construction/chapter_17_zh.md
/home/georg/projects/ml4t-zh/14_latent_factors/chapter_14_zh.md
/home/georg/projects/ml4t-zh/16_strategy_simulation/chapter_16_zh.md
/home/georg/projects/ml4t-zh/13_dl_time_series/chapter_13_zh.md
/home/georg/projects/ml4t-zh/11_ml_pipeline/chapter_11_zh.md
/home/georg/projects/ml4t-zh/12_gradient_boosting/chapter_12_zh.md
/home/georg/projects/ml4t-zh/10_text_feature_eng
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:17:50Z

- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/24_autonomous_agents -type f | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/22_rag_financial_research /home/georg/projects/ml4t-zh/23_knowledge_graphs -type f | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh/02_financial_data_universe -type f | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -iname \"*skill*\" -o -iname \"SKILL.md\" -o -iname \"*agent_recipe*\" 2>/dev/null | sort"})`


> [reasoning] Let me explore the key directories in detail: 24_autonomous_agents, 22_rag, 23_kg, 02_financial_data_universe, and search for skills.
Now let me explore the key chapter directories and search for skills in parallel.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/24_autonomous_agents/01_react_reasoning.ipynb
/home/georg/projects/ml4t-zh/24_autonomous_agents/01_react_reasoning.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/02_tool_contracts.ipynb
/home/georg/projects/ml4t-zh/24_autonomous_agents/02_tool_contracts.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.ipynb
/home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/04_research_agent.ipynb
/home/georg/projects/ml4t-zh/24_autonomous_agents/04_research_agent.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/05_aggregation_math.ipynb
/home/georg/projects/ml4t-zh/24_autonomous_agents/05_aggregation_math.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/06_multi_agent_
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.ipynb
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py
/home/georg/projects/ml4t-zh/22_rag_financial_research/02_domain_embeddings_comparison.ipynb
/home/georg/projects/ml4t-zh/22_rag_financial_research/02_domain_embeddings_comparison.py
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.ipynb
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py
/home/georg/projects/ml4t-zh/22_rag_financial_research/04_ragas_evaluation.ipynb
/home/georg/projects/ml4t-zh/22_rag_financial_research/04_ragas_evaluation.py
/home/georg/projects/ml4t-zh/22_rag_financial_research/05_10k_rag_assistant.ipynb
/home/georg/projects/ml4t-zh/22_rag_financial_resear
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/02_financial_data_universe/01_us_equities_eda.ipynb
/home/georg/projects/ml4t-zh/02_financial_data_universe/01_us_equities_eda.py
/home/georg/projects/ml4t-zh/02_financial_data_universe/02_corporate_actions.ipynb
/home/georg/projects/ml4t-zh/02_financial_data_universe/02_corporate_actions.py
/home/georg/projects/ml4t-zh/02_financial_data_universe/03_etfs_eda.ipynb
/home/georg/projects/ml4t-zh/02_financial_data_universe/03_etfs_eda.py
/home/georg/projects/ml4t-zh/02_financial_data_universe/04_cme_futures_eda.ipynb
/home/georg/projects/ml4t-zh/02_financial_data_universe/04_cme_futures_eda.py
/home/georg/projects/ml4t-zh/02_financial_data_universe/05_futures_session_aggregation.ipynb
/home/georg/projects/ml4t-zh/02_financial_data_universe/05_futures_session_aggreg
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
(no output)

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-13T07:17:53Z

- **tool**: `grep({"pattern": "(?i)\\b(skill|skills|agent recipe|61)\\b", "path": "/home/georg/projects/ml4t-zh", "include": "*.md", "output_mode": "content", "head_limit": 80})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -type d -iname \"*skill*\" -o -type d -iname \"*.claude*\" -o -type d -iname \"*agent*\" 2>/dev/null | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/ml4t-zh -maxdepth 3 -iname \"*.py\" -path \"*agent*\" 2>/dev/null | sort; echo \"---ML4T LIBS---\"; find /home/georg/projects/ml4t-zh -maxdepth 4 -iname \"*ml4t*\" 2>/dev/null | sort"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/ml4t-zh/.claude 2>/dev/null; ls -la /home/georg/projects/ml4t-zh/.github 2>/dev/null; find /home/georg/projects/ml4t-zh -maxdepth 2 -name \"AGENTS.md\" -o -maxdepth 2 -name \"CLAUDE.md\" 2>/dev/null"})`


> [reasoning] No SKILL.md files. Let me search for "skill" text and "61" agent skills. Also look at the READMEs and key files.

Let me read the key agent files. I'll do a large parallel read.
No `SKILL.md` files. Let me search for the "61 agent skills" concept and read the core agent modules.

  <details><summary>tool output</summary>

  ```text
Found 80 match(es) in 30 file(s)
[Output truncated due to size limit]

/home/georg/projects/ml4t-zh/03_market_microstructure/README.md
  40: - [`13_algoseek_minute_bars_eda`](13_algoseek_minute_bars_eda.ipynb) — This notebook provides a comprehensive exploration of the AlgoSeek TAQ minute bar dataset. Unlike simple OHLCV data, TAQ bars contain 61 pre-computed columns that capture the full microstructure of each trading minute: quote dynamics, trade execution, aggressor behavior, and liquidity conditions.

/home/georg/projects/ml4t-zh/03_market_microstructure/chapter_03.md
  132: **Enriched TAQ products** (for example, minute bars with precomputed microstructure fields) can help bridge part of this gap by incorporating trade-direction buckets, quote-pressure proxies, or off-exchange activit
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/24_autonomous_agents


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/24_autonomous_agents/01_react_reasoning.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/02_tool_contracts.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/04_research_agent.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/05_aggregation_math.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/06_multi_agent_research.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/07_adversarial_debate.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/08_forecasting_pipeline.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/10_framework_comparison.py
/home/georg/projects/ml4t-zh/24_autonomous_agents/11
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 28
drwxr-xr-x  5 georg georg 4096 Sep 10 00:21 .
drwxr-xr-x 42 georg georg 4096 Sep 12 01:44 ..
drwxr-xr-x  2 georg georg 4096 Sep 10 00:21 ci
-rw-r--r--  1 georg georg 2353 Sep 10 00:21 copilot-instructions.md
-rw-r--r--  1 georg georg 1247 Sep 10 00:21 dependabot.yml
drwxr-xr-x  2 georg georg 4096 Sep 10 22:39 scripts
drwxr-xr-x  2 georg georg 4096 Sep 10 23:16 workflows


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-13T07:17:58Z

- **tool**: `bash({"command": "wc -l /home/georg/projects/ml4t-zh/24_autonomous_agents/*.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_schemas.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_tools.py"})`


> [reasoning] Key finding: "61 agent skills" refers to an external repo github.com/ml4t/skills, not vendored. The chapter says "56 concept-first Markdown files organized into nine categories". README says 61 agent skills. So the skills are external. Let me read the relevant chapter sections and the code.

Let me now read the core Python modules in 24_autonomous_agents. Start with agent_schemas.py, agent_tools.py, agent_research.py, agent_specialists.py, agent_pipeline.py, research_operator.py. Also check sizes.
Key finding: skills live in external repo `github.com/ml4t/skills`. Now let me read the core agent modules in parallel.

  <details><summary>tool output</summary>

  ```text
519 /home/georg/projects/ml4t-zh/24_autonomous_agents/01_react_reasoning.py
   387 /home/georg/projects/ml4t-zh/24_autonomous_agents/02_tool_contracts.py
   598 /home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py
   789 /home/georg/projects/ml4t-zh/24_autonomous_agents/04_research_agent.py
   528 /home/georg/projects/ml4t-zh/24_autonomous_agents/05_aggregation_math.py
   583 /home/georg/projects/ml4t-zh/24_autonomous_agents/06_multi_agent_research.py
   678 /home/georg/projects/ml4t-zh/24_autonomous_agents/07_adversarial_debate.py
   800 /home/georg/projects/ml4t-zh/24_autonomous_agents/08_forecasting_pipeline.py
   707 /home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py
   991 /home/georg/projects/ml4t-zh/24_autonomous_agents/10_framework
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_schemas.py</path>
<type>file</type>
<content>
1: """Data schemas for the multi-agent forecasting pipeline.
2:
3: Plain dataclasses — no Pydantic dependency — so the teaching code stays
4: transparent and inspectable.
5: """
6:
7: from __future__ import annotations
8:
9: import json
10: from dataclasses import asdict, dataclass, field
11: from enum import Enum, StrEnum
12: from uuid import uuid4
13:
14: # ---------------------------------------------------------------------------
15: # Enums
16: # ---------------------------------------------------------------------------
17:
18:
19: class Sentiment(StrEnum):
20:     """Agent sentiment towards YES outcome."""
21:
22:     STRONGLY_BULLISH = "strongly_bullish"
23:     BULLIS
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_tools.py</path>
<type>file</type>
<content>
1: """Search provider abstraction and tool execution framework.
2:
3: Providers: Tavily (real web search), Mock (deterministic CI fallback).
4: No disk cache — teaching code stays transparent.
5: """
6:
7: from __future__ import annotations
8:
9: import os
10: import time
11: import warnings
12: from dataclasses import dataclass, field
13: from datetime import date, datetime, timedelta
14: from email.utils import parsedate_to_datetime
15: from typing import Any, Protocol, runtime_checkable
16: from urllib.parse import urlparse
17:
18: from agent_schemas import SearchResult
19:
20: # ---------------------------------------------------------------------------
21: # Protocol
22: # --
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:01Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_research.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_specialists.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_pipeline.py"})`


> [reasoning] Now let me read agent_research.py, agent_specialists.py, agent_pipeline.py, and research_operator.py. Also check the RAG and KG files. Let me do a batch.
Excellent detail. Now the research agent, specialists, pipeline, and operator.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_research.py</path>
<type>file</type>
<content>
1: """Research agent class and supporting utilities.
2:
3: Built step-by-step in NB04; downstream notebooks (NB06–NB08) import from here
4: rather than rebuilding the agent inline each time.
5: """
6:
7: from __future__ import annotations
8:
9: import json
10: import math
11: import re
12: from datetime import date
13:
14: from agent_providers import ChatMessage, LLMClient, TokenUsage
15: from agent_schemas import (
16:     AgentForecastArtifact,
17:     AgentTrace,
18:     EvidenceQuality,
19:     ForecastQuestion,
20:     SearchResult,
21:     Sentiment,
22: )
23: from agent_tools import SearchClient, ToolExecutor, format_search_results
24:
25: # -----------------------------
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_specialists.py</path>
<type>file</type>
<content>
1: """Specialist agent classes for the multi-agent forecasting pipeline.
2:
3: `DebateAgent` and `SupervisorAgent` are built step-by-step in NB07 and NB08
4: respectively; this module mirrors those classes for downstream notebooks
5: (NB10 framework comparison) that need to reuse the full pipeline.
6:
7: Each class is functionally identical to the inline version in its teaching
8: notebook. Prompts live here as module-level constants so all three frameworks
9: in NB10 can route the same text through their orchestrators.
10: """
11:
12: from __future__ import annotations
13:
14: from datetime import date
15:
16: from agent_providers import ChatMessage
17: from agent_research
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_pipeline.py</path>
<type>file</type>
<content>
1: """Aggregation math, calibration, and evaluation functions.
2:
3: Pure math only — no agent classes. Each agent class is built step-by-step in
4: its teaching notebook (NB04 ResearchAgent, NB07 DebateAgent, NB08 SupervisorAgent
5: and AIAForecaster) and mirrored in a helper module for downstream reuse:
6: ``agent_research`` for ResearchAgent and ``agent_specialists`` for DebateAgent
7: and SupervisorAgent.
8: """
9:
10: from __future__ import annotations
11:
12: import math
13: from collections.abc import Sequence
14: from dataclasses import dataclass
15:
16: from agent_schemas import AggregationResult
17:
18: # ---------------------------------------------------------------
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:04Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/research_operator.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_observability.py"})`


> [reasoning] Now the research_operator.py which has the 10 tools including list_skills / read_skill. Let me read it. Also agent_observability.py for trace/audit. And agent_providers.py for LLM abstraction.

Let me read those plus the RAG chapter key file 03_hybrid_retrieval.py and KG 03_graph_rag_qa.py.
Now the operator (skills tools) and observability, plus RAG/KG core modules.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/research_operator.py</path>
<type>file</type>
<content>
1: """ML4T Research Operator — one autonomous iteration on a real case study.
2:
3: A thin orchestrator (~600 lines) that loads case-study context, hands an LLM a
4: small set of general-purpose tools (registry SQL, file I/O, bash, parquet I/O,
5: skill discovery), and asks it to execute the §20.9 "what's next?" suggestion
6: for one of the chapter-20 case studies. The runtime is the deterministic ml4t
7: library stack; the discipline lives in the standalone skills repo at
8: `~/ml4t/skills`. The operator imports neither — both are reached through the
9: generic tool surface and discovered at run time.
10:
11: Sandbox: writes are confined to `ML4T_OUTPUT_DIR=$SANDBOX` so the pr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_observability.py</path>
<type>file</type>
<content>
1: """Agent observability: full-trace capture, persistence, and replay.
2:
3: Autonomous agents are only trustworthy if you can see what they did. This
4: module gives the forecasting notebooks a single, auditable record of every
5: run: the question, every prompt an agent received, every raw model response,
6: every search query and the documents it returned, and the structured forecast
7: that came out the other end.
8:
9: Three pieces, each independent:
10:
11: 1. ``TracingLLMClient`` wraps *any* ``LLMClient`` and records every call —
12:    the exact messages sent in and the raw text returned — without changing a
13:    line of agent logic. Because every agent in the cha
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:18:08Z

- **tool**: `bash({"command": "grep -nE \"^(class|def) |RRF|rerank|hybrid|BM25|leak|lookahead|point.in.time|cutoff|as_of|effective_date\" /home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py /home/georg/projects/ml4t-zh/22_rag_financial_research/05_10k_rag_assistant.py /home/georg/projects/ml4t-zh/22_rag_financial_research/08_rag_security.py 2>/dev/null | head -80"})`
- **tool**: `bash({"command": "grep -nE \"^(class|def) |leak|lookahead|point.in.time|cutoff|as_of|effective_date|temporal|valid_from|valid_to|bitemporal\" /home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py /home/georg/projects/ml4t-zh/23_knowledge_graphs/07_dynamic_kg_temporal.py /home/georg/projects/ml4t-zh/23_knowledge_graphs/02_supply_chain_kg_construction.py 2>/dev/null | head -80"})`
- **tool**: `bash({"command": "grep -nE \"ml4t.data|ml4t.engineer|ml4t-data|ml4t-engineer|ml4t\\.\" /home/georg/projects/ml4t-zh/pyproject.toml | head -60; echo \"=== installed ===\"; python3 -c \"import importlib.util as u; [print(m, bool(u.find_spec(m))) for m in ['ml4t','ml4t.data','ml4t.engineer']]\" 2>/dev/null; echo \"=== find site-packages ===\"; find / -maxdepth 8 -type d \\( -name \"ml4t\" -o -name \"ml4t_data*\" -o -name \"ml4t_engineer*\" \\) 2>/dev/null | head"})`
- **tool**: `bash({"command": "grep -nE \"^(class|def) \" /home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py /home/georg/projects/ml4t-zh/02_financial_data_universe/14_point_in_time_validation.py /home/georg/projects/ml4t-zh/02_financial_data_universe/15_survivorship_bias_detection.py /home/georg/projects/ml4t-zh/02_financial_data_universe/21_storage_benchmark_database.py 2>/dev/null"})`


> [reasoning] Now I have most of A. Let me look at the governance/evaluation piece (09) which covers point-in-time integrity, contamination-aware testing, Warden pattern. Also the multi-agent (06) and state/memory (03). But given output needs, let me grep for key symbols in the chapter 24 notebooks rather than read all.

Now for RAG (22) and KG (23). Let me read the key scripts. And data (02) data quality framework, point-in-time validation, survivorship.

Also find ml4t-data / ml4t-engineer libraries: are they vendored or installed? The pyproject may list them. Let me check.

Let me batch:
1. grep for classes/functions in 22 and 23
2. read 02 data quality framework sections
3. read 02 point_in_time_validation and survivorship
4. check pyproject for ml4t libs
5. read 07_10_ml4t_library_ecosystem.py for API

Let me do that.
Now RAG/KG components and data engineering. Let me grep for key symbols across those, and inspect library setup.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py:22:# This notebook demonstrates hybrid retrieval combining:
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py:25:# 2. **Keyword search (BM25)** - Sparse retrieval for exact matches
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py:26:# 3. **Reciprocal Rank Fusion (RRF)** - Combining ranked lists
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py:29:# - Implement a simple hybrid retrieval stack combining semantic and lexical search.
/home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py:30:# - Inspect when BM25, dense retrieval, and RRF succeed on different query types.
/home/georg/projects/ml4t-zh/22_rag_fina
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:38:# - Audit query validity, provenance coverage, and temporal filtering on live graph results
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:156:# Each template constrains the HOLDS vintage to `h.quarter <= $cutoff_date` and
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:158:# (`collect(h)[0]` after `ORDER BY h.quarter DESC`). This is the point-in-time
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:160:# cutoff, not the cross-product of every historical filing the institution made
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:168:  AND h.quarter <= $cutoff_date
/home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py:189:  AND
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
56:    # ml4t-data 0.1.2: HiveStorage.partitions() reports what a write committed, the anomaly
59:    "ml4t-data>=0.1.2",
64:    "ml4t-engineer>=0.1.3",
=== installed ===
ml4t False
=== find site-packages ===


<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py:86:def _to_date(value: object) -> object:
/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py:444:def calculate_psi(
/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py:551:def detect_gaps(df: pl.DataFrame, max_gap_days: int = 5) -> pl.DataFrame:
/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py:611:def detect_corporate_actions(df: pl.DataFrame, threshold: float = 0.25) -> pl.DataFrame:
/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py:678:def quality_check_pipeline(
/home/georg/projects/ml4t-zh/02_financial_data_universe/14_point_in_time_validation.py:144:def naive_leakag
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:20:12Z

- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/07_defining_the_learning_task/10_ml4t_library_ecosystem.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/02_financial_data_universe/14_point_in_time_validation.py", "limit": 460})`
- **tool**: `bash({"command": "grep -rniE \"leak|lookahead|look-ahead|point.in.time|as.of|knowledge.cutoff|future information|contaminat\" /home/georg/projects/ml4t-zh/22_rag_financial_research/*.py | head -60"})`
- **tool**: `bash({"command": "grep -rniE \"leak|lookahead|point.in.time|as_of|effective_date|availability|vintage|survivor|delist|restat\" /home/georg/projects/ml4t-zh/07_defining_the_learning_task/*.py /home/georg/projects/ml4t-zh/08_financial_features/*.py 2>/dev/null | head -70"})`


> [reasoning] The find / command timed out. Let me check the uv.lock / pyproject for ml4t-data, ml4t-engineer source. They're installed libraries (pip deps), not vendored. Let me check pyproject fully and the library ecosystem notebook.

Let me read:
- pyproject relevant section
- 07_defining_the_learning_task/10_ml4t_library_ecosystem.py (public API)
- 02 point_in_time_validation.py (PITValidator class)
- 02 data_quality_framework.py (quality check pipeline)
- 02 storage benchmarks (duckdb/parquet/timescale)

And RAG temporal-leakage: search across 22 for cutoff/date/leak. Let me grep chapter 22 for leakage. Also read the KG 07 leakage manifest.

Let me batch reads.
Libraries are pip deps (not vendored). Let me read the library ecosystem notebook, PIT validator, data-quality framework, and check RAG temporal controls.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/07_defining_the_learning_task/10_ml4t_library_ecosystem.py</path>
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
16: # %%
17: """The ml4t Library Ecosystem - unified data, feature, and diagnostic libraries for Chapters 7-12."""
18:
19: # %% [markdown]
20: # # The ml4t Library Ecosystem
21: #
22: # **Docker image**: `ml4t`
23: #
24: # **Chapter 7: Defining the Learning Task**
25: # **Section Reference**: 7.1 - D
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/02_financial_data_universe/14_point_in_time_validation.py</path>
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
17: # # Point-in-Time (PIT) Data Validation
18: #
19: # **Docker image**: `ml4t`
20: #
21: # ## Purpose
22: # Demonstrate the operational checks needed to keep a backtest free of
23: # lookahead bias on real ETF and macroeconomic data. Three threads run
24: # through the notebook: f
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:17:# # SEC Filing Discovery: Point-in-Time Metadata Integrity
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:25:#   the metadata fields a RAG system needs for point-in-time retrieval.
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:27:#   so downstream chunking and retrieval cannot accidentally leak the future.
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:118:# point-in-time filtering and citation formatting depend on.
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:190:# point-in-time mismatch rather than a retrieval bug. Fix it at the universe
/home/georg/projects/ml4t-zh/22
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/01_data_quality_diagnostics.py:335:# Visualizes data availability across time × asset for panel data.
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/01_data_quality_diagnostics.py:358:            dates at random, so a survivorship-free panel reads as a ragged skyline
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/01_data_quality_diagnostics.py:426:    # listing/delisting staircase reads as "where do we have data" rather than the reverse.
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/01_data_quality_diagnostics.py:793:# Longest dataset (56 years) with survivorship-free panel. Key concerns:
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/01_data_quality_diagnostics.py:794:# penny stocks
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:09Z

- **tool**: `bash({"command": "grep -nE \"^(from|import) ml4t|DataManager|HiveStorage|AnomalyDetector|def check|def calculate|class .*:\" /home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py | head -60; echo \"=== NB18/19 ===\"; grep -nE \"^(from|import) ml4t|DataManager|HiveStorage|Incremental|class .*:|def .*:\" /home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py /home/georg/projects/ml4t-zh/02_financial_data_universe/19_incremental_updates.py | head -50
…[truncated])`
- **tool**: `bash({"command": "grep -rniE \"dollar.?bar|volume.?bar|tick.?bar|imbalance.?bar|run.?bar|information.?driven|adv.?bar\" /home/georg/projects/ml4t-zh/08_financial_features/*.py /home/georg/projects/ml4t-zh/07_defining_the_learning_task/*.py /home/georg/projects/ml4t-zh/02_financial_data_universe/*.py 2>/dev/null | head -40"})`
- **tool**: `bash({"command": "grep -nE \"^(class|def) |RRF|rerank|chunk|embed|cutoff|filing_date|acceptance|knowledge\" /home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py /home/georg/projects/ml4t-zh/22_rag_financial_research/02_domain_embeddings_comparison.py /home/georg/projects/ml4t-zh/22_rag_financial_research/05_10k_rag_assistant.py /home/georg/projects/ml4t-zh/22_rag_financial_research/08_rag_security.py 2>/dev/null | head -90"})`
- **tool**: `webfetch({"url": "https://github.com/ml4t/skills", "format": "markdown"})`


> [reasoning] I have a lot. Let me now gather the remaining specifics:

1. Data quality framework (13) - the ml4t-data uses (DataManager, HiveStorage, anomaly), PSI. Let me grep imports and classes.
2. Storage benchmarks: DuckDB/Parquet/TimescaleDB/TimescaleDB results.
3. Survivorship bias quantification - check_survivorship_bias, check_universe_completeness, expected_terminal/Monte Carlo.
4. Alternative bars (dollar/volume bars) — search in 08_financial_features or ml4t-engineer.
5. Ch22 retrieval architecture components: chunking, embeddings, hybrid, rerank, ragas eval, security. Need concrete classes.
6. Ch23: KG construction, Graph RAG, temporal.
7. Also the "skills" guard encoding: the SKILL.md external repo. We can fetch it? The request asks "is there any skills directory or skill-template code in the repo". Answer: external repo. But maybe fetch the GitHub repo to describe skill format including guards. Let me webfetch github.com/ml4t/skills to confirm the categories and skill template. That would be valuable for downstream. Let me do that.

Let me also grep 08 for alternative bars / dollar bars / volume bars, and the ml4t-engineer registry.

Let me batch.
Let me gather data-quality/storage specifics, alternative bars, RAG component classes, and the external skills repo format.

  <details><summary>tool output</summary>

  ```text
62:from ml4t.data.anomaly import (
68:from ml4t.data.anomaly.config import (
74:from ml4t.data.validation import OHLCVValidator
444:def calculate_psi(
=== NB18/19 ===
/home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py:26:# - **DataManager**: Unified entry point for fetching, storing, and updating
/home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py:28:# - **HiveStorage**: Partitioned Parquet for fast queries and incremental writes
/home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py:29:# - **Incremental Updates**: Keep data fresh without re-downloading history
/home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py:35:# 1. Use `DataManager` as a single entry point for all data operations
/hom
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
(no output)

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:27:#   so downstream chunking and retrieval cannot accidentally leak the future.
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:28:# - State the parser-mode contract that downstream embedding and retrieval
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:122:def list_10k_filings(symbol: str, years: list[int]) -> dict:
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:130:        if filing.filing_date.year in years:
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py:134:                    "timestamp": filing.filing_date,
/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_fil
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
GitHub - ml4t/skills: Agent skills for Machine Learning for Algorithmic Trading: leakage-safe quant ML, backtesting, validation, and autonomous research workflows. · GitHub

[Skip to content](#start-of-content)



## Navigation Menu

[](/)

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fml4t%2Fskills)

Appearance settings

-   Platform

    -   AI CODE CREATION

        -   [GitHub CopilotWrite better code with AI](https://github.com/features/copilot)
        -   [GitHub Copilot appDirect agents from issue to merge](https://github.com/features/ai/github-app)
        -   [MCP RegistryIntegrate external tools](https://github.com/mcp)

    -   DEVELOPER WORKFLOWS

        -   [ActionsAutomate any
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:17Z

- **tool**: `webfetch({"format": "text", "url": "https://raw.githubusercontent.com/ml4t/skills/main/concepts/lookahead-bias/SKILL.md"})`
- **tool**: `webfetch({"format": "text", "url": "https://raw.githubusercontent.com/ml4t/skills/main/advanced-ai/agent-governance/SKILL.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/02_financial_data_universe/21_storage_benchmark_database.py", "limit": 120})`
- **tool**: `bash({"command": "grep -rniE \"dollar.?bar|volume.?bar|build_bars|tick.?bar|imbalance.?bar|run.?bar\" /home/georg/projects/ml4t-zh --include=*.py | head -30; echo \"=== labels ===\"; grep -nE \"^(from|import) ml4t|def .*barrier|triple|meta.?label|class .*Label\" /home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py | head -40"})`


> [reasoning] I now have the full skill catalog. Excellent. That answers the "61 agent skills" concept strongly. Let me fetch one skill template to show guard encoding e.g. lookahead-bias or data-leakage. Let me fetch the raw SKILL.md for lookahead-bias and agent-governance to show guard format. That's high value for downstream AlphaMill.

Also I still need:
- Storage benchmark results / mechanisms (DuckDB asof join, Parquet, TimescaleDB) - 21_storage_benchmark_database.py has duckdb_asof. Let me gather the class/function names and read the module docstring for numbers.
- Survivorship bias quantification: check_survivorship_bias, check_universe_completeness, Monte Carlo expected_terminal. Read those functions.
- Alternative bars "build-bars" is a skill; maybe implemented in 02 or 03. Search again more broadly for "dollar" in all repo py.
- ml4t-engineer compute_features + registry; labeling functions (triple barrier) - check 03_label_methods imports.
- RAG: hybrid retrieval classes done. Need reranker, ragas eval, security (Warden for agents is NB09).
- KG: construction (02), graph rag (03), temporal (07), features (09), portfolio (10).
- Point-in-time utilities shared: PITValidator, leakage_corr_scale_invariant, validate_signal_trade_lag, SplitAwarePreprocessor, pl.join_asof, PIT joins in preprocessing, visible_at_cutoff/leakage_test in KG, cutoff_date in RAG/operator.

Let me batch:
1. Read storage benchmark 21 docstring/functions and file benchmark 20.
2. Read survivorship functions.
3. grep "dollar bar|volume bar|build_bars|tick" across repo.
4. Fetch raw lookahead-bias SKILL.md and agent-governance.
5. Grep 03_label_methods for triple barrier implementation/library.

Let's go.
Full skill catalog captured. Let me get the skill template guards, storage benchmark specifics, survivorship quantification, and bar/label implementations.

  <details><summary>tool output</summary>

  ```text
---
name: ml4t-lookahead-bias
description: "Detect future information leaking into features, labels, or evaluation. Use when any pipeline step might expose data not yet available at prediction time."
when_to_use: "Use when computing features, creating labels, preprocessing data, or setting up cross-validation for time-series models"
dependencies: []
metadata:
  book_chapters: "6, 7"
  library: "ml4t-diagnostic"
---
# Lookahead Bias

The most common ML4T failure. A model uses future information during training - normalization with full-sample statistics, labels from future thresholds, standard k-fold CV on time series - producing a great backtest that fails immediately in production.

## The Problem

Lookahead bias means using information that would not have been available at
prediction tim
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
---
name: ml4t-agent-governance
description: "Security and governance controls for autonomous financial agents. Use when agents can call tools, read untrusted content, or affect research or trading decisions."
when_to_use: "Use when adding prompt-injection defenses, warden proxies, audit trails, approval gates, or production controls to agent workflows"
dependencies: [agent-tool-contracts, agent-state-memory]
metadata:
  book_chapters: "24, 25, 26"
  library: ""
paths: ["**/*governance*.py", "**/*warden*.py", "**/*safety*.py", "**/*risk*.py"]
---
# Agent Governance

Autonomous agents need defense in depth: policy enforcement before tool execution, audit trails after every action, and human approval before high-impact decisions.

## The Problem

Financial agents read adversarial documents,
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/02_financial_data_universe/21_storage_benchmark_database.py</path>
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
17: # # Storage Benchmark: Database Engines
18: #
19: # **Docker image**: `benchmark`
20: #
21: # > **Docker required**: This notebook depends on the `benchmark` environment and
22: # > database services. Run with:
23: # > ```bash
24: # > docker compose --profile benchmark up -d t
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== labels ===
35:# 3. Implement triple-barrier with fixed and ATR-based thresholds
64:from ml4t.engineer.config.labeling import LabelingConfig
65:from ml4t.engineer.labeling import (
66:    atr_triple_barrier_labels,
70:    meta_labels,
74:    triple_barrier_labels,
508:config = LabelingConfig.triple_barrier(
515:labels_tb = triple_barrier_labels(
533:# **Understanding triple-barrier requires seeing the price paths**.
543:def plot_triple_barrier_example(
546:    """Plot a single triple-barrier trade example with barriers overlaid."""
651:            fig = plot_triple_barrier_example(
690:# Use triple_barrier_labels with dynamic per-row percentage barriers
691:atr_config = LabelingConfig.triple_barrier(
697:labels_atr = triple_barrier_labels(
742:# Unlike simple forward-return labels, trip
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:23Z

- **tool**: `grep({"pattern": "dollar|volume_bar|build_bars|tick_bar|imbalance_bar", "path": "/home/georg/projects/ml4t-zh", "include": "*.py", "output_mode": "files_with_matches"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/02_financial_data_universe/15_survivorship_bias_detection.py", "offset": 960, "limit": 130})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py", "offset": 55, "limit": 70})`
- **tool**: `bash({"command": "grep -nE \"^(class|def) |Warden|PolicyDecision|injection|approval|contamination|point.in.time|repeat|trial|def _\" /home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py | head -80; echo \"=== 03 state ===\"; grep -nE \"^(class|def) |checkpoint|replay|quality_gate|schema_version|memory\" /home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py | head -60"})`


> [reasoning] Got the skill template. Now let me finish the remaining pieces:

1. Survivorship bias quantification functions - read the relevant sections of 15_survivorship_bias_detection.py (check_survivorship_bias, check_universe_completeness, run_monte_carlo/expected_terminal).
2. Alternative bars: search properly (zsh glob issue). Use grep tool.
3. Data quality framework: read key sections (ml4t.data.anomaly imports, quality_check_pipeline, PSI).
4. KG construction/RAG key classes (02, 03, 09, 10).
5. 22 RAG: ragas evaluation and security key components.
6. agent_providers.py, 03_state_and_memory, 09_evaluation governance (Warden). Grep for classes.
7. Point-in-time shared utilities: SplitAwarePreprocessor class details, join_asof usage in preprocessing.

Let me batch grep/read.
Let me finish: survivorship quantification, alternative bars, data-quality APIs, KG, and agent governance classes.

  <details><summary>tool output</summary>

  ```text
Found 112 match(es) in 112 file(s)

/home/georg/projects/ml4t-zh/06_strategy_definition/01_where_ideas_come_from.py

/home/georg/projects/ml4t-zh/05_synthetic_data/04_gtgan_irregular.py

/home/georg/projects/ml4t-zh/14_latent_factors/07_stochastic_discount_factor.py

/home/georg/projects/ml4t-zh/14_latent_factors/06_conditional_autoencoder.py

/home/georg/projects/ml4t-zh/14_latent_factors/02_eigenportfolios.py

/home/georg/projects/ml4t-zh/14_latent_factors/08_supervised_autoencoder.py

/home/georg/projects/ml4t-zh/04_fundamental_alternative_data/11_defi_tvl_evaluation.py

/home/georg/projects/ml4t-zh/22_rag_financial_research/07_institutional_holdings_graph.py

/home/georg/projects/ml4t-zh/04_fundamental_alternative_data/03_sec_form4_insider_transactions.py

/home/georg/projects/ml4t-zh/
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/02_financial_data_universe/15_survivorship_bias_detection.py</path>
<type>file</type>
<content>
960: # %% [markdown] tags=[]
961: # Leavers hold their shorter window and, over it, underperform the survivors. That is the
962: # mechanism behind the positive bias in §6: dropping them from the universe removes the weaker
963: # half of the distribution. The terminal-return scenarios then adjust the estimate at the
964: # margin — they do not create it.
965:
966: # %% [markdown] tags=[]
967: # ## 9. Detecting bias in your own data
968: #
969: # Two cheap tests. The first catches a universe filtered to today's constituents; the second
970: # catches the pattern this panel shows, where exits are recorded but only for part of the history.
971:
972:
973: # %%
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py</path>
<type>file</type>
<content>
55: from datetime import datetime
56: from pathlib import Path
57:
58: import numpy as np
59: import plotly.graph_objects as go
60: import polars as pl
61: import structlog
62: from ml4t.data.anomaly import (
63:     AnomalyManager,
64:     PriceStalenessDetector,
65:     ReturnOutlierDetector,
66:     VolumeSpikeDetector,
67: )
68: from ml4t.data.anomaly.config import (
69:     AnomalyConfig,
70:     PriceStalenessConfig,
71:     ReturnOutlierConfig,
72:     VolumeSpikeConfig,
73: )
74: from ml4t.data.validation import OHLCVValidator
75:
76: from data import load_us_equities
77: from utils.paths import get_output_dir
78: from utils.style import COLORS
79:
80: #
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
24:# security controls including the Warden pattern and injection defense.
31:# - Implement the Warden proxy pattern for tool-call authorization
32:# - Demonstrate fail-closed handling of detected prompt injection payloads
35:# reliability, replay, contamination control), 24.9 (security and governance)
82:def _question_id(question: str) -> str:
113:def _build_result(q, agent_probs: list[float]) -> ForecastResult:
327:def _leave_one_out_transform(
440:# ## Security: The Warden Pattern
442:# Section 24.9 describes the **Warden proxy**: a filter that sits between the
447:class WardenPolicy(NamedTuple):
448:    """A single policy rule for the Warden: (name, check_fn) pair."""
455:# ### Warden proxy
461:class Warden:
468:    def __init__(self, policies: list[WardenPolicy] | None = None):
500:de
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:27Z

- **tool**: `bash({"command": "for f in 03_market_microstructure/14_itch_bar_sampling.py 03_market_microstructure/16_itch_information_bars.py 03_market_microstructure/17_databento_bar_sampling.py; do echo \"===== $f =====\"; grep -nE \"^(class|def) |dollar|volume|tick|imbalance|information\" /home/georg/projects/ml4t-zh/$f | head -30; done"})`
- **tool**: `bash({"command": "for f in 23_knowledge_graphs/02_supply_chain_kg_construction.py 23_knowledge_graphs/03_graph_rag_qa.py 23_knowledge_graphs/06_gnn_feature_engineering.py 23_knowledge_graphs/09_knowledge_graph_features.py 23_knowledge_graphs/10_network_portfolio_construction.py; do echo \"===== $f =====\"; grep -nE \"^(class|def) |Neo4j|GraphDatabase|node|edge|provenance\" /home/georg/projects/ml4t-zh/$f | head -22; done"})`
- **tool**: `bash({"command": "for f in 22_rag_financial_research/04_ragas_evaluation.py 22_rag_financial_research/05_10k_rag_assistant.py 22_rag_financial_research/08_rag_security.py; do echo \"===== $f =====\"; grep -nE \"^(class|def) |ragas|injection|cutoff|filing_date|cite|provenance|chunk\" /home/georg/projects/ml4t-zh/$f | head -30; done"})`
- **tool**: `read({"filePath": "/home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py", "limit": 130, "offset": 440})`


> [reasoning] The "dollar|volume_bar" grep matched 112 files but likely because "volume" matched. Let me search specifically for the information bars: 03_market_microstructure has 14_itch_bar_sampling, 16_itch_information_bars, 17_databento_bar_sampling. Those are the alternative bars. Let me grep those specific files for functions/classes.

Also need KG construction and RAG security specifics. Let me batch final:
1. grep bar sampling files.
2. grep KG files for classes/functions.
3. grep 22 RAG 04 ragas / 05 assistant / 08 security classes.
4. read Warden class lines 440-560 of 09.
5. Maybe read agent_providers.py classes quickly.

Let me do it.
Now the alternative-bar implementations, KG/RAG component names, and Warden class.

  <details><summary>tool output</summary>

  ```text
===== 03_market_microstructure/14_itch_bar_sampling.py =====
24:# Build the four bar families §3.4 walks through (time, tick, volume, dollar
25:# plus imbalance/run information bars) from a single AAPL ITCH trading day,
32:# - Construct tick, volume, dollar, and imbalance bars from raw trades using
35:#   from time bars to volume/dollar bars.
37:#   aggressor field) and contrast tick-test vs midpoint-based imbalance bars.
56:"""Information-Driven Bars — constructing tick, volume, dollar, and imbalance bars from raw trades."""
103:def _repo_relative(path: Path) -> Path:
106:    ``ML4T_DATA_PATH`` may point anywhere - a shared data volume, or a sibling
135:# executions on the exchange, providing the raw tick stream for bar construction.
139:def load_itch_trades(symbol: str, max_trades: int |
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===== 23_knowledge_graphs/02_supply_chain_kg_construction.py =====
17:# # Building a Supply Chain Knowledge Graph at Scale
19:# **Chapter 23: Knowledge Graphs for Financial AI**
23:# > **Neo4j required**: The checked-in Qwen2.5 extraction cache is the default
27:# > docker compose run --rm ml4t-gpu python 23_knowledge_graphs/02_supply_chain_kg_construction.py
31:# This notebook demonstrates large-scale knowledge graph construction from SEC 10-K
33:# and loading them into a Neo4j graph database.
38:# - Load extracted triples into Neo4j using efficient batch UNWIND queries
41:# **Book Reference**: Chapter 23, Section 23.2 (Constructing Financial Knowledge Graphs)
44:# Requires a live Neo4j instance. Cache regeneration additionally requires an RTX-class GPU.
97:# Automatically detect GPU and
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===== 22_rag_financial_research/04_ragas_evaluation.py =====
71:# retrieved chunks, generated answer, citation IDs, and flags for refusal
80:class EvalSample:
85:    retrieved_chunks: list[dict]
87:    cited_chunk_ids: list[str]
93:# ### Load real 10-K filing text for context chunks
99:# Load real 10-K filing chunks for use as context
119:def find_evidence_sentence(sentences: list[str], required_terms: list[str]) -> str:
146:        retrieved_chunks=[{"id": "c1", "text": _aapl_competition}],
151:        cited_chunk_ids=["c1"],
164:        retrieved_chunks=[
172:        cited_chunk_ids=["c4", "c5"],
185:        retrieved_chunks=[{"id": "c8", "text": _msft_climate}],
190:        cited_chunk_ids=["c8"],
200:# out-of-scope queries that should trigger abstention, prompt-injection
210:        re
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py</path>
<type>file</type>
<content>
440: # ## Security: The Warden Pattern
441: #
442: # Section 24.9 describes the **Warden proxy**: a filter that sits between the
443: # agent and external tools, enforcing policies on every tool call.
444:
445:
446: # %%
447: class WardenPolicy(NamedTuple):
448:     """A single policy rule for the Warden: (name, check_fn) pair."""
449:
450:     name: str
451:     check: Callable[[str, dict], tuple[bool, str]]
452:
453:
454: # %% [markdown]
455: # ### Warden proxy
456: #
457: # Sits between the agent and the ToolExecutor, blocking calls that violate any policy.
458:
459:
460: # %%
461: class Warden:
462:     """Proxy that enforces policies on tool calls before ex
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:32Z

- **tool**: `bash({"command": "grep -nE \"^from ml4t|^import ml4t|BarSampler|Sampler\\(|to_information|expected_imbalance\" /home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py /home/georg/projects/ml4t-zh/03_market_microstructure/16_itch_information_bars.py /home/georg/projects/ml4t-zh/03_market_microstructure/17_databento_bar_sampling.py | head -40"})`
- **tool**: `bash({"command": "grep -rnE \"create_dataset_builder|CombinatorialCV|PurgedKFold|SplitAware|embargo|purg\" /home/georg/projects/ml4t-zh/07_defining_the_learning_task/*.py /home/georg/projects/ml4t-zh/11_ml_pipeline/*.py 2>/dev/null | head -40"})`
- **tool**: `bash({"command": "grep -nE \"duckdb|DuckDB|timescale|Timescale|asof|ASOF|def .*duckdb|def .*engine|ENGINES|class .*:\" /home/georg/projects/ml4t-zh/02_financial_data_universe/21_storage_benchmark_database.py | head -50"})`
- **tool**: `bash({"command": "grep -nE \"def |policy|guard|injection|trust\" /home/georg/projects/ml4t-zh/22_rag_financial_research/08_rag_security.py | head -40; echo \"=== providers ===\"; grep -nE \"^(class|def) |Protocol|create_llm_client|complete_with_usage\" /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_providers.py | head -30"})`


> [reasoning] I now have essentially everything. Let me get a couple more specifics:

1. The ml4t.engineer.bars library API names (VolumeBarSampler, DollarBarSampler, ImbalanceBarSampler, FixedTickImbalanceBarSampler) — confirmed. Also `from ml4t.engineer.bars import ...`? Let me grep the import lines in 14/16/17.
2. ml4t-engineer create_dataset_builder / CombinatorialCV (from skill). And labeling functions (triple_barrier_labels, meta_labels, atr_triple_barrier_labels, LabelingConfig).
3. RAG `08_rag_security` defended_policy function name.
4. ml4t-data providers: FREDProvider, HiveStorage, DataManager, Universe, GapDetector, OHLCVValidator, AnomalyManager/detectors.
5. Storage benchmark: DuckDB ASOF function, TimescaleDB presence. Let me grep import lines and function names for duckdb_asof and engine list.

Let me do a final batch of targeted greps.
Final targeted pass: library import surfaces (bars, dataset builder, labeling) and storage/security function names.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:70:from ml4t.engineer.bars import (
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:71:    DollarBarSampler,
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:72:    FixedTickImbalanceBarSampler,
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:73:    TickBarSampler,
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:74:    VolumeBarSampler,
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:76:from ml4t.engineer.bars.run import TickRunBarSampler
/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py:269:# - **TickBarSampler**: Fixed number of trades p
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:28:# is the `SplitAwarePreprocessor` class that prevents lookahead bias.
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:34:# 3. Implement a reusable `SplitAwarePreprocessor` class
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:399:# ## 2. SplitAwarePreprocessor
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:412:class SplitAwarePreprocessor:
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:419:        >>> preprocessor = SplitAwarePreprocessor(
/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py:442:    def fit
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
24:# > docker compose --profile benchmark up -d timescaledb clickhouse questdb influxdb
34:# | **Embedded** | SQLite, DuckDB, ArcticDB | In-process, no server required |
35:# | **Time-Series Servers** | ClickHouse, QuestDB, TimescaleDB | Production-scale, Docker required |
45:# 5. **ASOF Join** - Trade-quote alignment (critical for microstructure)
58:# - **Durability inside the timed region.** PostgreSQL and TimescaleDB commit
84:# | SQLite / DuckDB | file size on disk | the database file |
87:# | PostgreSQL / TimescaleDB | `pg_total_relation_size` / `hypertable_size` | table **plus indexes** (and, for the hypertable, all its chunks) |
102:# docker compose --profile benchmark up -d timescaledb clickhouse questdb influxdb
182:    "DuckDB": {"expected": False, "tested": False, "category": "e
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
23:# finance assistants, a critical concern when RAG systems operate on untrusted
27:# - Define structured attack cases covering prompt injection, retrieval poisoning,
29:# - Implement baseline vs defended answering policies with trust-aware filtering
43:# reproducible while still exercising injection, poisoning, and refusal logic.
70:# to financial RAG: indirect prompt injection (adversarial instructions hidden
72:# untrusted chunks), action injection (attempts to trigger unauthorized system
82:# as trusted or untrusted and specifying whether a correct answer is possible
83:# from the trusted evidence alone.
97:# ### Load trusted context sentences
112:def find_evidence_sentence(sentences: list[str], required_terms: list[str]) -> str:
121:_trusted_competition = find_evidence_sentence(_aapl
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:37Z

- **tool**: `bash({"command": "grep -nE \"langgraph|LangGraph|CrewAI|crewai|StateGraph|create_react_agent|def .*crew|graph\" /home/georg/projects/ml4t-zh/24_autonomous_agents/10_framework_comparison.py | head -30; echo \"=== dataset_builder usage ===\"; grep -rnE \"create_dataset_builder|DatasetBuilder\" /home/georg/projects/ml4t-zh --include=*.py | head; echo \"=== ml4t-diagnostic splitters ===\"; grep -rnE \"from ml4t.diagnostic|import ml4t.diagnostic\" /home/georg/projects/ml4t-zh --include=*.py | head -20"})`
- **tool**: `bash({"command": "grep -nE \"class |def |label_horizon|purge|embargo|expand|rolling\" /home/georg/projects/ml4t-zh/11_ml_pipeline/04_nested_cv_hpo.py | head -30; echo \"=== combine/purged fns ===\"; grep -rnE \"def generate_cv_splits|def make_purged|purged|embargo_size\" /home/georg/projects/ml4t-zh/11_ml_pipeline/*.py /home/georg/projects/ml4t-zh/utils/*.py 2>/dev/null | head -20"})`


> [reasoning] I have comprehensive coverage. Let me also quickly verify the presence of framework comparison (LangGraph/CrewAI) classes and the `create_dataset_builder` in ml4t-engineer (the skill references it). The request mentions LangGraph/Claude SDK stack. 10_framework_comparison.py covers native SDK, CrewAI, LangGraph. Let me grep.

Also "stateful equity-research agent" — that's the research operator + agent. "multi-agent forecasting with adversarial debate" — done.

Let me do one last quick grep for LangGraph/CrewAI and the framework classes, plus the 24 README mentions. And check if ml4t-engineer create_dataset_builder is used anywhere in repo.

Then I'll write the report.

  <details><summary>tool output</summary>

  ```text
16:# # Framework Comparison: Native SDK vs CrewAI vs LangGraph
33:# 2. **CrewAI**: *role-prompted approximation* of the same flow. CrewAI's
35:#    role / goal / backstory prompts; the CrewAI variant does not wrap the
37:# 3. **LangGraph**: pipeline as a `StateGraph` with typed state and four
44:# role-prompted CrewAI approximation rather than a wrap of the same agent
61:# pinned 2026-06-09 claude-sonnet run. It reloads the saved native and LangGraph
66:# real provider), while Variant B uses CrewAI's native LiteLLM layer and needs one
71:"""Framework comparison: same four-phase pipeline in native, CrewAI, LangGraph."""
98:# the notebook reloads the saved native + LangGraph traces named below, makes no
106:    "langgraph": "10_framework_comparison_20260609T151202Z_c8cba3007562.json",
120:#
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
33:# - Implement nested walk-forward CV with proper inner/outer purging and embargo
190:LABEL_HORIZON = 21  # sessions the label looks forward, and the purge each split needs
199:def evaluate_alpha_grid(
206:    label_horizon: int,
218:        label_horizon=label_horizon,
219:        embargo_size=10,
220:        expanding=True,
271:        print("Cached grid uses a narrower alpha range; recomputing with expanded sweep.")
452:def _selected_alpha(study) -> float:
467:def _make_single_loop_objective(
477:    def objective(trial):
497:def single_loop_cv(
503:    label_horizon: int = 21,
517:        label_horizon=label_horizon,
518:        embargo_size=10,
519:        expanding=True,
570:# with purging and embargo.
574:def _make_nested_objective(
581:    label_horizon: int,
587:    structure wi
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:41Z

- **tool**: `bash({"command": "sed -n '250,330p' /home/georg/projects/ml4t-zh/utils/cv_splits.py 2>/dev/null; echo \"=== imports nested ===\"; grep -nE \"^from|^import\" /home/georg/projects/ml4t-zh/11_ml_pipeline/04_nested_cv_hpo.py | head -30"})`


> [reasoning] Found utils/cv_splits.py generate_cv_splits. Let me quickly check its signature and any purge class. Also read the top of 11_ml_pipeline/04_nested_cv_hpo.py to find the split function import.

Let me do one final quick grep.

  <details><summary>tool output</summary>

  ```text
calendar_id=calendar_id,
        timestamp_col=date_col,
        fold_direction="backward",
    )


def make_wf_config(
    case_study_id: str,
    label_horizon: str = "0D",
    date_col: str = "timestamp",
    *,
    buffer_unit: str = DEFAULT_LABEL_BUFFER_UNIT,
) -> WalkForwardConfig:
    """Backward-compatible alias for make_walk_forward_config."""
    return make_walk_forward_config(
        case_study_id=case_study_id,
        label_horizon=label_horizon,
        date_col=date_col,
        buffer_unit=buffer_unit,
    )


def generate_cv_splits(
    dataset: pl.DataFrame | pd.DataFrame,
    case_study_id: str | None = None,
    setup_path: Path | None = None,
    label_buffer: str = "0D",
    outcome_horizon: str | None = None,
    date_col: str = "timestamp",
    *,
    buffer_unit:
…[truncated]
  ```
  </details>

## assistant · 2026-09-13T07:21:45Z


> [reasoning] I now have comprehensive material. Let me write the structured report. Given the user's request is technical and structured with concrete paths and symbols, I'll produce a detailed report, but respecting the ADHD-friendly output style (lead with answer, numbered, cap lists at 5—though this is an investigation report requiring completeness; I'll be structured with headers).

Let me organize into A (agents) and B (data).

Key facts to include:

A1. 24_autonomous_agents/
- Files: agent_schemas.py, agent_providers.py, agent_tools.py, agent_research.py, agent_specialists.py, agent_pipeline.py, agent_observability.py, research_operator.py, agent_fixtures.py. Notebooks 01-11 paired .py/.ipynb.
- ReAct: ResearchAgent in agent_research.py (max_steps, parse_json, validate_action, ToolExecutor, SearchResult, AgentTrace). Step prompt schema JSON {"action":"search"|"forecast"}. Notebook 01.
- Tool contracts: agent_tools.py: SearchClient Protocol, TavilySearchClient with cutoff_date filtering (_filter_by_date uses pub >= cutoff -> skip), MockSearchClient, ToolExecutor audit log (ToolExecution: tool_name, args, status, duration_ms, result_preview, provenance), ToolDefinition.to_anthropic_schema/to_openai_schema, SEARCH_TOOL, DEFAULT_ALLOWED_DOMAINS.
- State/memory: agent_schemas.py AgentState (ticker, cutoff_date, run_id, evidence, open_questions, tool_trace, quality_gates, synthesis_status; to_json/from_json); QualityGateResult. Notebook 03: check_coverage_gate, check_freshness_gate, check_consistency_gate, run_quality_gates(as_of), checkpoint_state/restore_checkpoint. Memory hierarchy: working=context, short-term=AgentState, long-term=RAG Ch22.
- Multi-agent: agent_specialists.py DebateAgent (bull/bear, max_rounds, consensus_threshold 0.05, DebateRound/DebateArtifact), SupervisorAgent (two-phase: disagreements+queries then finalize with confidence), agent_research ResearchAgent. agent_pipeline.py: neyman_extremize, neyman_extremize_weighted, platt_scale, logodds_extremize, find_optimal_d, brier_score, log_score, expected_calibration_error, reliability_bins. Notebook 05/06 (ThreadPoolExecutor)/07/08.
- Observability/auditability: agent_observability.py TracingLLMClient wraps any LLMClient, LLMCall (seq,label,model,json_mode,messages,response,tokens,timestamp), RunTrace.capture/.save/.load, rehydration methods, sanitize_trace_for_commit. forecast_traces/*.json.
- Frameworks: agent_providers.py LLMClient Protocol, create_llm_client order Anthropic→OpenAI→Google→OpenRouter→Ollama, ChatMessage, concrete clients. 10_framework_comparison.py: native Python SDK, CrewAI role-based, LangGraph StateGraph (typed state, 4 nodes). Runtime ~14 min, pinned traces.
- Research operator: research_operator.py (925 lines) 10 tools: query_registry (read-only SQL guard keywords), read_file, edit_file, write_file, run_bash (sandbox caveat), read_parquet, write_parquet, list_skills, read_skill, done. TOOL_SCHEMAS OpenAI format. Path safety _resolve_in_allowed/_writable_in_sandbox. Sandbox ML4T_OUTPUT_DIR. CASE_STUDY_TASKS. Trace persistence/sanitize.
- Governance: 09_evaluation_and_governance.py Warden (WardenPolicy NamedTuple, check -> blocked_log/allowed_log), _no_write_policy, _domain_allowlist_policy, _make_rate_limit_policy, inspect_untrusted_input, _detect, OWASP mapping. Production reliability: contamination-aware testing, point-in-time, calibration, ablations.

A2. RAG (22):
- 01_sec_filing_pipeline.py: filing metadata integrity (filing_date, acceptance timestamp, ingestion_timestamp), point-in-time metadata; parsing modes.
- 02_domain_embeddings_comparison.py: chunking sentence-window, get_sentence_transformer_embeddings, get_openai_embeddings, get_voyage_embeddings, cosine_similarity, compute_precision_at_k, compute_mrr, relevance labels; bge-large vs MiniLM results.
- 03_hybrid_retrieval.py: BM25Retriever, SemanticRetriever, reciprocal_rank_fusion (k=60), HybridRetriever, CrossEncoderReranker, TwoStageRetriever, heuristic_rerank_score.
- 04_ragas_evaluation.py: EvalSample, retrieval_hit, faithfulness, citation_accuracy.
- 05_10k_rag_assistant.py: SentenceSplitter chunk_size=512 overlap=50, create_index, create_query_engine, source_records, answer_diagnostics, abstentions/citations.
- 08_rag_security.py: AttackCase, has_injection_signal, baseline_policy, defended_policy (injection detection + trust filtering + evidence gating).
- 07_institutional_holdings_graph.py: point-in-time 13F features.
- Temporal leakage: cutoff_date, filing_date metadata.

KG (23):
- 02_supply_chain_kg_construction.py: Triple dataclass, build_batch_prompt, extract_relationships_batch, _parse_json_triples; Neo4j GraphDatabase UNWIND loading; cached extracted_triples.parquet + meta.json (content hash, schema, row count, extractor identity).
- 03_graph_rag_qa.py: text_to_cypher (constrained templates), validate_cypher (requires $cutoff_date), enforce_query_limits, execute_read_only, synthesize_answer; provenance_coverage, temporal_filter_present metrics; negative control earlier cutoff.
- 07_dynamic_kg_temporal.py: load_temporal_events, to_iso_date, visible_at_cutoff (public_time <= cutoff), build_snapshots, relationship_churn, leakage_test, write_snapshot_manifest (cutoff, window, extractor identity, per-parquet SHA-256); post_disclosure_effective_date.
- 06_gnn_feature_engineering.py: DenseGATAutoencoder, build_node_feature_row, fit_train_scaler, build_graph_losses (transductive leak warning).
- 09_knowledge_graph_features.py: validate_supply_snapshot, fetch_supply_relationships, normalize_name.
- 10_network_portfolio_construction.py: compute_mst, compute_degree_centrality, build_mst_graph.

A3. Skills:
- No SKILL.md in repo. External repo github.com/ml4t/skills. Operator tools list_skills/read_skill, SKILLS_ROOT env RESEARCH_OPERATOR_SKILLS_ROOT default ../skills. _parse_skill_frontmatter. 61 skills in 9 categories. Skill template format: The Problem, WRONG, CORRECT, Guardrails, Production Implementation, Checklist. YAML frontmatter name/description/when_to_use/dependencies/metadata.book_chapters/library/paths.
- Guards encoded as skills: concepts/lookahead-bias, data-leakage, point-in-time, survivorship-bias, backtest-overfitting; validation/purging-embargo, cpcv, deflated-sharpe, walk-forward-cv; advanced-ai/agent-governance.
- Fetched example: lookahead-bias SKILL.md and agent-governance SKILL.md (Warden pattern).

B4. 02:
- 13_data_quality_framework.py: imports ml4t.data.anomaly AnomalyManager, PriceStalenessDetector, ReturnOutlierDetector, VolumeSpikeDetector; AnomalyConfig, PriceStalenessConfig, ReturnOutlierConfig, VolumeSpikeConfig; OHLCVValidator; calculate_psi; detect_gaps; detect_corporate_actions; quality_check_pipeline.
- 14_point_in_time_validation.py: naive_leakage_corr, leakage_corr_scale_invariant, validate_signal_trade_lag, PITValidator (LEAK_THRESHOLD 0.30; check_future_leakage, check_date_gaps, check_monotonic_dates), FREDProvider.fetch_ohlcv(vintage_date=...) bitemporal/realtime_start/end, forward_fill only.
- 15_survivorship_bias_detection.py: check_survivorship_bias (3 signatures: unique_end_dates/all_same_end, delisting_rate<0.05, exits_cover_full_span), check_universe_completeness (new listings/delistings, coverage_ratio), expected_terminal, run_monte_carlo, build_panel_matrices, universe_path, survivor_path, survivor bias quantification.
- 20_storage_benchmark_file.py: CSV/Parquet/Feather/HDF5.
- 21_storage_benchmark_database.py: SQLite, DuckDB, TimescaleDB, ClickHouse, QuestDB, PostgreSQL, InfluxDB, ArcticDB; operations write/read/range/aggregation/ASOF; DuckDB native ASOF v1.1+; duckdb_asof function; docker compose --profile benchmark.
- 18_data_management.py: DataManager, HiveStorage, StorageConfig, Universe, GapDetector (ml4t.data.update_manager); 19_incremental_updates.py.

B5. ml4t-data / ml4t-engineer:
- Installed pip deps via pyproject (ml4t-data>=0.1.2, ml4t-engineer>=0.1.3), also ml4t-backtest, ml4t-diagnostic, ml4t-live. NOT vendored. uv.lock.
- Public APIs: ml4t.data.DataManager, ml4t.data.storage.HiveStorage, StorageConfig, ml4t.data.universe.Universe, ml4t.data.update_manager.GapDetector, ml4t.data.validation.OHLCVValidator, ml4t.data.anomaly.*, ml4t.data.providers.FREDProvider.
- ml4t.engineer: compute_features, ml4t.engineer.core.registry.get_registry (120+ features), ml4t.engineer.config.labeling.LabelingConfig, ml4t.engineer.labeling triple_barrier_labels/atr_triple_barrier_labels/meta_labels, ml4t.engineer.bars samplers.
- ml4t.diagnostic.signal.analyze_signal, ml4t.diagnostic.splitters.WalkForwardCV, CombinatorialCV (per skill), config WalkForwardConfig.
- Leakage-safe dataset prep: skill shows ml4t.engineer.create_dataset_builder(features, labels, dates, scaler) + CombinatorialCV. In-repo equivalent: utils/cv_splits.py generate_cv_splits wrapping ml4t.diagnostic WalkForwardCV with label_buffer; 11_ml_pipeline/04_nested_cv_hpo.py nested_cv/single_loop_cv with label_horizon=21, embargo_size.
- Alternative bars: ml4t.engineer.bars TickBarSampler, VolumeBarSampler, DollarBarSampler, FixedTickImbalanceBarSampler, TickImbalanceBarSampler, WindowTickImbalanceBarSampler, ImbalanceBarSampler, TickRunBarSampler (from ml4t.engineer.bars.run). Used in 03_market_microstructure/14,16,17.
- Point-in-time: pl.join_asof(strategy="backward"), PITValidator, visible_at_cutoff/leakage_test, cutoff_date plumbing.

B6. Shared PIT/lookahead utilities:
- 07_defining_the_learning_task/02_preprocessing_pipeline.py SplitAwarePreprocessor (fit on train only, _scale_params, save/load) — canonical leakage guard.
- 02/14 PITValidator, leakage_corr_scale_invariant, validate_signal_trade_lag.
- utils/cv_splits.py generate_cv_splits (label_buffer/embargo).
- 23/07 visible_at_cutoff, leakage_test, write_snapshot_manifest (SHA-256 provenance).
- 22/01 filing metadata PIT contract; 22/05 filing_date.
- 24 search cutoff_date filtering in TavilySearchClient._filter_by_date; ResearchAgent cutoff; SupervisorAgent cutoff_date.

Now let me write. Since the user asked for structured technical report with concrete paths and symbol names, I'll be thorough but organized. Use absolute paths.

I should note the ml4t-zh repo vs the book repo naming (stefan-jansen/machine-learning-for-trading). The local path is /home/georg/projects/ml4t-zh.

Let me produce the final report with the required <results> block.

I need to be careful: the downstream wants recommendations, but my job is search specialist—report findings. I'll give mechanism + note what AlphaMill can lift.

Let me write it.
<analysis>
**Literal Request**: Map paths + symbols + mechanisms in ml4t-zh for autonomous/multi-agent design, RAG/KG retrieval, the "61 agent skills" system, and data-engineering/leakage-safe prep.

**Actual Need**: A citable inventory of ml4t's agent contracts, memory/audit schemas, skill-guard format, and data-quality/PIT guards so AlphaMill can model its AI factor agents and DuckDB/Parquet bridge on it.

**Success Looks Like**: Absolute paths, class/function names, schemas, and protocols for all six sub-questions, with enough mechanism detail to write recommendations directly.
</analysis>

# ml4t-zh Investigation Report

Repo root: `/home/georg/projects/ml4t-zh`. Note: `.ipynb` and `.py` are jupytext pairs; the `.py` is source of truth. `ml4t-*` libraries are **pip-installed**, not vendored (repo rule: "The six ml4t-* libraries are the production implementations").

---

## A. AGENTS

### A1. `/home/georg/projects/ml4t-zh/24_autonomous_agents/` — core modules

The reusable (non-notebook) modules are: `agent_schemas.py`, `agent_providers.py`, `agent_tools.py`, `agent_research.py`, `agent_specialists.py`, `agent_pipeline.py`, `agent_observability.py`, `research_operator.py`. Notebooks 01-11 each have a paired `.py`.

**ReAct loop — `ResearchAgent`**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_research.py`
- `class ResearchAgent` (line 209): `__init__(llm: LLMClient, search: SearchClient | None, agent_id, max_steps=5, max_search_results=5)`; `run(question: ForecastQuestion, market_price)` returns `AgentForecastArtifact`.
- Loop enforces a strict JSON action contract: `build_step_prompt()` emits `{"action":"search","query":...}` or `{"action":"forecast","p_yes":0.XX,"rationale":...}`.
- `parse_json()` (fenced/unfenced fallback), `validate_action()` (clamps p_yes to [0,1], rejects bool/NaN), rich extractors `extract_confidence`, `extract_sentiment`, `extract_key_findings`, `extract_uncertainties`, `assess_evidence_quality`.
- On unrecognized action it feeds the error back to the LLM (line 290-300); on exhausted steps records `forced_default`.

**Tool contracts**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_tools.py`
- `@runtime_checkable class SearchClient(Protocol)` — `search(query, max_results, cutoff_date)`.
- `TavilySearchClient` does **point-in-time filtering**: `_filter_by_date()` drops any result with `published >= cutoff` (line 111-120); `_domain_allowed()` allow/block-list by hostname suffix.
- `MockSearchClient` applies the same cutoff logic deterministically.
- `ToolExecutor` maintains an independent audit trail: `@dataclass ToolExecution(tool_name, args, status, duration_ms, result_preview, provenance)`; `execute_search()`, `get_log_summary()`.
- `@dataclass ToolDefinition` with `to_anthropic_schema()` / `to_openai_schema()`; `SEARCH_TOOL`; `DEFAULT_ALLOWED_DOMAINS` (reuters, wsj, ft, bloomberg, sec.gov, federalreserve.gov, bls.gov, ...).

**State & memory schemas**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_schemas.py`
- `@dataclass AgentState`: `ticker, cutoff_date, run_id, evidence, open_questions, tool_trace, quality_gates: list[QualityGateResult], synthesis_status`; `to_json()` / `from_json()` — explicit state separate from the context window.
- `@dataclass QualityGateResult(gate_name, passed, reason, details)`.
- `AgentTrace`, `AgentForecastArtifact` (p_yes, rationale, traces, confidence, sentiment, key_findings, evidence_quality, uncertainties, token_usage, search_queries_made, sources_consulted), `SupervisorArtifact`, `DebateRound`/`DebateArtifact`, `AggregationResult`, `ForecastQuestion`, `ForecastResult`, `TokenUsage`.
- `/home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py`: `check_coverage_gate`, `check_freshness_gate(all `as_of`), `check_consistency_gate`, `run_quality_gates(state, as_of)`, `checkpoint_state`/`restore_checkpoint`. Memory hierarchy documented: working = context window, short-term = `AgentState`, long-term = RAG (Ch22).

**Multi-agent forecasting + adversarial debate**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_specialists.py`
- `class DebateAgent(llm, max_rounds=3, consensus_threshold=0.05)`: bull vs bear, `BULL_PROMPT_TEMPLATE` / `BEAR_PROMPT_TEMPLATE`, emits `DebateArtifact` with per-round probabilities, key evidence, `consensus_reached`, `early_termination`.
- `class SupervisorAgent(llm, search, max_queries=3)`: two-phase reconciliation — `SUPERVISOR_DISAGREEMENTS_PROMPT` (identify disagreements + propose clarifying queries) then `SUPERVISOR_FINALIZE_PROMPT` (updated p_yes + confidence high/medium/low), cutoff-aware searches.
- `agent_pipeline.py`: `neyman_extremize`, `neyman_extremize_weighted` (Herfindahl effective-N), `platt_scale`, `logodds_extremize`, `find_optimal_d`, `brier_score`, `log_score`, `sharpness`, `expected_calibration_error`, `reliability_bins`. Calibration uses `DEFAULT_D = sqrt(3)`.
- NB06 runs `ThreadPoolExecutor` identical agents with temperature diversity (AIA Forecaster result).

**Auditability / replay**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_observability.py`
- `TracingLLMClient` wraps any `LLMClient` and records `LLMCall(seq, label, model, json_mode, messages, response, input/output/total_tokens, timestamp)` — full prompt and raw response, untruncated.
- `RunTrace` (`capture`, `from_result`, `to_json`, `save`, `load`), rehydration methods (`agent_artifacts`, `debate_obj`, `supervisor_obj`, `forecast_result`) so replay is a drop-in for a live run; `sanitize_trace_for_commit` trims only third-party snippet/LLM text.
- Traces persisted to `/home/georg/projects/ml4t-zh/24_autonomous_agents/forecast_traces/*.json`; `merge_calls` restores chronological order across threads.

**Framework stack**
- `/home/georg/projects/ml4t-zh/24_autonomous_agents/agent_providers.py`: `LLMClient(Protocol)`, `ChatMessage`, `MockLLMClient`, `AnthropicChatClient`, `OpenAIChatClient`, `GoogleGeminiClient`, `OllamaChatClient`, `create_llm_client()` auto-select order Anthropic → OpenAI → Google → OpenRouter → Ollama.
- `/home/georg/projects/ml4t-zh/24_autonomous_agents/10_framework_comparison.py`: same pipeline in (a) native Python SDK, (b) CrewAI role/backstory agents incl. `_build_crewai_agents`, (c) LangGraph `StateGraph` with typed state and four nodes. Pinned replay traces in `forecast_traces/`.
- NB01 `01_react_reasoning.py` (Tree-of-Thoughts/Reflexion discussion), NB09 `09_evaluation_and_governance.py`.

**Stateful equity-research operator (the "AI factor agent" analog)**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/research_operator.py` (925 lines, ~600 core)
- 10 tools in `TOOL_FUNCTIONS` / `TOOL_SCHEMAS` (OpenAI function schema): `query_registry` (read-only SQLite, blocks INSERT/UPDATE/DELETE/DROP/ALTER/ATTACH, 200-row cap), `read_file`, `edit_file`, `write_file`, `run_bash`, `read_parquet`, `write_parquet`, `list_skills`, `read_skill`, `done`.
- Path safety: `_resolve_in_allowed` (read roots = sandbox, code repo, skills repo) and `_writable_in_sandbox` (writes confined, `ML4T_OUTPUT_DIR` redirect). `run_bash` carries an explicit threat-model docstring: guardrails, **not** a sandbox; recommends container/firejail + no egress.
- `SYSTEM_PROMPT` encodes workflow: inspect registry → list/read skills → state hypothesis → execute → compare to baseline → `done(summary)`. Budget `MAX_TOOL_CALLS=60`. `CASE_STUDY_TASKS` maps case study → concrete experiment.
- `sanitize_operator_trace_for_commit` normalizes home paths; artifacts in `operator_artifacts/`.

**Governance / production reliability**
`/home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py`
- `class WardenPolicy(NamedTuple)` and `class Warden` with `check(tool_name, args) -> (allowed, reason)`, `blocked_log`/`allowed_log`.
- Policies: `_no_write_policy`, `_domain_allowlist_policy`, `_make_rate_limit_policy(limit)`.
- Prompt-injection: `_detect`, `inspect_untrusted_input` (fail-closed); OWASP LLM Top-10 mapping. Also scores Brier/log/ECE, calibration, and ablations.

### A2. RAG (`22_rag_financial_research/`) and KG (`23_knowledge_graphs/`)

**RAG**
- `/home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py`: PIT metadata integrity — `filing_date`, acceptance timestamp, `ingestion_timestamp` required on every chunk so retrieval cannot leak the future; `list_10k_filings`; parser-mode contract.
- `02_domain_embeddings_comparison.py`: sentence-window chunking (80-600 chars), `get_sentence_transformer_embeddings`, `get_openai_embeddings`, `get_voyage_embeddings`, `cosine_similarity`, `compute_precision_at_k`, `compute_mrr`, `get_relevance_labels`, `stable_rank_indices`.
- `03_hybrid_retrieval.py`: `class BM25Retriever`, `class SemanticRetriever`, `reciprocal_rank_fusion(ranked_lists, k=60)`, `class HybridRetriever`, `class CrossEncoderReranker` (with `heuristic_rerank_score` fallback), `class TwoStageRetriever` (retrieve broad candidate pool → rerank → small set).
- `04_ragas_evaluation.py`: `@dataclass EvalSample(query, retrieved_chunks, answer, cited_chunk_ids, ...)`, `retrieval_hit`, `faithfulness`, `citation_accuracy`.
- `05_10k_rag_assistant.py`: `SentenceSplitter(chunk_size=512, chunk_overlap=50)`, `create_index` (optional ChromaDB), `create_query_engine`, `source_records`, `answer_diagnostics`, `evaluate_query_outputs` (citation rate, abstention rate).
- `07_institutional_holdings_graph.py`: point-in-time 13F ownership features.
- `08_rag_security.py`: `@dataclass AttackCase`; `has_injection_signal`; `baseline_policy` vs `defended_policy` = injection detection + trust-based chunk filtering (`trusted` flag) + evidence-gated refusal.

**KG**
- `/home/georg/projects/ml4t-zh/23_knowledge_graphs/02_supply_chain_kg_construction.py`: `@dataclass Triple` (`to_dict()` for batch UNWIND), `build_batch_prompt`, `extract_relationships_batch`, `_parse_json_triples`, `batched`; loads to Neo4j. Cache `output/supply_chain_cache/extracted_triples.parquet` + `.meta.json` pinning content hash, schema, row count, extractor identity.
- `03_graph_rag_qa.py`: safe Graph-RAG — `text_to_cypher` (constrained templates), `validate_cypher` (rejects if `$cutoff_date` missing), `enforce_query_limits`, `execute_read_only`, `synthesize_answer`; metrics `temporal_filter_present`, `provenance_coverage`; negative control re-runs an earlier cutoff and asserts no future rows and shifted position values.
- `07_dynamic_kg_temporal.py`: **leakage controls** — `load_temporal_events`, `to_iso_date`, `visible_at_cutoff(df, cutoff)` filters `public_time <= cutoff`, `build_snapshots`, `relationship_churn`, `leakage_test(df, cutoff)` asserts zero `public_time > cutoff`, `write_snapshot_manifest` (cutoff, window, extractor identity, per-parquet SHA-256). `post_disclosure_effective_date` flags negative disclosure lag.
- `06_gnn_feature_engineering.py`: `DenseGATAutoencoder`, `build_node_feature_row`, `fit_train_scaler`, `build_graph_losses` (explicit transductive-inference leak warning).
- `09_knowledge_graph_features.py`: `validate_supply_snapshot`, `fetch_supply_relationships`, `normalize_name`.
- `10_network_portfolio_construction.py`: `compute_mst`, `build_mst_graph`, `compute_degree_centrality`.

### A3. The "61 agent skills" concept

- **No `SKILL.md` / skills directory exists inside ml4t-zh.** The catalog is an external companion repo: `https://github.com/ml4t/skills` (61 standalone skills, 9 categories). ml4t-zh only *consumes* it.
- Consumer code: `research_operator.py` — `SKILLS_REPO_URL`, `SKILLS_ROOT` (env `RESEARCH_OPERATOR_SKILLS_ROOT`, default `CODE_REPO.parent/"skills"`), `tool_list_skills(category)`, `tool_read_skill(name_or_path)`, `_parse_skill_frontmatter` (reads `name`, `description`, `metadata.library`). `TOOL_SCHEMAS` describe skills as "WRONG/CORRECT pattern + Production Implementation block".
- Skill file format (verified from the repo): YAML frontmatter (`name`, `description`, `when_to_use`, `dependencies`, `metadata.book_chapters`, `metadata.library`, `paths`) followed by sections: **The Problem → WRONG code → CORRECT code → Guardrails → Production Implementation (`ml4t-*` handoff) → Checklist**. Max 120 lines; CI enforces schema and executes numeric examples.
- Categories: Concepts(10), Data(7), Features(10), Validation(8), Backtest(5), Portfolio(5), Advanced AI(5), Production(2), Infrastructure(4), Workflows(5).
- **How guards are encoded** (guard skills relevant to AlphaMill):
  - Lookahead/leakage: `concepts/lookahead-bias`, `concepts/data-leakage`, `concepts/point-in-time`, `concepts/survivorship-bias`.
  - Multiple testing: `concepts/backtest-overfitting`, `validation/deflated-sharpe`.
  - CV leakage: `validation/purging-embargo`, `validation/cpcv`, `validation/walk-forward-cv`.
  - Agent safety: `advanced-ai/agent-governance` (Warden/policy/approval/audit), `advanced-ai/agent-tool-contracts`, `advanced-ai/agent-state-memory`, `advanced-ai/multi-agent-forecasting`, `advanced-ai/research-operator`.
  - Example `concepts/lookahead-bias/SKILL.md` guardrails: rolling stats must use `.shift(1)`; never `fit_transform` on test; no `shuffle=True` on time series; thresholds from expanding windows; report dates not period-end; investigate Sharpe>2 or IS/OOS gap<5%. Production handoff: `ml4t.engineer.create_dataset_builder(...)` + `ml4t.diagnostic.splitters.CombinatorialCV(embargo_pct=0.01)`.
  - Example `advanced-ai/agent-governance`: Warden allowlist, high-impact tools require approval, retrieved text is untrusted evidence, audit log includes policy decisions, explicit stop conditions.

---

## B. DATA

### B4. `/home/georg/projects/ml4t-zh/02_financial_data_universe/`

- **Data-quality framework** — `13_data_quality_framework.py`:
  - Library: `ml4t.data.anomaly.{AnomalyManager, PriceStalenessDetector, ReturnOutlierDetector, VolumeSpikeDetector}` and their configs `AnomalyConfig, PriceStalenessConfig, ReturnOutlierConfig, VolumeSpikeConfig`; `ml4t.data.validation.OHLCVValidator`.
  - Local helpers: `calculate_psi` (population stability index), `detect_gaps`, `detect_corporate_actions(threshold=0.25)`, `quality_check_pipeline`.
- **Storage benchmarks**:
  - `20_storage_benchmark_file.py`: CSV / Parquet / Feather (Arrow IPC) / HDF5 — write, forced read, columnar ops.
  - `21_storage_benchmark_database.py`: engines SQLite, DuckDB, ClickHouse, QuestDB, TimescaleDB, PostgreSQL, InfluxDB, ArcticDB; ops write/read/range-query/OHLCV-aggregation/**ASOF join**. DuckDB has native ASOF (v1.1+) via `duckdb_asof` (line 652); SQLite has none (line 456). Uniform timing policy via `time_write`/`time_read`, `validate_result`, `wait_until_rows_visible`. Server engines need `docker compose --profile benchmark up -d`.
  - `22_pandas_polars_benchmark.py`: pandas vs Polars.
- **Point-in-time validation** — `14_point_in_time_validation.py`:
  - `naive_leakage_corr` (fails to detect), `leakage_corr_scale_invariant` (correct detector: feature's own return vs next price return), `validate_signal_trade_lag(signals, execution_lag=1)` shifts by trading rows.
  - `class PITValidator` (`LEAK_THRESHOLD = 0.30`): `check_future_leakage`, `check_date_gaps(max_gap_days=5)`, `check_monotonic_dates`.
  - Bitemporal macro: `ml4t.data.providers.FREDProvider.fetch_ohlcv(..., vintage_date=...)` maps to FRED `realtime_start/end`; **forward-fill only, never back-fill**; timestamp must be release date.
- **Survivorship bias quantification** — `15_survivorship_bias_detection.py`:
  - `check_survivorship_bias(data, symbol_col, date_col)` → three signatures: `all_same_end_date` (unique end dates < 10), `delisting_rate < 0.05`, `exits_cover_full_span` (< 0.8 of panel span). Returns `likely_biased`.
  - `check_universe_completeness(..., expected_market_size=4500, expected_ipo_rate=(100,400))` → entry/exit flows, `coverage_ratio`, warnings.
  - Monte-Carlo quantification: `expected_terminal`, `run_monte_carlo`, `build_panel_matrices`, `universe_path`, `survivor_path`, `total_return`.
- `18_data_management.py` / `19_incremental_updates.py`: `ml4t.data.DataManager` (`fetch`, `batch_load`, `load`, `update`), `ml4t.data.storage.HiveStorage` + `StorageConfig`, `ml4t.data.universe.Universe`, `ml4t.data.update_manager.GapDetector`, `OHLCVValidator`.

### B5. ml4t-data / ml4t-engineer

- **Not vendored.** Declared in `/home/georg/projects/ml4t-zh/pyproject.toml` (lines ~56-64): `ml4t-data>=0.1.2`, `ml4t-engineer>=0.1.3`; also `ml4t-backtest`, `ml4t-diagnostic`, `ml4t-live`. Pinned in `uv.lock`. Envs under `/home/georg/projects/ml4t-zh/envs/`.
- **Public API surface actually called**:
  - Dataset prep / features: `ml4t.engineer.compute_features(df, [name | {name,params} | config_path])`; `ml4t.engineer.core.registry.get_registry()` → `.list_all()`, `.get(name)` with `name/category/description/formula/parameters/input_type` (120+ features). Demo: `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/10_ml4t_library_ecosystem.py`.
  - Labels: `ml4t.engineer.config.labeling.LabelingConfig` (`.triple_barrier(...)`), `ml4t.engineer.labeling.{triple_barrier_labels, atr_triple_barrier_labels, meta_labels}` in `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py`.
  - Cross-validation: `ml4t.diagnostic.splitters.WalkForwardCV` (+ `config.WalkForwardConfig`), referenced `CombinatorialCV(embargo_pct=...)` in skills.
  - Signal eval: `ml4t.diagnostic.signal.analyze_signal(...)`.
  - **Leakage-safe dataset builder (skill-documented)**: `ml4t.engineer.create_dataset_builder(features, labels, dates=timestamps, scaler="standard")` then `builder.split(cv)` → `fold.X_train/y_train/X_test/y_test`. This is the canonical "split-aware dataset" entry point.
  - In-repo equivalent: `/home/georg/projects/ml4t-zh/utils/cv_splits.py` `generate_cv_splits(dataset, case_study_id/setup_path, label_buffer, outcome_horizon, cv_config)` delegating to `WalkForwardCV`; folds carry `train_start/end`, `val_start/end`; buffer sized to label horizon. `11_ml_pipeline/04_nested_cv_hpo.py` `single_loop_cv`/`nested_cv` use `label_horizon=21`, `embargo_size=10` (inner embargo = label horizon).
  - **Alternative bars**: `ml4t.engineer.bars.{TickBarSampler, VolumeBarSampler, DollarBarSampler, FixedTickImbalanceBarSampler, TickImbalanceBarSampler, ImbalanceBarSampler, WindowTickImbalanceBarSampler}`, plus `ml4t.engineer.bars.run.TickRunBarSampler`. Used in `/home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py`, `16_itch_information_bars.py`, `17_databento_bar_sampling.py` (tick-test / Lee-Ready labeling, AFML imbalance formula, alpha adaptation, threshold calibration).
- **Point-in-time join**: Polars `join_asof(..., strategy="backward")` documented in `07_defining_the_learning_task/10_ml4t_library_ecosystem.py` (fundamental/macro alignment and trade-quote matching); daily-characteristics PIT join in `02_preprocessing_pipeline.py` ~line 800.

### B6. Shared point-in-time / lookahead-prevention utilities

Inline (not a single shared module) but consistent across the repo:
- `SplitAwarePreprocessor` — `/home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py` (class line 412): `fit(train_df)` stores `_scale_params` from train only; `transform`; `save`/`load`; used per-fold at line 1062. NB also demonstrates the leaky full-data variant for contrast (~line 951).
- `PITValidator`, `leakage_corr_scale_invariant`, `validate_signal_trade_lag` — `02_financial_data_universe/14_point_in_time_validation.py`.
- `generate_cv_splits` (label-buffer/embargo) — `/home/georg/projects/ml4t-zh/utils/cv_splits.py`.
- KG temporal: `visible_at_cutoff` + `leakage_test` + `write_snapshot_manifest` (SHA-256) — `23_knowledge_graphs/07_dynamic_kg_temporal.py`; Cypher `$cutoff_date` enforcement — `23_knowledge_graphs/03_graph_rag_qa.py`.
- RAG/search PIT: filing `filing_date`/`acceptance` flags — `22_rag_financial_research/01_sec_filing_pipeline.py`; `cutoff_date` filter — `24_autonomous_agents/agent_tools.py` (`TavilySearchClient._filter_by_date`), threaded through `ResearchAgent.run` and `SupervisorAgent.run`.

---

<results>
<files>
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_schemas.py - AgentState, QualityGateResult, Debate/ Supervisor/ Aggregation artifacts, TokenUsage; typed state + JSON checkpoint
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_research.py - ResearchAgent ReAct loop, JSON action schema, validators, rich output extraction
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_tools.py - SearchClient protocol, Tavily/Mock clients with cutoff_date PIT filter, ToolExecutor audit log, ToolDefinition schema translator, domain allowlist
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_specialists.py - DebateAgent (bull/bear) and SupervisorAgent (two-phase reconciliation); prompt templates
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_pipeline.py - Neyman extremization, Platt/log-odds calibration, find_optimal_d, Brier/log/ECE metrics
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_observability.py - TracingLLMClient, LLMCall, RunTrace capture/save/load/rehydrate, trace sanitization
- /home/georg/projects/ml4t-zh/24_autonomous_agents/agent_providers.py - LLMClient protocol + Anthropic/OpenAI/Google/Ollama clients, create_llm_client
- /home/georg/projects/ml4t-zh/24_autonomous_agents/research_operator.py - 10-tool autonomous research operator, registry SQL guard, sandbox path safety, list_skills/read_skill, trace artifacts
- /home/georg/projects/ml4t-zh/24_autonomous_agents/09_evaluation_and_governance.py - Warden/WardenPolicy, no-write/domain/rate-limit policies, injection detection, OWASP mapping
- /home/georg/projects/ml4t-zh/24_autonomous_agents/03_state_and_memory.py - quality gates (coverage/freshness/consistency), checkpoint/restore, memory hierarchy
- /home/georg/projects/ml4t-zh/24_autonomous_agents/10_framework_comparison.py - native SDK vs CrewAI vs LangGraph StateGraph, pinned traces
- /home/georg/projects/ml4t-zh/22_rag_financial_research/01_sec_filing_pipeline.py - PIT filing metadata (filing_date/acceptance/ingestion_timestamp), parser contract
- /home/georg/projects/ml4t-zh/22_rag_financial_research/03_hybrid_retrieval.py - BM25Retriever, SemanticRetriever, reciprocal_rank_fusion(k=60), HybridRetriever, CrossEncoderReranker, TwoStageRetriever
- /home/georg/projects/ml4t-zh/22_rag_financial_research/04_ragas_evaluation.py - EvalSample, retrieval_hit, faithfulness, citation_accuracy
- /home/georg/projects/ml4t-zh/22_rag_financial_research/05_10k_rag_assistant.py - SentenceSplitter(512/50), create_index/query_engine, answer diagnostics, abstention/citation rates
- /home/georg/projects/ml4t-zh/22_rag_financial_research/08_rag_security.py - AttackCase, has_injection_signal, baseline vs defended policy (trust filtering + evidence gating)
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/02_supply_chain_kg_construction.py - Triple dataclass, batch extraction, Neo4j UNWIND, content-hash cache meta
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/03_graph_rag_qa.py - text_to_cypher, validate_cypher (requires $cutoff_date), read-only execution, provenance/temporal metrics, negative control
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/07_dynamic_kg_temporal.py - visible_at_cutoff, leakage_test, snapshot manifest with per-parquet SHA-256
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/06_gnn_feature_engineering.py - DenseGATAutoencoder, train-only scaler, transductive leak warning
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/09_knowledge_graph_features.py - snapshot validation + KG-to-ML feature extraction
- /home/georg/projects/ml4t-zh/23_knowledge_graphs/10_network_portfolio_construction.py - MST/centrality network portfolio
- /home/georg/projects/ml4t-zh/02_financial_data_universe/13_data_quality_framework.py - AnomalyManager/detectors, OHLCVValidator, PSI, gap/corporate-action detectors
- /home/georg/projects/ml4t-zh/02_financial_data_universe/14_point_in_time_validation.py - PITValidator, leakage_corr_scale_invariant, validate_signal_trade_lag, FRED vintage_date bitemporal
- /home/georg/projects/ml4t-zh/02_financial_data_universe/15_survivorship_bias_detection.py - check_survivorship_bias, check_universe_completeness, Monte-Carlo bias quantification
- /home/georg/projects/ml4t-zh/02_financial_data_universe/20_storage_benchmark_file.py - CSV/Parquet/Feather/HDF5 benchmark
- /home/georg/projects/ml4t-zh/02_financial_data_universe/21_storage_benchmark_database.py - DuckDB/SQLite/TimescaleDB/ClickHouse/QuestDB/Postgres/InfluxDB; native DuckDB ASOF
- /home/georg/projects/ml4t-zh/02_financial_data_universe/18_data_management.py - DataManager, HiveStorage, StorageConfig, Universe, GapDetector
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/02_preprocessing_pipeline.py - SplitAwarePreprocessor (train-only fit, save/load, per-fold)
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/03_label_methods.py - ml4t-engineer LabelingConfig, triple_barrier_labels, atr_triple_barrier_labels, meta_labels
- /home/georg/projects/ml4t-zh/07_defining_the_learning_task/10_ml4t_library_ecosystem.py - compute_features, registry, analyze_signal, join_asof PIT pattern
- /home/georg/projects/ml4t-zh/utils/cv_splits.py - generate_cv_splits over WalkForwardCV with label_buffer/embargo
- /home/georg/projects/ml4t-zh/11_ml_pipeline/04_nested_cv_hpo.py - nested/single-loop CV with label_horizon + embargo_size
- /home/georg/projects/ml4t-zh/03_market_microstructure/14_itch_bar_sampling.py - Tick/Volume/Dollar/FixedTickImbalance/TickRun bar samplers
- /home/georg/projects/ml4t-zh/03_market_microstructure/16_itch_information_bars.py - AFML tick-imbalance formula vs library, alpha/window variants
- /home/georg/projects/ml4t-zh/03_market_microstructure/17_databento_bar_sampling.py - threshold calibration for dollar/volume/imbalance bars
- /home/georg/projects/ml4t-zh/pyproject.toml - declares ml4t-data>=0.1.2, ml4t-engineer>=0.1.3, ml4t-backtest/diagnostic/live
</files>

<answer>
**A) Agent design.** ml4t's autonomous stack is deliberately framework-agnostic and contract-first. The reusable core lives in 24_autonomous_agents as plain dataclasses + Protocols, not a framework: `ResearchAgent` (ReAct) emits a strict JSON action contract (`search` | `forecast`) validated by `parse_json`/`validate_action`; `DebateAgent` runs bull/bear rounds with a `consensus_threshold`; `SupervisorAgent` does two-phase disagreement→clarifying-search→finalize; `agent_pipeline` supplies Neyman extremization and calibration. Memory is an explicit `AgentState` (tick, cutoff_date, run_id, evidence, open_questions, tool_trace, quality_gates) with JSON checkpoint/replay and coverage/freshness/consistency gates. Auditability is first-class via `TracingLLMClient`/`RunTrace` recording every prompt and raw response to `forecast_traces/`. Tool safety is a `Warden` policy proxy plus read-only/sandboxed operator tools and explicit threat-model documentation. The research operator (an AI research agent over a SQLite registry, Parquet, and a skills corpus) is the closest structural analog to an AI factor-generation agent.

**The "61 agent skills" is an external repo** (github.com/ml4t/skills), not code in ml4t-zh; ml4t-zh reaches it through `list_skills`/`read_skill` in `research_operator.py`. Skills are concept-first Markdown with a fixed section contract (Problem, WRONG, CORRECT, Guardrails, Production Implementation, Checklist) and YAML frontmatter mapping to book chapters and an `ml4t-*` library handoff. Leakage/overfitting guards are themselves skills: concepts/lookahead-bias, data-leakage, point-in-time, survivorship-bias, backtest-overfitting; validation/purging-embargo, cpcv, deflated-sharpe, walk-forward-cv; advanced-ai/agent-governance. This is the exact pattern AlphaMill should copy for its factor-hypothesis skills: put methodology in versioned Markdown files, keep the agent prompt thin, and expose skills as discoverable tools.

**RAG/KG retrieval.** RAG uses sentence-window chunking, embedding-model benchmarking, BM25+dense `HybridRetriever` fused by RRF (k=60), then a `CrossEncoderReranker` in a `TwoStageRetriever`; evaluation is Ragas-style (retrieval_hit, faithfulness, citation_accuracy, abstention). PIT is enforced by carrying `filing_date`/acceptance/ingestion timestamps on every chunk and by cutoff-aware searches. Graph RAG uses a schema-constrained `text_to_cypher` + `validate_cypher` that hard-requires a `$cutoff_date` parameter, read-only execution, provenance metrics, and a negative-control test that an earlier cutoff actually changes the answer. The temporal-KG notebook supplies the strongest reusable guard: `visible_at_cutoff` (`public_time <= cutoff`), `leakage_test`, and a snapshot manifest with SHA-256 per Parquet.

**B) Data engineering.** Data quality uses ml4t-data's `OHLCVValidator` and anomaly detectors (staleness, return outlier, volume spike) plus local PSI/gap/corporate-action checks. PIT validation is the reusable core: `leakage_corr_scale_invariant`, `validate_signal_trade_lag`, and `PITValidator` (threshold 0.30) with bitemporal macro retrieval via `FREDProvider.fetch_ohlcv(vintage_date=...)` and forward-fill-only rules. Survivorship is quantified with two detectors (three bias signatures; entry/exit completeness) plus a Monte-Carlo bias estimator. Storage is benchmarked across CSV/Parquet/Feather/HDF5 and SQLite/DuckDB/TimescaleDB/ClickHouse/QuestDB/Postgres/InfluxDB with a uniform timing/validation policy; notably DuckDB's native ASOF join is highlighted and SQLite's absence is noted. ml4t-data/ml4t-engineer are pip-installed production libs, not vendored. Leakage-safe dataset prep is done through `ml4t-engineer` bars/labeling/CV APIs and, in-repo, through `SplitAwarePreprocessor`, `utils/cv_splits.generate_cv_splits` (label-buffer/embargo), and nested CV with `label_horizon`/`embargo_size`. Alternative bars live in `ml4t.engineer.bars` (tick, volume, dollar, imbalance, tick-run) and are demonstrated on ITCH/Databento trade data.
</answer>

<next_steps>
For AlphaMill recommendations, use these five anchors:
1. Agent core: model on `AgentState` + JSON action contract + `RunTrace` (24_autonomous_agents) rather than adopting LangGraph initially; keep a framework adapter layer like `10_framework_comparison.py`.
2. Factor skills: mirror the external SKILL.md contract and expose `list_skills`/`read_skill` tools; encode lookahead/leakage/multiple-testing guards as skill files, not hidden in prompts.
3. Tool contracts: copy `ToolDefinition` dual-schema translation, per-call `ToolExecution` audit records, and the Warden policy proxy with approval-required tiers.
4. Data bridge guards: enforce `PITValidator` + `leakage_corr_scale_invariant` + `validate_signal_trade_lag` as pre-insert gates; require bitemporal/vintage columns (release/public time) and forward-fill-only.
5. Storage: adopt DuckDB native ASOF + Hive-partitioned Parquet (ml4t's `HiveStorage` model); benchmark against the repo's operation set (range query, OHLCV aggregation, ASOF).
Ready to proceed - no follow-up needed.
</next_steps>
</results>
