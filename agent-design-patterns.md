---
layout: page
title: Agent Design Patterns
---

Framework-agnostic patterns that appear across LangGraph, CrewAI, OpenAI Agents SDK, and AutoGen.
Understanding these as patterns — separate from any specific library — makes it easier to recognise
them in code, apply them deliberately, and switch frameworks without starting from scratch.

---

## ReAct — the foundational loop

The basis of almost every tool-using agent: **Re**ason, **Act**, observe, repeat.

```
Think: "I need the current price of AAPL to answer this."
Act:   call get_stock_price("AAPL")
Observe: "$213.40"
Think: "Now I can answer."
Respond: "Apple's current price is $213.40."
```

The model sees the tool result appended to the conversation and decides whether to call
another tool or respond. Most frameworks implement this loop for you — you just define the tools.

**When it breaks:** the model loops indefinitely calling tools instead of stopping.
Fix: set a max iterations limit, or add an explicit stopping condition.

---

## Plan-then-execute

Add an explicit planning step before any tools are called. The planner generates a list of
steps; the executor works through them.

```
User input → Planner node → [step 1, step 2, step 3] → Worker node → Tool calls → Response
```

```python
# LangGraph sketch
def planner(state):
    plan = llm.invoke(f"Create a step-by-step plan to: {state['input']}")
    return {"plan": plan.content, "current_step": 0}

def worker(state):
    step = state["plan"][state["current_step"]]
    result = execute_tool(step)
    return {"results": state["results"] + [result], "current_step": state["current_step"] + 1}

def router(state):
    if state["current_step"] >= len(state["plan"]):
        return "respond"
    return "worker"
```

**Why bother:** without planning, agents tend to dive into the first tool that looks relevant
and lose sight of the overall goal. Planning forces decomposition before action.

**Where to look:** `sidekick_with_planning` in the [community contributions](community-contributions.md).

---

## Reflection / self-critique

The agent generates a draft, then critiques it, then revises. Can be one agent reviewing its
own output or a separate critic agent.

```
Generator → Draft → Critic → Feedback → Generator → Revised draft → (repeat or done)
```

```python
# Single-agent reflection with OpenAI SDK
def reflect_and_revise(task: str, max_rounds: int = 3) -> str:
    draft = llm_call(f"Complete this task: {task}")

    for _ in range(max_rounds):
        critique = llm_call(
            f"Critique this output for the task '{task}':\n\n{draft}\n\n"
            "List specific improvements needed. If it's good enough, say APPROVED."
        )
        if "APPROVED" in critique:
            break
        draft = llm_call(f"Revise based on this critique:\n\n{critique}\n\nOriginal:\n\n{draft}")

    return draft
```

**Key insight:** the critic and generator can use different prompts (or even different models —
a cheap model for criticism, expensive for generation) to save cost.

---

## Iterative refinement with success criteria

A tighter version of reflection: define explicit, checkable success criteria upfront,
then loop until they're met or a max iteration limit is hit.

```python
# LangGraph pattern
def evaluator(state):
    criteria = [
        "contains a code example",
        "under 200 words",
        "mentions the main gotcha"
    ]
    checks = [llm_check(state["output"], c) for c in criteria]
    passed = all(checks)
    return {"passed": passed, "iteration": state["iteration"] + 1}

def router(state):
    if state["passed"] or state["iteration"] >= 5:
        return "done"
    return "generator"
```

**Where to look:** `patch_to_pr` in the [community contributions](community-contributions.md) —
iterates up to 5 times until a PR description passes structured criteria.

---

## Parallel fan-out

Run multiple agents or tool calls simultaneously and aggregate results. The main use case:
research tasks where you're gathering from several independent sources at once.

```python
import asyncio

async def research(topic: str) -> dict:
    # All three run at the same time
    web, papers, news = await asyncio.gather(
        search_web(topic),
        search_papers(topic),
        search_news(topic)
    )
    return {"web": web, "papers": papers, "news": news}
```

**In LangGraph:** use `Send` to fan out to multiple subgraph instances, then a reducer
node to aggregate.

**In CrewAI:** set `Process.parallel` on the crew — tasks with no dependencies run
concurrently.

**Watch out for:** rate limits. Firing 10 parallel LLM calls at once can hit OpenAI's
TPM limits. Add a semaphore if you're fanning out at scale.

---

## Agent-as-tool vs handoff

Two different ways for a manager agent to delegate to a specialist:

| | Handoff | Agent-as-tool |
|---|---|---|
| Who responds to user? | The specialist | The manager |
| Manager involvement | Steps back entirely | Stays in control |
| Best for | Routing to a dedicated owner | Bounded subtask within a larger flow |

```python
# OpenAI Agents SDK — agent as tool
specialist = Agent(name="Specialist", instructions="...")

manager = Agent(
    name="Manager",
    tools=[
        specialist.as_tool(
            tool_name="consult_specialist",
            tool_description="Get specialist input on a specific question."
        )
    ]
)
```

Use **handoffs** when the specialist owns the problem end-to-end.
Use **agent-as-tool** when the manager needs to synthesise results from multiple specialists.

**Where to look:** `code_review_agent` — three specialist agents (security, performance, style)
as tools for a manager that scores and synthesises findings.

---

## Competitive parallelism

Two agents tackle the same task independently; a judge picks the better result.
Trades cost (2x LLM calls) for quality and reliability.

```python
async def competitive_run(task: str) -> str:
    result_a, result_b = await asyncio.gather(
        agent_a.run(task),
        agent_b.run(task)
    )
    winner = judge_agent.run(
        f"Task: {task}\n\nOption A: {result_a}\n\nOption B: {result_b}\n\n"
        "Which is better and why? Return the winner's text."
    )
    return winner
```

**When to use:** high-stakes outputs where quality matters more than cost.
Also useful as a hedge against model failures — if one agent errors, the other still produces output.

**Where to look:** `url_security_advisor_gradio_sb` in the community contributions.

---

## Hierarchical subgraphs

A manager graph calls specialist subgraphs and decides — based on results — whether to
invoke them again or stop. Enables dynamic depth without hardcoding a fixed pipeline.

```
Manager graph
├── decides: "need more analysis"
│   └── calls Analyst subgraph (iteration 1)
├── decides: "still uncertain"
│   └── calls Analyst subgraph (iteration 2)
└── decides: "confident enough" → produces output
```

In LangGraph this is a compiled subgraph called as a node. The manager's state includes
a counter or confidence score that drives the routing decision.

**Where to look:** `StocksMarketInvestmentRecommender` — the most sophisticated example in
the community contributions, with a manager controlling analyst depth via Pydantic state.

---

## Guardrails / domain gating

Validate input before spending tokens on the main task. Cheap checks upfront prevent
expensive downstream failures.

```python
def domain_gate(user_input: str) -> str | None:
    """Returns an error message if input is out of domain, else None."""
    # Fast check — regex, classifier, or a cheap LLM call
    if not is_medical_query(user_input):
        return "This system only handles medical literature queries."
    if contains_pii(user_input):
        return "Please don't include personal health information."
    return None

def run_pipeline(user_input: str) -> str:
    error = domain_gate(user_input)
    if error:
        return error
    return expensive_research_pipeline(user_input)
```

**Layers worth adding:**
- Input format validation (is this a valid URL / ticker / query?)
- Domain check (is this in scope?)
- PII / safety check
- Output check (does the response meet quality criteria before returning?)

**Where to look:** `medical_deep_research` — validates domain before fanning out to 5 parallel searches.

---

## Human-in-the-loop

Pause the agent at a decision point and wait for human approval before continuing.
Essential for any action with real-world consequences (sending emails, running code, spending money).

```python
# LangGraph — interrupt before a dangerous action
from langgraph.types import interrupt

def execute_action(state):
    action = state["proposed_action"]

    # Pause here and surface the action for approval
    approval = interrupt({
        "action": action,
        "message": f"About to execute: {action}. Approve?"
    })

    if approval != "yes":
        return {"result": "Action cancelled by user."}

    return {"result": run_action(action)}
```

The graph pauses, serialises state to a checkpoint, and resumes when the human responds.
LangGraph's checkpointing makes this resumable across process restarts.

**When you need it:** file deletion, API calls that cost money, sending messages, anything irreversible.

---

## Chunk + multi-level summarisation

For inputs that exceed the context window: chunk the input, summarise each chunk, then
summarise the summaries.

```
Long document
├── chunk 1 → summary 1 ─┐
├── chunk 2 → summary 2 ─┤→ section summary ─┐
├── chunk 3 → summary 3 ─┘                   ├→ final summary
├── chunk 4 → summary 4 ─┐                   │
└── chunk 5 → summary 5 ─┴→ section summary ─┘
```

```python
def hierarchical_summarise(text: str, chunk_size: int = 4000) -> str:
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    chunk_summaries = [summarise(c) for c in chunks]

    if len(chunk_summaries) <= 3:
        return summarise("\n\n".join(chunk_summaries))

    # Recurse for very long documents
    return hierarchical_summarise("\n\n".join(chunk_summaries))
```

**Where to look:** `transcript_summarizer` in the community contributions — processes long
VTT transcripts with nested summarisation running on local Ollama/LLaMA3.

---

## Choosing a pattern

| Situation | Pattern to reach for |
|---|---|
| Agent drifts off task | Plan-then-execute |
| Output quality is inconsistent | Reflection / iterative refinement |
| Multiple independent sources to query | Parallel fan-out |
| High-stakes single output | Competitive parallelism |
| Multiple specialists, manager synthesises | Agent-as-tool |
| Multiple specialists, each owns a domain | Handoffs |
| Long document exceeds context | Chunk + summarise |
| Action has real-world consequences | Human-in-the-loop |
| Expensive pipeline, many invalid inputs | Guardrails / domain gating |

---

[Back to index](index.md)
