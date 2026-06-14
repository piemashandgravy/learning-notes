---
layout: page
title: OpenAI SDK
---

## What it is

Direct Python access to OpenAI's API (and any OpenAI-compatible endpoint, including Azure OpenAI).
No orchestration framework — just you and the model. Start here before adding frameworks on top.

---

## Core pattern

```python
from openai import OpenAI

client = OpenAI()  # picks up OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain what a vector database is."}
    ]
)

print(response.choices[0].message.content)
```

---

## Tool calling (function calling)

How you give a model access to external functions. The model decides when to call them.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current price of a stock by ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "e.g. AAPL"}
                },
                "required": ["ticker"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What's Apple's stock price?"}],
    tools=tools
)
# If the model wants to call the tool, response.choices[0].message.tool_calls is populated
# You execute the function yourself, then send the result back in a follow-up message
```

---

## Structured outputs

Force the model to return valid JSON matching a schema — useful for extraction pipelines.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Extract: John Smith, age 34, London"}],
    response_format={"type": "json_object"}
)
# Or use response_format with a Pydantic schema for full type safety (gpt-4o and above)
```

---

## Azure OpenAI (work setup)

```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint="https://your-company.openai.azure.com/",
    azure_ad_token_provider=token_provider,
    api_version="2024-08-01-preview"
)
# No API key — DefaultAzureCredential handles auth via Azure CLI / managed identity
```

---

## When to use

- Simple single-turn completions
- Extraction tasks (structured outputs)
- When you want full control without a framework
- Building blocks before adding CrewAI or LangGraph on top

## When to move up the stack

- You need multiple agents collaborating → **CrewAI**
- You need loops, branching, complex state → **LangGraph**
- You want to expose your own tools to the model cleanly → **MCP**

---

## Resources

- [OpenAI Python SDK — GitHub](https://github.com/openai/openai-python)
- [OpenAI API reference](https://platform.openai.com/docs/api-reference)
- [Azure OpenAI quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart)

---

[Back to index](index.md)
