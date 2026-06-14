---
layout: page
title: LangGraph
---

## What it is

Low-level graph-based agent orchestration from the LangChain team. You define a graph where
nodes are Python functions (or agents) and edges define the flow between them — including
conditional branching and cycles. More verbose than CrewAI but gives you full control.

The key thing LangGraph adds over a simple chain: **loops**. Agents can revisit earlier steps,
retry, reflect on their own output, or wait for human input mid-run.

---

## Core pattern

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. Define your state — this is passed between all nodes
class State(TypedDict):
    messages: list
    next_step: str

# 2. Define nodes (just Python functions)
def research_node(state: State) -> State:
    # Call your LLM or tool here
    result = "...some research result..."
    return {"messages": state["messages"] + [result]}

def review_node(state: State) -> State:
    # Another LLM call — maybe checking the research quality
    approved = True
    return {"next_step": "end" if approved else "research"}

# 3. Build the graph
graph = StateGraph(State)
graph.add_node("research", research_node)
graph.add_node("review", review_node)

graph.set_entry_point("research")
graph.add_edge("research", "review")

# Conditional edge — loops back if review rejects
graph.add_conditional_edges(
    "review",
    lambda state: state["next_step"],
    {"end": END, "research": "research"}
)

app = graph.compile()
result = app.invoke({"messages": [], "next_step": ""})
```

---

## Key concepts

- `StateGraph` — the graph; typed state flows through every node
- `Node` — any Python function that takes state and returns updated state
- `Edge` — connection between nodes; can be fixed or conditional
- `Conditional edge` — branch based on state (this is how you get loops and decisions)
- `compile()` — locks the graph and returns a runnable app
- `invoke()` — runs the graph synchronously; `stream()` for token-by-token output

---

## LangGraph vs CrewAI

| | CrewAI | LangGraph |
|---|---|---|
| Abstraction level | High — roles, crews, tasks | Low — nodes, edges, state |
| Setup speed | Fast | More verbose |
| Loops / cycles | Limited | First-class |
| Conditional flow | Basic | Full control |
| Debugging | Harder to inspect | State is explicit, easier to trace |
| Best for | Role-based team pipelines | Complex stateful workflows |

Rule of thumb: start with CrewAI, move to LangGraph when you need branching logic or loops.

---

## Gotchas

- State must be a `TypedDict` (or Pydantic model) — LangGraph is strict about this
- Every node must return a dict that matches (a subset of) the state schema
- Cycles are allowed but easy to make infinite — always have a termination condition
- LangGraph and LangChain are separate packages; you don't need all of LangChain to use LangGraph

---

## Resources

- [LangGraph docs](https://langchain-ai.github.io/langgraph/) — conceptual guides are good
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph) — examples in `/examples`
- [DeepLearning.AI — AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — free short course; covers ReAct agents, memory, and human-in-the-loop

---

[Back to index](index.md)
