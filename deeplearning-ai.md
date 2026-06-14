---
layout: page
title: DeepLearning.AI — Agentic AI Courses
---

All courses are free at [deeplearning.ai/courses](https://www.deeplearning.ai/courses/).
Notebook-based, 1–3 hours each, pitched at working developers. Built directly with the framework teams.

---

## Start here — foundations

**[Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/)**
The broadest entry point. Covers what agentic AI is, how iterative multi-step workflows differ from
single-turn completions, and when to use an agent vs a simpler approach. Good first watch.

**[AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/courses/ai-agentic-design-patterns-with-autogen/)**
Uses AutoGen but the real content is framework-agnostic design patterns that apply everywhere:
- Reflection — agent critiques its own output before finalising
- Tool use — agent calls external functions
- Planning — agent breaks a task into sub-tasks first
- Multi-agent collaboration — specialists hand off to each other

Understanding these patterns means you can reason about what any framework is doing under the hood.

---

## CrewAI

**[Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/)** ← start here
Role-based agents, sequential vs hierarchical process, tool use within agents, practical pipelines.
Built with the CrewAI team. João (founder) teaches several lessons.

**[Practical Multi AI Agents and Advanced Use Cases with crewAI](https://www.deeplearning.ai/courses/practical-multi-ai-agents-and-advanced-use-cases-with-crewai/)**
Intermediate — agents that collaborate on complex business tasks.

**[Design, Develop, and Deploy Multi-Agent Systems with CrewAI](https://www.deeplearning.ai/courses/design-develop-and-deploy-multi-agent-systems-with-crewai/)**
Production-focused — tools, memory, scaling reliably.

---

## LangGraph

**[AI Agents in LangGraph](https://www.deeplearning.ai/courses/ai-agents-in-langgraph/)** ← start here
ReAct agent pattern, building agents from scratch then with LangGraph, memory, human-in-the-loop.
Best structured intro to LangGraph.

**[Long-Term Agentic Memory With LangGraph](https://www.deeplearning.ai/courses/long-term-agentic-memory-with-langgraph/)**
How agents store, retrieve, and refine knowledge across sessions.

---

## OpenAI SDK

**[Building Systems with the ChatGPT API](https://www.deeplearning.ai/courses/chatgpt-building-system/)** ← most relevant
Breaking down complex tasks, chaining LLM calls, evaluating outputs. Closest course to raw SDK usage.

**[Reasoning with o1](https://www.deeplearning.ai/courses/reasoning-with-o1/)**
Specific to OpenAI's o1 reasoning models — different prompting approach than GPT-4o.

---

## MCP — Model Context Protocol

**[MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/)** ← start here
Building MCP servers in Python, connecting to Claude Desktop, tools/resources/prompts. From Anthropic.

**[Build AI Apps with MCP Server: Working with Box Files](https://www.deeplearning.ai/courses/build-ai-apps-with-mcp-server-working-with-box-files/)**
Practical example using Box as the data source; walks through to a multi-agent system.

---

## Worth knowing about

**[Evaluating AI Agents](https://www.deeplearning.ai/courses/evaluating-ai-agents/)**
How to systematically test and improve agents — important once you move beyond toy examples.

**[Agent Memory: Building Memory-Aware Agents](https://www.deeplearning.ai/courses/agent-memory-building-memory-aware-agents/)**
Making agents remember things across sessions.

**[Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex/)**
When your agents need to query documents or a knowledge base.

**[A2A: The Agent2Agent Protocol](https://www.deeplearning.ai/courses/a2a-the-agent2agent-protocol/)**
Google's open protocol for agents across different frameworks talking to each other — emerging standard alongside MCP.

**[Agent Skills with Anthropic](https://www.deeplearning.ai/courses/agent-skills-with-anthropic/)**
Giving agents expert on-demand knowledge for coding, research, and analysis.

---

## Suggested order

1. Agentic AI *(what is this space)*
2. AI Agentic Design Patterns with AutoGen *(the patterns behind all frameworks)*
3. Building Systems with the ChatGPT API *(direct SDK, no framework)*
4. Multi AI Agent Systems with crewAI *(first framework)*
5. AI Agents in LangGraph *(lower level, more control)*
6. MCP: Build Rich-Context AI Apps with Anthropic *(connecting agents to tools)*
7. Evaluating AI Agents *(making it production-ready)*

---

[Back to index](index.md)
