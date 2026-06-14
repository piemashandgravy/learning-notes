---
layout: page
title: OpenAI Agents SDK
---

## What it is

OpenAI's official framework for building agents — separate from the base `openai` package.
Where the OpenAI SDK gives you raw API access, the Agents SDK gives you higher-level
primitives: agents with instructions and tools, handoffs between specialists, guardrails,
sessions, and built-in tracing.

Sits at a similar level of abstraction to CrewAI but is OpenAI-native and tighter — less
framework magic, more explicit wiring.

```bash
pip install openai-agents
```

---

## Core pattern

```python
from agents import Agent, Runner

agent = Agent(
    name="Research Assistant",
    instructions="You are a concise research assistant. Answer in bullet points.",
    model="gpt-4o-mini"
)

# Synchronous run
result = Runner.run_sync(agent, "What are the main use cases for vector databases?")
print(result.final_output)

# Async run (preferred in production)
import asyncio

async def main():
    result = await Runner.run(agent, "Explain RAG in one paragraph.")
    print(result.final_output)

asyncio.run(main())
```

---

## Function tools

The `@function_tool` decorator turns any Python function into a tool the agent can call.
It extracts the schema automatically from the type hints and docstring.

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_stock_price(ticker: str) -> str:
    """Get the current price of a stock.

    Args:
        ticker: The stock ticker symbol, e.g. AAPL.
    """
    # Your real implementation here
    return f"{ticker}: £142.50"

@function_tool
async def search_news(query: str, max_results: int = 5) -> list[str]:
    """Search for recent news articles on a topic.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.
    """
    # Your real implementation here
    return [f"Article about {query}"]

agent = Agent(
    name="Finance Agent",
    instructions="You answer questions about stocks using the tools available.",
    tools=[get_stock_price, search_news],
    model="gpt-4o-mini"
)
```

The docstring `Args:` block becomes the tool description the model sees — write it clearly.

---

## Hosted tools (OpenAI-managed)

Tools that run on OpenAI's infrastructure — no implementation needed on your side.

```python
from agents import Agent, WebSearchTool, FileSearchTool, CodeInterpreterTool

agent = Agent(
    name="Research Agent",
    instructions="Use web search to find current information.",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=5,
            vector_store_ids=["vs_abc123"]  # your OpenAI vector store
        ),
        CodeInterpreterTool(),  # sandboxed Python execution
    ]
)
```

- `WebSearchTool` — live web search
- `FileSearchTool` — retrieval over an OpenAI vector store
- `CodeInterpreterTool` — runs Python in a sandbox
- `ImageGenerationTool` — generates images via DALL-E

---

## Handoffs — routing between specialist agents

Handoffs let a triage agent delegate to a specialist. The specialist then takes over the
conversation for the rest of that run — the triage agent doesn't narrate the result.

```python
from agents import Agent, Runner, handoff

billing_agent = Agent(
    name="Billing Specialist",
    instructions="You handle all billing questions and invoice disputes."
)

refund_agent = Agent(
    name="Refund Specialist",
    instructions="You process refund requests. Always ask for the order number first."
)

triage_agent = Agent(
    name="Support Triage",
    instructions="Route the user to the right specialist. Do not answer directly.",
    handoffs=[
        handoff(billing_agent),
        handoff(refund_agent)
    ]
)

result = Runner.run_sync(triage_agent, "I need a refund for order #4521")
print(result.final_output)
```

The model sees each handoff as a tool (`transfer_to_billing_specialist`, etc.) and picks
the right one based on the conversation.

---

## Agents as tools — manager keeps control

Alternative to handoffs: the manager agent calls specialists as tools and synthesises
the results itself rather than handing off entirely.

```python
from agents import Agent, Runner

researcher = Agent(
    name="Researcher",
    instructions="Find information on the given topic. Be factual and concise."
)

writer = Agent(
    name="Writer",
    instructions="Turn research notes into a clear, readable summary."
)

manager = Agent(
    name="Manager",
    instructions="Use the researcher to gather information, then the writer to produce the output.",
    tools=[
        researcher.as_tool(
            tool_name="research",
            tool_description="Research a topic and return key facts."
        ),
        writer.as_tool(
            tool_name="write_summary",
            tool_description="Turn notes into a polished summary."
        )
    ]
)

result = Runner.run_sync(manager, "Write a summary of how LangGraph works.")
print(result.final_output)
```

**Handoffs vs agents-as-tools:**

| | Handoffs | Agents as tools |
|---|---|---|
| Who responds to the user? | The specialist | The manager |
| Best for | Routing to a dedicated specialist | Bounded subtasks within a larger flow |
| Manager involvement | Hands off entirely | Stays in control throughout |

---

## Sessions — memory across turns

Sessions persist conversation history automatically across multiple `Runner.run()` calls.

```python
from agents import Agent, Runner, Session

agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
session = Session()

# Turn 1
result = await Runner.run(agent, "My name is Matt.", session=session)
print(result.final_output)

# Turn 2 — agent remembers the previous turn
result = await Runner.run(agent, "What's my name?", session=session)
print(result.final_output)  # "Your name is Matt."
```

For persistence across process restarts, pass a `session_id` and back it with Redis.

---

## Guardrails

Validate agent inputs and outputs before they reach the user or the model.

```python
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, RunContextWrapper
from pydantic import BaseModel

class SafetyCheck(BaseModel):
    is_safe: bool
    reason: str

@input_guardrail
async def no_personal_data(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
    # Run a fast check model or regex here
    contains_pii = any(term in input.lower() for term in ["national insurance", "passport"])
    return GuardrailFunctionOutput(
        output_info=SafetyCheck(is_safe=not contains_pii, reason="PII detected" if contains_pii else "OK"),
        tripwire_triggered=contains_pii
    )

agent = Agent(
    name="Safe Agent",
    instructions="Answer helpfully.",
    input_guardrails=[no_personal_data]
)
```

If the tripwire triggers, the run is stopped and a `GuardrailTripwireTriggered` exception is raised.

---

## Built-in tracing

Every run is automatically traced. View traces at [platform.openai.com/traces](https://platform.openai.com/traces) —
no extra setup needed when using OpenAI models.

To disable:
```python
from agents import RunConfig

result = await Runner.run(
    agent,
    "Hello",
    run_config=RunConfig(tracing_disabled=True)
)
```

---

## Vs other frameworks

| | OpenAI Agents SDK | CrewAI | LangGraph |
|---|---|---|---|
| Abstraction | Medium | High | Low |
| Provider lock-in | OpenAI-first (others supported) | Any via LiteLLM | Any |
| Handoffs | Native, clean | Via hierarchical process | Manual edges |
| Tracing | Built-in to OpenAI dashboard | Via third-party | LangSmith |
| Best for | OpenAI-native, quick multi-agent | Role-based crews | Complex stateful loops |

---

## Gotchas

- `Runner.run_sync()` is a convenience wrapper — use `await Runner.run()` in async code
- Docstrings on `@function_tool` functions are not optional — the model uses them to decide when to call the tool; vague docstrings produce wrong tool choices
- Handoffs transfer control completely — if you want the manager to stay in the loop, use `agent.as_tool()` instead
- Sessions store history in memory by default — wire Redis if you need cross-process persistence

---

## Resources

- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/)
- [GitHub repo + examples](https://github.com/openai/openai-agents-python)
- [Ed Donner — Agentic AI course, Week 2](ed-donner.md) — full week dedicated to this SDK
- [DeepLearning.AI — Building Systems with the ChatGPT API](https://www.deeplearning.ai/courses/chatgpt-building-system/) — covers the underlying patterns

---

## From your code

**Pattern — Using `@function_tool` with Docstrings**

The `@function_tool` decorator automatically uses type hints and docstrings to define the API for agent-accessible functions. Ensure your docstrings clearly describe parameters and return types, as vague descriptions can lead to incorrect tool usage by the model.

**Gotcha — Asynchronous Operations**

While `Runner.run_sync()` is convenient for scripts, use `await Runner.run()` in production — it handles concurrency properly and is the expected pattern in any async context.

**Pattern — Handoffs vs. Agents as Tools**

Handoffs transfer control entirely to a specialist — the manager steps back. `agent.as_tool()` keeps the manager in control and synthesises results. Choose based on whether the specialist should own the response or just assist with a bounded subtask.

---

[Back to index](index.md)
