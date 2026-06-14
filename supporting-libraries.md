---
layout: page
title: Supporting Libraries
---

These aren't agent frameworks — they're the tools that agent frameworks are built on top of,
and that you'll reach for constantly when building real pipelines.

---

## asyncio

Python's built-in library for writing concurrent code with `async`/`await`.
The key idea: instead of waiting for a slow operation (API call, file read, network request)
to finish before starting the next one, you kick off multiple operations and handle them as
they complete.

**Why it matters for agents**
LLM calls are slow. If you have 5 agents making API calls, doing them sequentially takes 5x longer
than doing them in parallel. asyncio is how you do them in parallel.

```python
import asyncio
import openai

client = openai.AsyncOpenAI()

async def classify(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Classify this: {text}"}]
    )
    return response.choices[0].message.content

async def main():
    texts = ["item one", "item two", "item three"]

    # Run all three LLM calls at the same time instead of one after another
    results = await asyncio.gather(*[classify(t) for t in texts])
    print(results)

asyncio.run(main())
```

**Key things to know**
- `async def` — defines a coroutine (a function that can be paused/resumed)
- `await` — pauses here until the slow thing finishes, but lets other coroutines run meanwhile
- `asyncio.gather()` — runs multiple coroutines in parallel, returns all results
- OpenAI SDK has `AsyncOpenAI` for async use; LangGraph and CrewAI both support async natively

**DeepLearning.AI**
No dedicated course but async patterns come up in the LangGraph course.

---

## Pydantic

Data validation library. You define the shape of your data as a Python class, and Pydantic
enforces it at runtime — raising clear errors if something doesn't match instead of letting
bad data silently cause problems downstream.

**Why it matters for agents**
LLMs return text. Pydantic is how you turn that text into structured, type-safe Python objects —
and how you guarantee an agent's output matches the shape your next step expects.

```python
from pydantic import BaseModel
from openai import OpenAI

class TaskClassification(BaseModel):
    id: str
    categories: list[str]
    referenced_ids: list[str]
    reasoning: str

client = OpenAI()

# OpenAI will guarantee the response matches this schema
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Classify task T-301: optimise Python loops for Snowflake."}],
    response_format=TaskClassification
)

result: TaskClassification = response.choices[0].message.parsed
print(result.categories)  # ['CODE_REFACTOR', 'SNOWFLAKE']
```

**Key things to know**
- `BaseModel` — the base class; subclass it to define your schema
- Fields are just type-annotated class attributes
- OpenAI's `.parse()` method (not `.create()`) returns a typed Pydantic object directly
- LangGraph state can be defined as a Pydantic model instead of TypedDict
- CrewAI uses Pydantic internally for all its own classes

**Where you'll use it**
- Structured outputs from LLMs (extraction, classification)
- Defining the shape of agent inputs/outputs
- Validating data coming in from external APIs

---

## Serper

A cheap, fast API for Google Search results — returns structured JSON rather than raw HTML.
The standard way to give an agent web search capability without building a scraper.

**Why it matters for agents**
Agents frequently need to look things up. Serper is the simplest way to add a search tool —
one API call returns the top Google results as clean JSON your agent can reason over.

```python
import httpx
import os

def google_search(query: str, num_results: int = 5) -> list[dict]:
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
        json={"q": query, "num": num_results}
    )
    return response.json().get("organic", [])

results = google_search("LangGraph vs CrewAI 2025")
for r in results:
    print(r["title"], r["link"])
```

**Using it as a CrewAI tool**

```python
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()  # picks up SERPER_API_KEY from environment

researcher = Agent(
    role="Research Analyst",
    goal="Find up-to-date information on the given topic.",
    backstory="You verify claims with current sources.",
    tools=[search_tool],
    llm=llm
)
```

**Key things to know**
- Sign up at [serper.dev](https://serper.dev) — free tier gives 2,500 searches/month
- `crewai_tools` has a `SerperDevTool` built in, so no manual wiring needed in CrewAI
- LangGraph: wrap the `google_search` function above as a tool node
- Also supports news search, image search, and shopping results via separate endpoints

---

## HuggingFace

The central hub for open-source AI models — tens of thousands of LLMs, embedding models,
image models, and more, plus libraries to run them. The alternative to always calling OpenAI.

**Why it matters for agents**
Two main uses:

1. **Running models locally or cheaply** — swap OpenAI for an open-source LLM (Llama, Mistral, Qwen, etc.)
   when you want to avoid API costs, keep data private, or run offline.
2. **Embedding models** — essential for RAG (retrieval-augmented generation), where you need to
   turn documents into vectors for semantic search.

**Using a HuggingFace model via LiteLLM (works with CrewAI)**

```python
from crewai import LLM

# HuggingFace Inference API — hosted, no local GPU needed
llm = LLM(
    model="huggingface/meta-llama/Llama-3.1-8B-Instruct",
    api_key=os.environ["HUGGINGFACE_API_KEY"]
)
```

**Running a model locally with transformers**

```python
from transformers import pipeline

# Downloads model on first run, cached locally after
generator = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct")
result = generator("Explain what a vector database is in one sentence.")
print(result[0]["generated_text"])
```

**Embedding models (for RAG)**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, good quality
embeddings = model.encode(["document one", "document two", "document three"])
# Returns numpy arrays you can store in a vector DB (Chroma, FAISS, Pinecone, etc.)
```

**Key things to know**
- [huggingface.co/models](https://huggingface.co/models) — browse available models; filter by task
- `transformers` — the core library for loading and running models locally
- `sentence-transformers` — specifically for embedding models; easier API than raw transformers
- `huggingface_hub` — for downloading models and datasets programmatically
- LiteLLM (which CrewAI wraps) supports HuggingFace endpoints directly via `huggingface/model-name`
- Local models need a GPU to run at useful speed; CPU-only works for small models

**DeepLearning.AI**
- [Building Code Agents with Hugging Face smolagents](https://www.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents/) — HuggingFace's own lightweight agent framework

---

## How they fit together

```
asyncio          → run multiple agent/LLM calls in parallel
Pydantic         → validate and type agent inputs and outputs
Serper           → give agents a web search tool
HuggingFace      → swap in open-source models; add embedding/RAG capability
```

A typical production pipeline uses all four: Pydantic to define task schemas,
asyncio to run agents concurrently, Serper so agents can look things up,
and HuggingFace embedding models to retrieve relevant context before each LLM call.

---

[Back to index](index.md)
