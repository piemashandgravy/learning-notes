---
layout: page
title: Debugging & Observability
---

Agents are harder to debug than regular code because the interesting decisions happen inside
LLM calls — you can't step through them in a debugger. The fix is observability: making every
decision, tool call, and state transition visible so you can diagnose what actually happened.

---

## OpenAI Agents SDK — built-in tracing

Zero configuration. Every run is automatically traced and visible at
[platform.openai.com/traces](https://platform.openai.com/traces).

The trace shows:
- Each agent turn and its output
- Every tool call with inputs and outputs
- Handoffs between agents
- Token usage per step

```python
# Nothing to add — tracing is on by default when using OpenAI models.
# To disable for a specific run:
from agents import Runner, RunConfig

result = await Runner.run(
    agent,
    "Hello",
    run_config=RunConfig(tracing_disabled=True)
)
```

**Custom spans** — wrap your own code in a trace:

```python
from agents.tracing import trace, custom_span

with trace("my-pipeline"):
    with custom_span("preprocessing"):
        data = preprocess(input)
    result = await Runner.run(agent, data)
```

---

## LangGraph — LangSmith

LangSmith is LangChain's observability platform. Works with LangGraph with two environment
variables — no code changes needed.

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key_here
export LANGCHAIN_PROJECT=my-project   # optional — groups traces in the UI
```

Sign up at [smith.langchain.com](https://smith.langchain.com) — free tier available.

**What you see in LangSmith:**
- Every node execution with input/output state
- Full LLM prompt and response for each call
- Tool calls and results
- Graph structure visualised
- Latency and token usage per node

**Programmatic access** — useful for evaluation:

```python
from langsmith import Client

client = Client()
runs = client.list_runs(project_name="my-project", run_type="chain")

for run in runs:
    print(run.name, run.status, run.total_tokens)
```

**`@traceable` decorator** — trace any function outside of LangGraph:

```python
from langsmith import traceable

@traceable(name="my-search-tool")
def search(query: str) -> list[str]:
    return serper_search(query)
```

---

## LangGraph — inspecting state directly

Before reaching for LangSmith, print state at each node during development:

```python
def my_node(state: MyState) -> dict:
    print(f"[my_node] input: {state['messages'][-1].content[:100]}")
    result = llm.invoke(state["messages"])
    print(f"[my_node] output: {result.content[:100]}")
    return {"messages": [result]}
```

**Stream events instead of waiting for final output:**

```python
async for event in graph.astream_events({"messages": [("user", "hello")]}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="", flush=True)
    elif event["event"] == "on_tool_start":
        print(f"\n[tool call] {event['name']} — {event['data']['input']}")
```

**Replay from a checkpoint** — re-run a specific node without re-running the whole graph:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "session-1"}}

# Get saved state at any point
state = graph.get_state(config)
print(state.values)   # current state
print(state.next)     # which node runs next

# Resume from that state (without re-running earlier nodes)
result = await graph.ainvoke(None, config)
```

See `langgraph_checkpoint_howto` in the [community contributions](community-contributions.md)
for a worked example of this.

---

## CrewAI — verbose mode and AgentOps

**Verbose mode** is the fastest way to see what's happening:

```python
from crewai import Agent, Crew, Task

agent = Agent(
    role="Researcher",
    goal="...",
    backstory="...",
    verbose=True    # prints each agent's reasoning and tool calls
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
```

**AgentOps** — full observability dashboard for CrewAI:

```python
import agentops
agentops.init(os.environ["AGENTOPS_API_KEY"])

# That's it — CrewAI integrates automatically from here
crew.kickoff(inputs={"topic": "..."})
```

Sign up at [agentops.ai](https://agentops.ai) — free tier available. Shows session replays,
cost per run, agent decision trees, and tool usage.

**Langfuse** is a popular open-source alternative to AgentOps:

```python
os.environ["LANGFUSE_PUBLIC_KEY"] = "..."
os.environ["LANGFUSE_SECRET_KEY"] = "..."
# CrewAI picks it up via its LiteLLM integration automatically
```

---

## AutoGen — runtime logging

```python
import autogen

# Log to SQLite
logging_session_id = autogen.runtime_logging.start(
    logger_type="sqlite",
    config={"dbname": "autogen_runs.db"}
)

# ... run your agents ...

autogen.runtime_logging.stop()
```

Query the log afterwards:

```python
import sqlite3
conn = sqlite3.connect("autogen_runs.db")
rows = conn.execute("SELECT agent_name, request, response FROM chat_completions").fetchall()
for row in rows:
    print(row[0], row[1][:80])
```

For a simpler option, set `human_input_mode="ALWAYS"` during development — you see every
message and can intervene at any turn.

---

## Common failure modes

### Infinite loop
**Symptom:** agent keeps calling tools and never stops.  
**Cause:** no termination condition, or the model never decides it's done.  
**Fix:** set `max_iterations` / `max_round` / `max_consecutive_auto_reply`. Add explicit termination instructions to the system prompt: *"When the task is complete, reply with TERMINATE."*

### Wrong tool called
**Symptom:** agent calls the wrong tool, or calls it with wrong parameters.  
**Cause:** vague tool descriptions or overlapping tool names.  
**Fix:** make tool descriptions specific and distinct. Describe *when* to call it, not just *what* it does. Check the tool schema being sent — log `response.model_dump()` before the agent runs.

### Context window overflow
**Symptom:** `context_length_exceeded` error, or agent "forgets" earlier turns.  
**Cause:** too much history accumulates in a long-running conversation.  
**Fix:** summarise old messages before they're dropped. In LangGraph, add a node that compresses message history when it exceeds a threshold. In CrewAI/AutoGen, set shorter `max_iter` / `max_round`.

### Hallucinated tool calls
**Symptom:** model refers to tools that don't exist, or tries to call a function not in the schema.  
**Cause:** system prompt mentions tools by name without registering them, or model trained on similar but different APIs.  
**Fix:** only mention tools in system prompts if they're registered. Use `tool_choice="required"` to force real tool use rather than text descriptions of tool use.

### State corruption (LangGraph)
**Symptom:** state values unexpectedly overwritten or lost between nodes.  
**Cause:** wrong reducer — default reducer overwrites, `add_messages` appends. Mixing them incorrectly.  
**Fix:** print state at each node boundary. Check your `Annotated` type on each state field matches the behaviour you expect.

### Silent tool failure
**Symptom:** agent carries on as if the tool succeeded, but the result is wrong.  
**Cause:** tool returns an empty string or `None` on failure instead of raising.  
**Fix:** tools should raise exceptions on failure — the framework catches them and sends the error back to the model as context, letting it retry or recover.

---

## What to log in production

```python
import time
from dataclasses import dataclass

@dataclass
class RunRecord:
    session_id: str
    input: str
    output: str
    tool_calls: list[str]
    total_tokens: int
    duration_seconds: float
    success: bool
    error: str | None = None
```

**Minimum useful signals:**
- Input + final output (for quality review)
- Which tools were called and in what order (for debugging loops)
- Total token count (for cost tracking)
- Wall-clock duration (slow runs often indicate a loop)
- Whether it terminated cleanly or hit a max-iteration limit

**Don't log:** full message history by default — it's large and usually only needed when
debugging a specific failed run. Log the session ID and retrieve full history on demand.

---

## Debugging checklist

When an agent run produces a wrong or unexpected result:

1. **Check the trace first** — OpenAI traces / LangSmith / AgentOps before adding any print statements
2. **Find the last good state** — which node/turn did the right thing? Where did it go wrong?
3. **Inspect the exact prompt** — what did the model actually receive? Hidden system messages, injected context, or tool descriptions can cause surprising behaviour
4. **Check tool outputs** — did the tool return what you expected? Log inputs *and* outputs
5. **Replay from checkpoint** — in LangGraph, replay from the last good state rather than re-running the whole graph
6. **Reduce to minimal reproduction** — swap in a mock tool that returns a fixed value to isolate whether the issue is in the tool or the agent's reasoning

---

## Resources

- [LangSmith docs](https://docs.smith.langchain.com/)
- [AgentOps](https://agentops.ai)
- [Langfuse](https://langfuse.com) — open-source alternative
- [OpenAI platform traces](https://platform.openai.com/traces)
- [LangGraph — how to add human-in-the-loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)

---

[Back to index](index.md)
