---
layout: page
title: Tool Design & Structured Outputs
---

Two closely related skills: giving agents tools they can use reliably, and getting
structured data back from LLM calls. Both come down to the same principle — the model
can only work with what you make explicit in the schema.

---

## Tool Design

### What the model actually sees

When you register a tool, the model receives a JSON schema describing it. This schema —
not your Python code — is what the model uses to decide when and how to call the tool.

```json
{
  "type": "function",
  "function": {
    "name": "search_products",
    "description": "Search the product catalogue by keyword. Use this when the user asks about available products, prices, or stock. Do not use for order status queries.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search terms, e.g. 'blue running shoes size 10'"
        },
        "max_results": {
          "type": "integer",
          "description": "Maximum number of results to return. Default 5.",
          "default": 5
        }
      },
      "required": ["query"]
    }
  }
}
```

**The description is the interface.** Write it for the model, not for a human reader.
Tell it *when* to call this tool, not just *what* it does.

---

### Writing good tool descriptions

```python
# Bad — describes what the function does, not when to use it
@function_tool
def get_weather(city: str) -> str:
    """Gets weather data."""
    ...

# Good — tells the model when to reach for it and what it returns
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather conditions for a city.

    Use this when the user asks about weather, temperature, rain, or conditions
    in a specific location. Returns a plain text description of current conditions
    including temperature in Celsius and general conditions (sunny, cloudy, etc.).

    Args:
        city: The city name, e.g. 'London' or 'New York'. Do not include country codes.
    """
    ...
```

**Rules of thumb:**
- Start the description with a verb: "Get", "Search", "Calculate", "Send"
- Include "use this when..." for tools that might overlap with others
- Include "do not use for..." when there's an obvious wrong use case
- Describe the return value format so the model knows what it's getting back
- Write `Args:` entries for every parameter — the model uses them to fill in values correctly

---

### Error handling — raise, don't return

Tools should raise exceptions on failure. The framework catches them, formats the error
as a message, and sends it back to the model — which can then retry, adjust, or explain.

```python
# Bad — silent failure; model sees an empty string and may hallucinate a result
@function_tool
def get_stock_price(ticker: str) -> str:
    try:
        return fetch_price(ticker)
    except Exception:
        return ""

# Good — informative exception; model sees the error and can respond appropriately
@function_tool
def get_stock_price(ticker: str) -> str:
    """Get the current price of a stock.

    Args:
        ticker: Stock ticker symbol, e.g. 'AAPL', 'MSFT'. Must be uppercase.
    """
    if not ticker.isupper():
        raise ValueError(f"Ticker must be uppercase, got '{ticker}'")

    price = fetch_price(ticker)
    if price is None:
        raise ValueError(f"No price data found for ticker '{ticker}'. Check it's a valid symbol.")

    return f"{ticker}: ${price:.2f}"
```

The model receiving `"No price data found for ticker 'APPL'"` can respond with
"I couldn't find a price for APPL — did you mean AAPL?" rather than hallucinating a number.

---

### What to return from a tool

Tools return strings that get injected into the conversation. Keep returns:
- **Concise** — long returns consume tokens on every subsequent turn
- **Informative** — include enough context for the model to act on the result
- **Structured** — JSON or key-value pairs are easier for the model to parse than prose

```python
@function_tool
def search_orders(customer_id: str, status: str = "all") -> str:
    """Search orders for a customer.

    Args:
        customer_id: The customer's ID number.
        status: Filter by status — 'pending', 'shipped', 'delivered', or 'all'.
    """
    orders = db.query(customer_id=customer_id, status=status)

    if not orders:
        return f"No orders found for customer {customer_id} with status '{status}'."

    # Return compact JSON — easier for the model than prose
    return json.dumps([
        {"id": o.id, "status": o.status, "total": o.total, "date": o.date}
        for o in orders[:10]
    ], indent=2)
```

---

### Tools vs subagents

| Use a tool when... | Use a subagent when... |
|---|---|
| The action is a single API call or function | The subtask requires multiple steps or its own reasoning |
| The result is deterministic | The subtask benefits from LLM judgment |
| You need the manager to stay in control | The subtask can be delegated end-to-end |
| Speed matters (tools are faster than LLM calls) | Quality of subtask output matters more than speed |

A search API call → tool. A "research this topic and summarise findings" step → subagent.

---

### Async tools

If a tool makes an I/O call (API, database, filesystem), make it async:

```python
import httpx
from agents import function_tool

@function_tool
async def search_web(query: str, num_results: int = 5) -> str:
    """Search the web for current information on a topic.

    Args:
        query: The search query.
        num_results: Number of results to return (1-10).
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
            json={"q": query, "num": num_results}
        )
    results = response.json().get("organic", [])
    return "\n".join(f"- {r['title']}: {r['link']}" for r in results)
```

---

### Tools in each framework

**OpenAI Agents SDK** — `@function_tool` decorator (schema from type hints + docstring):
```python
from agents import function_tool

@function_tool
def my_tool(param: str) -> str:
    """Description here."""
    ...
```

**LangGraph** — `@tool` decorator, then bind to model:
```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Description here."""
    ...

llm_with_tools = llm.bind_tools([my_tool])
```

**CrewAI** — subclass `BaseTool` or use `@tool` decorator:
```python
from crewai.tools import tool

@tool("My Tool Name")
def my_tool(param: str) -> str:
    """Description here — used as the tool description in CrewAI."""
    ...
```

**Raw OpenAI SDK** — define schema manually, handle tool calls yourself:
```python
tools = [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]
response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
if response.choices[0].message.tool_calls:
    # execute tool, append result, call again
```

---

## Structured Outputs

### Two approaches

**JSON mode** — model returns valid JSON, but you define no schema:
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Extract name and age from: John Smith, 34"}],
    response_format={"type": "json_object"}
)
data = json.loads(response.choices[0].message.content)
# data["name"], data["age"] — but no guarantee of field names or types
```

**Structured outputs with Pydantic** — model is constrained to match your schema exactly:
```python
from pydantic import BaseModel
from openai import OpenAI

class Person(BaseModel):
    name: str
    age: int
    city: str | None = None

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Extract: John Smith, 34, London"}],
    response_format=Person
)
person: Person = response.choices[0].message.parsed
print(person.name, person.age)  # fully typed — no json.loads, no KeyError
```

**Use `.parse()` over JSON mode** whenever you know the schema. JSON mode is for exploratory
extraction where you don't know what fields you'll get back.

---

### Useful Pydantic patterns

**Optional fields with defaults:**
```python
class TaskExtraction(BaseModel):
    title: str
    priority: str = "medium"          # default if not mentioned
    due_date: str | None = None       # None if not found
    tags: list[str] = []              # empty list if none
```

**Enums for constrained values:**
```python
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Task(BaseModel):
    title: str
    priority: Priority    # model can only return one of the four values
```

**Nested models:**
```python
class Address(BaseModel):
    street: str
    city: str
    postcode: str

class Customer(BaseModel):
    name: str
    email: str
    address: Address      # model fills in a nested object

class OrderList(BaseModel):
    customers: list[Customer]   # list of nested objects
    total_count: int
```

**Literal types for yes/no decisions:**
```python
from typing import Literal

class SafetyCheck(BaseModel):
    verdict: Literal["safe", "unsafe", "unclear"]
    reason: str
    confidence: float   # 0.0 to 1.0
```

---

### Validation with Field

Add constraints and descriptions to individual fields:

```python
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    query: str = Field(description="The search terms to use. Be specific.")
    num_results: int = Field(default=5, ge=1, le=20, description="Number of results, 1–20.")
    language: str = Field(default="en", pattern="^[a-z]{2}$", description="ISO 639-1 language code.")
```

Field descriptions become part of the JSON schema the model sees — use them to guide
the model on what values are expected.

---

### Structured outputs in each framework

**OpenAI Agents SDK** — define output type on the agent:
```python
from pydantic import BaseModel
from agents import Agent, Runner

class ResearchSummary(BaseModel):
    key_findings: list[str]
    confidence: float
    sources: list[str]

agent = Agent(
    name="Researcher",
    instructions="Research the topic and return structured findings.",
    output_type=ResearchSummary
)

result = Runner.run_sync(agent, "What are the main benefits of LangGraph?")
summary: ResearchSummary = result.final_output
print(summary.key_findings)
```

**LangGraph** — use `with_structured_output()`:
```python
from pydantic import BaseModel

class RouteDecision(BaseModel):
    next_node: Literal["research", "write", "done"]
    reason: str

structured_llm = llm.with_structured_output(RouteDecision)

def router(state):
    decision = structured_llm.invoke(state["messages"])
    return {"next": decision.next_node}
```

**CrewAI** — set `output_pydantic` on a Task:
```python
from crewai import Task
from pydantic import BaseModel

class Report(BaseModel):
    title: str
    summary: str
    action_items: list[str]

task = Task(
    description="Write a report on the research findings.",
    agent=writer,
    output_pydantic=Report    # crew returns a typed Report object
)
```

---

### Common gotchas

**`.parse()` requires gpt-4o or newer** — older models don't support the structured output
constraint. `json_object` mode works on gpt-3.5-turbo and up but gives no schema guarantees.

**Don't use `response_format` with function/tool calling in the same request** — they conflict.
If you're using tools, the structured output comes from the tool call results, not `response_format`.

**Optional fields need a default** — `field: str | None` without `= None` will still require
the field to be present. Always pair `| None` with `= None`.

**Large nested schemas slow the model down** — a deeply nested Pydantic model with 20+ fields
increases the chance of the model making a mistake. For complex extractions, consider two passes:
extract rough data first, then validate/structure in a second call.

**Pydantic v1 vs v2** — most frameworks now expect Pydantic v2. If you see
`pydantic.error_wrappers.ValidationError` (v1) vs `pydantic_core.InitErrorDetails` (v2),
you may have a version mismatch. Pin `pydantic>=2.0`.

---

[Back to index](index.md)
