---
layout: page
title: Agent Memory
---

## The problem

By default an LLM has no memory. Every call starts fresh — it knows nothing about previous
conversations, prior results, or what it decided last time. For simple one-shot tasks that's
fine. For agents that run over time or across sessions, you need to build memory explicitly.

---

## Four types of memory

| Type | What it stores | Where it lives | Analogy |
|---|---|---|---|
| **In-context** | Current conversation | The prompt | Working memory |
| **Episodic** | Past conversations / runs | Database | Diary |
| **Semantic** | Facts and knowledge | Vector DB | Long-term memory |
| **Procedural** | How to do things | System prompt / tools | Muscle memory |

Most real systems combine two or three of these.

---

## In-context memory (simplest)

Just keep appending to the messages list. The model "remembers" everything in the current
context window — but it's gone when the process ends.

```python
messages = [{"role": "system", "content": "You are a research assistant."}]

def chat(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply

chat("What's the capital of France?")   # Paris
chat("And what's its population?")      # Remembers we're talking about Paris
```

**Limit:** context windows have token limits. For long conversations, summarise older messages
or use a sliding window — keep the last N turns, drop the rest.

---

## Episodic memory (cross-session)

Persist past runs to a database so the agent can refer back to what it did before.
Simple version: write summaries to a file or database, load them at the start of each session.

```python
import json
from pathlib import Path

MEMORY_FILE = Path("agent_memory.json")

def load_memory() -> list[dict]:
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []

def save_memory(entry: dict):
    memory = load_memory()
    memory.append(entry)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

# At the start of a run: load past episodes into the system prompt
past = load_memory()
summary = "\n".join(f"- {e['date']}: {e['summary']}" for e in past[-5:])

system = f"""You are a research assistant.

Previous sessions:
{summary}

Use this context to avoid repeating work."""
```

---

## Semantic memory (vector DB)

Store facts as embeddings so the agent can retrieve relevant ones at query time.
This is RAG applied to agent memory — see the [Vector Databases & RAG](rag-vector-databases.md) page for the full pattern.

```python
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.PersistentClient(path="./agent_memory_db")
memory = chroma.get_or_create_collection("agent_memory")

def remember(fact: str, metadata: dict = {}):
    embedding = client.embeddings.create(
        model="text-embedding-3-small", input=fact
    ).data[0].embedding
    memory.add(
        documents=[fact],
        embeddings=[embedding],
        ids=[str(hash(fact))],
        metadatas=[metadata]
    )

def recall(query: str, top_k: int = 3) -> list[str]:
    embedding = client.embeddings.create(
        model="text-embedding-3-small", input=query
    ).data[0].embedding
    results = memory.query(query_embeddings=[embedding], n_results=top_k)
    return results["documents"][0]

# Agent learns something
remember("The client prefers bullet-point summaries over prose.", {"type": "preference"})
remember("Q3 report analysis was completed on 2026-05-01.", {"type": "task_log"})

# Agent recalls relevant context before a new task
context = recall("format preferences for client reports")
```

---

## Memory in LangGraph

LangGraph has built-in memory via checkpointers — the graph state is persisted between runs
so the agent picks up exactly where it left off.

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# Persist state to a local SQLite file
checkpointer = SqliteSaver.from_conn_string("agent_checkpoints.db")
app = graph.compile(checkpointer=checkpointer)

# Each thread_id is a separate conversation / agent run
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [...]}, config=config)

# Next time you call with the same thread_id, the agent remembers everything
result2 = app.invoke({"messages": [new_message]}, config=config)
```

---

## Memory in CrewAI

CrewAI has memory built in — enable it with one flag:

```python
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    memory=True,          # enables short-term + long-term memory
    verbose=True
)
```

- **Short-term memory** — shared context within a single crew run
- **Long-term memory** — persisted across runs (stored locally via embeddings)
- **Entity memory** — tracks specific people, places, organisations mentioned

---

## Summarisation — keeping context manageable

As conversations get long, older content pushes out newer content (or hits token limits).
Fix: periodically summarise older messages and replace them with the summary.

```python
def summarise_history(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarise this conversation history concisely."},
            {"role": "user", "content": str(messages)}
        ]
    )
    return response.choices[0].message.content

# When messages exceed a threshold, compress the oldest N turns
if len(messages) > 20:
    old = messages[1:11]   # keep system prompt at [0]
    summary = summarise_history(old)
    messages = [messages[0], {"role": "system", "content": f"Earlier context: {summary}"}] + messages[11:]
```

---

## Gotchas

- **Don't store everything** — noisy memory makes retrieval worse; store summaries, not raw transcripts
- **Memory poisoning** — if the agent stores wrong facts, it will confidently repeat them; add a review step for important memories
- **Thread IDs matter in LangGraph** — a missing or wrong thread_id starts a fresh conversation with no history
- **CrewAI memory uses embeddings** — it calls an embedding model in the background; make sure your API key covers it

---

## Resources

- [LangGraph persistence docs](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [CrewAI memory docs](https://docs.crewai.com/concepts/memory)
- [DeepLearning.AI — Long-Term Agentic Memory With LangGraph](https://www.deeplearning.ai/courses/long-term-agentic-memory-with-langgraph/)
- [DeepLearning.AI — Agent Memory: Building Memory-Aware Agents](https://www.deeplearning.ai/courses/agent-memory-building-memory-aware-agents/)

---

[Back to index](index.md)
