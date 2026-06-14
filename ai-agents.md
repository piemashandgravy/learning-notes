---
layout: page
title: AI & Agents
---

## CrewAI

Multi-agent orchestration framework. Agents are given a role, goal, and backstory.
Tasks are assigned to agents and chained sequentially or hierarchically via a Crew.

**Key concepts**
- `Agent` — the worker (role + goal + backstory + llm)
- `Task` — a unit of work assigned to an agent
- `Crew` — orchestrates agents and tasks; runs via `crew.kickoff()`
- `Process.sequential` — tasks run in order; `Process.hierarchical` adds a manager agent

**LLM wiring**
- Use `LLM(model="...")` from `crewai` — wraps LiteLLM, not LangChain
- Model strings: `"gpt-4o-mini"`, `"azure/your-deployment"`, `"gemini/gemini-2.0-flash"`
- At work (Azure OpenAI + managed identity): use `DefaultAzureCredential` from `azure-identity`; no API keys needed
- Avoid passing LangChain objects (`ChatOpenAI`, `ChatGoogleGenerativeAI`) — newer CrewAI versions reject them

**Gotchas**
- Default `max_iter=25` causes very long runs on extraction tasks — set `max_iter=5`
- Don't use CrewAI for PDF→JSON extraction; use direct API calls with `response_format=json_object` instead
- `output_file` on a Task writes raw LLM output including markdown fences — parse manually if needed

**Resources**
- [Official examples repo](https://github.com/crewAIInc/crewAI-examples) — trip planner, research agent, etc.
- [Official docs](https://docs.crewai.com) — quickstart and core concepts are solid
- [DeepLearning.AI short course](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — free, structured, built with CrewAI team; best starting point

---

[Back to index](index.md)
