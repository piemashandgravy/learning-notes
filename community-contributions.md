---
layout: page
title: Ed Donner — Community Contributions
---

Curated highlights from the community contributions in Ed Donner's
[Agentic AI course repo](https://github.com/ed-donner/agents) (cloned locally at `~/dev/agents/`).
These are real student projects submitted via PR — quality varies, but the best ones are worth
studying for novel application ideas and architectural patterns.

Browse the raw folders at: `~/dev/agents/{1_foundations,2_openai,3_crew,4_langgraph}/community_contributions/`

---

## Chapter 1 — Foundations

### `1_medtech_opportunity_finder`
**What it does:** Three-step pipeline (business area → pain point → solution) for generating healthcare AI business ideas, with streamed Markdown output.  
**Why it's interesting:** Clean example of chaining sequential LLM calls into surprising outputs, plus streaming response patterns — neither of which is in the base lab.

---

## Chapter 2 — OpenAI Agents SDK

### `agentic_task_scheduling`
**What it does:** Multi-agent calendar system using agent handoffs, SQLite persistence, and conflict resolution.  
**Why it's interesting:** Shows session management and state across turns without framework-level persistence — the handoff flow (triage → scheduler) is a clean teachable pattern.

### `code_review_agent`
**What it does:** Three specialist agents (security, performance, style) review code in parallel, then a manager synthesises findings with scoring.  
**Why it's interesting:** Clean agent-as-tool pattern — specialist agents converted to tools for the manager. Structured Pydantic outputs for reliable scoring. Reusable template for any parallel expert review.

### `drawing_agents`
**What it does:** Three-agent pipeline (planner → drawer → evaluator) that draws on a canvas using Pillow, with image input feeding back into the evaluator.  
**Why it's interesting:** Image I/O with agents and a real feedback loop. Bridges vision tasks with LLM instruction execution — useful for any multimodal reasoning project.

### `url_security_advisor_gradio_sb`
**What it does:** Security analyser with input guardrails, two agents checking in parallel, and a manager picking the best result.  
**Why it's interesting:** Competitive parallelism — two agents race and the manager selects. Also shows input validation guardrails (URL/email format checking) before any expensive calls are made.

### `deep_research_qa`
**What it does:** Clarifier → searcher → writer → evaluator pipeline for research queries, deployed on Hugging Face Spaces via Gradio.  
**Why it's interesting:** Full end-to-end production pattern with quality gates. Shows deployment via HF Spaces and how to chain structured outputs across pipeline stages.

### `ragive_ai_learning_assistant`
**What it does:** Personalised learning roadmap generator — plans skills, searches resources in parallel, synthesises delivery paths.  
**Why it's interesting:** Async parallel resource gathering for multiple skills simultaneously, then profile-aware ranking. Good example of `asyncio.gather()` at scale.

### `medical_deep_research`
**What it does:** Guardrail-protected research system for medical literature — validates domain, then fans out to 5 parallel searches, synthesises, and emails results.  
**Why it's interesting:** Domain-specific guardrails to gate expensive searches. The fan-out + synthesis pattern is reusable for any specialised research workflow.

### `Self_Hosted_Web_Search`
**What it does:** Full deep-research pipeline running locally using Ollama + Llama3 instead of OpenAI.  
**Why it's interesting:** Drop-in model swap: shows exactly how to run the same agent patterns with local LLMs — useful when API costs or data privacy matter.

### `code_learning_assistant`
**What it does:** Five-agent system that explains code via language concepts, walkthrough, PR documentation, and git diff analysis.  
**Why it's interesting:** Git integration for context — the agents read actual diffs and commit history, not just the code file. Teaching-focused UX.

---

## Chapter 3 — CrewAI

### `engineering_team_with_feedback_loops`
**What it does:** Code-generation crew with real-time Gradio streaming via a shared queue — agents emit task output live as text generates.  
**Why it's interesting:** Queue-based streaming is the right solution to CrewAI's "cold start" UX problem (long silence before output appears). Pattern is directly reusable.

### `conversational-debate`
**What it does:** Three-agent debate (proposer vs. opposer + judge) with long-term memory and turn-based iteration via Gradio.  
**Why it's interesting:** Uses CrewAI memory across rounds, implements a judgment phase, and shows multi-round adversarial reasoning. Also a good Gradio streaming example.

### `incident_postmortem`
**What it does:** Sequential three-agent crew (summariser → RCA analyst → action owner) for blameless postmortem generation.  
**Why it's interesting:** Compact, domain-focused workflow. Shows how to encode tone guidance ("blameless") into agent instructions. A solved template for incident review.

### `schema_builder`
**What it does:** Generates JSON schemas and Pydantic models from natural language data descriptions.  
**Why it's interesting:** Meta-use of agents — the output is code/schema rather than text. Useful as a dev tool inside an AI pipeline.

### `1_swap_trading_prism`
**What it does:** USD SOFR swap trading monitor — multi-agent system analysing market positions via Serper search.  
**Why it's interesting:** Finance-specific domain design. Shows how to integrate Serper for live market data within a CrewAI crew rather than just general web search.

### `software_team_flow_ui_no_code_docker_run`
**What it does:** Full software engineering crew with a Gradio no-code UI, containerised with Docker.  
**Why it's interesting:** End-to-end deployment pattern: Gradio UI + CrewAI backend + Docker. Closest to a production-ready template in the contributions.

### `career_agent_crew`
**What it does:** Career advisory crew — analyses a CV, matches against job descriptions, produces tailored application guidance.  
**Why it's interesting:** Multi-document input (CV + JD). Shows how to pass structured file content into agent context across a sequential crew.

---

## Chapter 4 — LangGraph

### `patch_to_pr`
**What it does:** Takes a git patch → drafts a GitHub PR description → evaluator checks success criteria → loops up to 5 times if criteria aren't met.  
**Why it's interesting:** Tight feedback loop with structured success criteria — shows exactly how to do iterative refinement in LangGraph. Solves a real developer problem.

### `sidekick_with_planning`
**What it does:** Agentic assistant with an explicit planner node (generates steps), worker node (executes tools), and evaluator node (checks success criteria). Async SQLite checkpointing throughout.  
**Why it's interesting:** Planning before execution — the graph generates a plan before any tool is called. Closest pattern to how o1-style reasoning works. Combined with async checkpointing for full session persistence.

### `three_agent_debate_langgraph`
**What it does:** For/against agents + moderator, with routing that forces both sides to speak before evaluation, and a structured-output verdict when max iterations hit.  
**Why it's interesting:** Psychology-aware design — prevents anchoring bias via routing constraints. Forced final verdict via structured output is a clean fallback pattern.

### `langgraph_checkpoint_howto`
**What it does:** Tutorial on retrieving and replaying LangGraph checkpoints at any step.  
**Why it's interesting:** Technique, not application: shows how to test individual pipeline steps by replaying from a checkpoint — saves cost and time during development.

### `StocksMarketInvestmentRecommender`
**What it does:** Hierarchical multi-graph system — a Market Analyst subgraph called by a manager graph that decides iteratively whether to analyse more.  
**Why it's interesting:** Most sophisticated multi-graph pattern in the contributions. Manager node controls depth (re-invokes analyst or stops). Uses Pydantic state instead of long message lists. Integrates MCP tools.

### `transcript_summarizer`
**What it does:** Processes long VTT transcripts via chunking + multi-level summarisation (chunk → section → document), running on Ollama/LLaMA3, containerised with Docker.  
**Why it's interesting:** Shows the chunking-for-context-windows pattern end-to-end. Nested summarisation is the right approach for long documents — and fully local/containerised.

### `sidekick_with_session_memory`
**What it does:** LangGraph sidekick extended with persistent session memory across restarts.  
**Why it's interesting:** Directly extends the course lab. Concrete implementation of cross-session memory using LangGraph's checkpointer — worth comparing against `sidekick_with_planning`.

### `repo_onboarding_sidekick`
**What it does:** Agentic tool for onboarding to a new codebase — reads repo structure, summarises purpose, maps key files, suggests first tasks.  
**Why it's interesting:** Meta-application (an agent that explains codebases). Pattern extends naturally: add git log, test coverage, or CI history as additional tools.

### `sidekick-Personal-CoWorker-refactored-AzureOpenAI`
**What it does:** The course sidekick refactored to use Azure OpenAI with managed identity instead of a direct API key.  
**Why it's interesting:** Directly relevant to a work environment. Shows how to swap in `AzureOpenAI` + `DefaultAzureCredential` across a LangGraph project without changing agent logic.

---

## Patterns worth lifting

These themes appear in the strongest contributions and are worth understanding as reusable patterns:

| Pattern | Where to look |
|---|---|
| **Agent-as-tool** (specialist → manager tool) | `code_review_agent` |
| **Competitive parallelism** (two agents, manager picks) | `url_security_advisor_gradio_sb` |
| **Plan-then-execute** (explicit planner node) | `sidekick_with_planning` |
| **Iterative refinement with success criteria** | `patch_to_pr` |
| **Hierarchical subgraphs** (manager controls depth) | `StocksMarketInvestmentRecommender` |
| **Guardrails for domain gating** | `medical_deep_research` |
| **Queue-based streaming from CrewAI** | `engineering_team_with_feedback_loops` |
| **Chunk + multi-level summarisation** | `transcript_summarizer` |
| **Checkpoint replay for dev/test** | `langgraph_checkpoint_howto` |
| **Local model swap** (Ollama drop-in) | `Self_Hosted_Web_Search` |

---

[Back to index](index.md)
