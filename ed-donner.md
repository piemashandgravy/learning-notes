---
layout: page
title: Ed Donner — Courses
---

Ed Donner is Co-Founder and CTO at Nebula.io. His courses are among the most practical
available on LLM engineering and agentic AI — hands-on, notebook-based, and built by
someone actively building production systems. All materials are free on GitHub.

---

## Course 1: Complete Agentic AI Engineering

**GitHub:** [github.com/ed-donner/agents](https://github.com/ed-donner/agents) (5,000+ stars)

A 6-week programme covering the full agentic AI stack. Each week focuses on one framework,
building up from foundations to production patterns.

| Week | Topic | What you build |
|---|---|---|
| 1 | Foundations | Agent patterns from first principles |
| 2 | OpenAI Agents SDK | Agents using OpenAI's official SDK |
| 3 | CrewAI | Multi-agent crew pipelines |
| 4 | LangGraph | Graph-based stateful agents |
| 5 | AutoGen | Collaborative multi-agent systems |
| 6 | MCP | Connecting agents to external tools via Model Context Protocol |

**Why it's worth doing:**
Each week you implement the same class of problem in a different framework — so by the end
you have a genuine basis for comparison rather than just knowing one tool. The progression
from OpenAI SDK → CrewAI → LangGraph mirrors the recommended learning path on this site.

---

## Course 2: Mastering LLM Engineering

**GitHub:** [github.com/ed-donner/llm_engineering](https://github.com/ed-donner/llm_engineering) (6,000+ stars)

An 8-week programme covering LLMs from the ground up — before agents, before frameworks.
Starts with raw API usage, local models, and GPU compute, and builds towards an autonomous
agentic system by week 8.

**Topics covered:**
- Frontier model APIs (OpenAI, Anthropic, Google)
- Running models locally with Ollama
- GPU compute via Google Colab
- RAG and retrieval patterns
- Fine-tuning
- Building toward a full agentic AI solution

**Why it's worth doing:**
If the Agentic AI course is "how to build agents", this course is "how LLMs work and why
they behave the way they do". The two complement each other well — this one builds intuition
that makes debugging agents much easier.

---

## Course 3: Generative AI and Agentic AI in Production

**GitHub:** [github.com/ed-donner/production](https://github.com/ed-donner/production)

The production-focused follow-on — covers what happens after you've built something and
want to deploy it reliably. Smaller than the other two but fills an important gap.

---

## Suggested order

1. **LLM Engineering** (weeks 1-4) — get comfortable with raw LLM APIs and local models
2. **Agentic AI** (all 6 weeks) — build agents across every major framework
3. **LLM Engineering** (weeks 5-8) — RAG, fine-tuning, building toward production
4. **Production** — deploy and operationalise

Or if you want to get into agents faster: skip straight to **Agentic AI week 1**, then
revisit **LLM Engineering** for depth on the parts that feel unclear.

---

## Also worth reading

**Towards Data Science** — [towardsdatascience.com](https://towardsdatascience.com)

Medium publication with a consistently high signal-to-noise ratio for ML and AI engineering
topics. Particularly good for:
- Practical deep-dives on frameworks (LangGraph, CrewAI, vector DBs)
- Comparisons between approaches ("LangGraph vs CrewAI for X")
- Worked examples with real code

Readable without a Medium subscription for a limited number of articles per month.
Search within the site for a specific framework name — the community-written tutorials
often fill gaps that official docs don't cover.

---

[Back to index](index.md)
