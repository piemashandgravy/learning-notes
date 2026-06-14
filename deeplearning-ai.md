---
layout: page
title: DeepLearning.AI — Agentic AI Courses
---

## Overview

Andrew Ng's DeepLearning.AI platform hosts a series of free short courses on agentic AI,
many built directly with the framework teams. Each course is 1–3 hours, notebook-based,
and pitched at working developers rather than researchers. The best structured learning
path for this stack.

All courses are free at [deeplearning.ai/short-courses](https://www.deeplearning.ai/short-courses/).

---

## Recommended order

### 1. AI Agents in LangGraph
**[deeplearning.ai/short-courses/ai-agents-in-langgraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/)**

Built with the LangChain team. Covers:
- ReAct agent pattern (Reason + Act loop)
- Building agents from scratch, then with LangGraph
- Memory and persistence across turns
- Human-in-the-loop interrupts
- Essay writing agent as the running example

*Good first course — teaches the underlying agent pattern before adding framework abstractions.*

---

### 2. Multi AI Agent Systems with crewAI
**[deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)**

Built with the CrewAI team. Covers:
- Role-playing agents and why backstory matters
- Sequential vs hierarchical process
- Tool use within agents
- Multi-agent collaboration patterns
- Practical examples: research pipeline, customer support, financial analysis

*Best starting point specifically for CrewAI. João (CrewAI founder) teaches several lessons.*

---

### 3. MCP: Build Rich-Context AI Apps with Anthropic
**[deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/)**

Built with Anthropic. Covers:
- What MCP is and why it exists
- Building MCP servers in Python
- Connecting servers to Claude Desktop
- Resources, tools, and prompts
- Multi-server setups

*Take this after you understand tool calling from the SDK/LangGraph courses.*

---

### 4. AI Agentic Design Patterns with AutoGen
**[deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/)**

Uses Microsoft's AutoGen framework but the core content — design patterns — applies everywhere:
- Reflection: agent critiques its own output
- Tool use pattern
- Planning pattern
- Multi-agent collaboration pattern

*The design patterns are framework-agnostic and worth understanding regardless of which tool you use.*

---

### 5. Building Agentic RAG with LlamaIndex
**[deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/)**

Covers retrieval-augmented generation in an agentic context:
- Router agents that select the right data source
- Tool-calling over document indexes
- Multi-document agents

*Useful when your agents need to query documents or a knowledge base.*

---

## The four agentic design patterns (Andrew Ng)

These patterns underpin everything across all the frameworks:

1. **Reflection** — the agent reviews and critiques its own output before finalising
2. **Tool use** — the agent calls external functions (search, code execution, APIs)
3. **Planning** — the agent breaks a task into sub-tasks before executing
4. **Multi-agent collaboration** — specialist agents work in parallel or hand off to each other

Understanding these patterns means you can reason about what any framework is doing under the hood.

---

[Back to index](index.md)
