---
layout: home
title: Learning Notes
---

A running log of agentic AI tools and frameworks — written for a Python developer branching out into this space.
Each page covers the core concepts, practical gotchas, and useful resources.

---

## The landscape (quick orientation)

These four tools sit at different levels of the stack:

| Tool | What it is | When to reach for it |
|---|---|---|
| **OpenAI SDK** | Direct API access | Simplest tasks; full control; no overhead |
| **MCP** | Standard for connecting AI to tools/data | Exposing your own tools to any LLM |
| **CrewAI** | High-level multi-agent framework | Quick multi-agent pipelines; role-based teams |
| **LangGraph** | Low-level graph-based agent orchestration | Complex stateful workflows; loops; full control |

A reasonable learning path: **OpenAI SDK → CrewAI → LangGraph → MCP**

---

## Topics

- [OpenAI SDK](openai-sdk.md)
- [CrewAI](crewai.md)
- [LangGraph](langgraph.md)
- [MCP — Model Context Protocol](mcp.md)
- [DeepLearning.AI — Agentic AI Courses](deeplearning-ai.md)
- [Supporting Libraries — asyncio, Pydantic, Serper, HuggingFace](supporting-libraries.md)

---

## How to add notes

**From your dev machine**
Edit any `.md` file in the repo, then `git add . && git commit -m "..." && git push`. Pages rebuilds in ~30 seconds.

**From any browser (Chromebook, phone, work)**
Open the repo on GitHub, click a file, hit the pencil icon to edit in place.
Or press `.` on the repo homepage to open a full VS Code editor in the browser.

**What's worth adding**
- Things that surprised you or only clicked after confusion
- Code patterns you'll want to copy-paste later
- Gotchas — the things that wasted time
- Links to a specific doc page that was particularly clear, plus 3–5 bullets on what you took from it

**On external documentation**
Link to it — don't copy it. External docs (e.g. [LangGraph](https://github.com/langchain-ai/langgraph)) update constantly and a pulled copy goes stale.
The valuable thing to write here is your own understanding: what the docs didn't make obvious, what pattern finally made it click.

---

*Last updated: June 2026*
