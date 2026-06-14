---
layout: page
title: Vector Databases & RAG
---

## The problem RAG solves

LLMs only know what's in their training data and what you put in their context window.
If you want an agent to reason over your own documents — internal reports, codebases,
knowledge bases, PDFs — you have two options:

1. **Stuff everything into the prompt** — expensive, hits context limits, slow
2. **Retrieve only what's relevant** — this is RAG

**RAG (Retrieval-Augmented Generation)** means: before calling the LLM, fetch the most
relevant chunks of your data and include them in the prompt. The model reasons over
fresh, specific context rather than stale training data.

---

## How it works

```
INGEST (once)                          QUERY (every request)
──────────────────────────────         ────────────────────────────────────
                                
 Your documents                         User question
      ↓                                      ↓
 Split into chunks                      Embed the question
      ↓                                      ↓
 Embed each chunk                       Search vector DB for nearest chunks
      ↓                                      ↓
 Store in vector DB                     Add chunks to prompt → call LLM
```

**Embedding** turns text into a list of numbers (a vector) that captures semantic meaning.
Chunks that mean similar things end up close together in vector space.
The search step finds chunks whose vectors are closest to the query vector.

---

## Key concepts

**Chunking** — splitting documents into pieces before embedding.
Too large: you retrieve irrelevant content along with the useful bit.
Too small: you lose context. Typical chunk size: 500–1000 tokens with ~100 token overlap.

**Embedding model** — the model that converts text to vectors. Separate from your LLM.
Common choices:
- `text-embedding-3-small` (OpenAI) — cheap, hosted, good quality
- `all-MiniLM-L6-v2` (HuggingFace) — free, runs locally, fast, slightly lower quality

**Similarity search** — finding the closest vectors to a query vector.
Usually cosine similarity or dot product. You ask for top-k results (e.g. top 5 chunks).

**Vector database** — stores embeddings and lets you search them at scale.

---

## Vector databases — which to use

| DB | Best for | Runs |
|---|---|---|
| **Chroma** | Learning, local dev, prototyping | Local or hosted |
| **FAISS** | Pure similarity search, no server needed | Local (in-memory or file) |
| **Qdrant** | Production, open source, good performance | Local or hosted |
| **Pinecone** | Managed production, simplest API | Hosted only |
| **Weaviate** | Feature-rich, built-in embedding support | Local or hosted |

Start with **Chroma** — zero infrastructure, runs in a folder on disk, easy to swap out later.

---

## Minimal RAG pipeline with Chroma

```python
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("my_docs")

# ── INGEST ──────────────────────────────────────────────────────────────────

def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

documents = [
    "The quarterly report shows revenue up 12% year on year.",
    "Our main risk factor is currency exposure in EUR/GBP.",
    "The board approved a share buyback of £50m in March.",
]

collection.add(
    documents=documents,
    embeddings=[embed(d) for d in documents],
    ids=[f"doc_{i}" for i in range(len(documents))]
)

# ── QUERY ────────────────────────────────────────────────────────────────────

def rag_query(question: str, top_k: int = 2) -> str:
    results = collection.query(
        query_embeddings=[embed(question)],
        n_results=top_k
    )
    context = "\n".join(results["documents"][0])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer using only this context:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

print(rag_query("What did the board approve in March?"))
```

---

## Using HuggingFace embeddings (free, local)

```python
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("my_docs")

# Same pattern — just swap the embed function
def embed(text: str) -> list[float]:
    return model.encode(text).tolist()
```

No API key, no cost, runs entirely on your machine.

---

## RAG as an agent tool (CrewAI)

```python
from crewai_tools import RagTool

rag_tool = RagTool(config={
    "llm": {"provider": "openai", "config": {"model": "gpt-4o-mini"}},
    "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
    "vectordb": {"provider": "chroma", "config": {"collection_name": "my_docs"}}
})

analyst = Agent(
    role="Research Analyst",
    goal="Answer questions using internal documents.",
    backstory="You only cite information from the provided knowledge base.",
    tools=[rag_tool],
    llm=llm
)
```

---

## RAG in LangGraph

In LangGraph you add a retrieval node — a plain Python function that queries your vector DB
and injects the results into the state before the LLM node runs.

```python
def retrieve(state: State) -> State:
    results = collection.query(
        query_embeddings=[embed(state["question"])],
        n_results=3
    )
    context = "\n".join(results["documents"][0])
    return {"context": context}

def generate(state: State) -> State:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Context:\n{state['context']}"},
            {"role": "user", "content": state["question"]}
        ]
    )
    return {"answer": response.choices[0].message.content}

graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_edge("retrieve", "generate")
```

---

## Gotchas

- **Chunk overlap matters** — without it, a relevant sentence split across two chunks gets missed
- **Embedding model consistency** — you must embed queries with the same model used to embed documents
- **Chroma persistence** — use `PersistentClient(path="...")` or your data vanishes when the process ends
- **Top-k isn't always enough** — if your chunks are noisy, add a re-ranking step to filter before the LLM call
- **Don't embed too-short chunks** — single sentences lose context; aim for paragraph-level minimum

---

## Resources

- [Chroma docs](https://docs.trychroma.com)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [Qdrant quickstart](https://qdrant.tech/documentation/quick-start/)
- [Pinecone docs](https://docs.pinecone.io)
- [DeepLearning.AI — Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/courses/building-agentic-rag-with-llamaindex/)
- [DeepLearning.AI — Event-Driven Agentic Document Workflows](https://www.deeplearning.ai/courses/event-driven-agentic-document-workflows/)

---

[Back to index](index.md)
