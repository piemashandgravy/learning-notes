---
layout: page
title: Cost & Model Selection
---

LLM costs can surprise you. A pipeline that costs pennies per run in dev can cost pounds
per run in production if you chose the wrong model or let an agent loop unchecked.
Getting model selection right early saves money and makes iteration faster.

---

## Pricing at a glance

Prices per 1 million tokens (as of mid-2026 — check [openai.com/pricing](https://openai.com/pricing) for current rates):

| Model | Input | Output | Best for |
|---|---|---|---|
| **gpt-4o** | $2.50 | $10.00 | Complex reasoning, difficult tool use, final outputs |
| **gpt-4o-mini** | $0.15 | $0.60 | Classification, routing, structured extraction, most tasks |
| **gpt-4.1** | $2.00 | $8.00 | Long context, instruction following |
| **gpt-4.1-mini** | $0.40 | $1.60 | Mid-tier tasks needing longer context |
| **gpt-4.1-nano** | $0.10 | $0.40 | Cheapest OpenAI option — simple tasks only |
| **o3-mini** | $1.10 | $4.40 | Multi-step reasoning, maths, code — cheaper than o1 |
| **o1** | $15.00 | $60.00 | Hardest reasoning tasks — expensive, use sparingly |
| **claude-sonnet-4** | ~$3.00 | ~$15.00 | Strong alternative to gpt-4o for complex tasks |
| **claude-haiku-4** | ~$0.80 | ~$4.00 | Fast, cheap alternative to gpt-4o-mini |

**Key ratio to remember:** gpt-4o-mini is ~17x cheaper than gpt-4o on input tokens.
Most tasks don't need gpt-4o.

**Output tokens cost more than input tokens** — a model that is verbose costs more.
Prompt it to be concise when output length doesn't matter.

---

## Token counting — what costs what

A rough guide:
- 1 token ≈ 4 characters of English text
- 1 token ≈ ¾ of a word
- 1,000 words ≈ 1,300 tokens
- A typical system prompt: 200–500 tokens
- A tool schema (one tool): 50–150 tokens
- A page of text: ~500 tokens
- A short code file: ~300–800 tokens

**In an agent loop**, tokens accumulate fast. Each turn the model sees:
- System prompt (repeated every turn)
- Full conversation history so far
- All tool schemas (repeated every turn)
- The latest tool results

A 10-turn agent conversation with a 500-token system prompt and 3 tool schemas might
easily consume 15,000–30,000 tokens — most of it in the repeated context, not the actual answers.

**Estimate before you build:**

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o-mini")

system_prompt = "You are a helpful assistant..."
tokens = len(enc.encode(system_prompt))
print(f"System prompt: {tokens} tokens")

# Rough cost for 1000 runs
cost_per_run = (tokens / 1_000_000) * 0.15  # gpt-4o-mini input price
print(f"System prompt cost × 1000 runs: ${cost_per_run * 1000:.4f}")
```

---

## Model selection by task

### Use gpt-4o-mini (or equivalent cheap model) for:
- Classification and routing decisions
- Structured data extraction (JSON from text)
- Summarisation
- Simple question answering
- Guardrail checks
- Any task where you're iterating quickly in development

### Use gpt-4o (or equivalent capable model) for:
- Complex multi-step reasoning
- Tasks where output quality directly affects the end product
- Difficult tool use (model needs to chain several tools correctly)
- Code generation that needs to be correct first time
- Final synthesis after multiple cheaper agents have gathered information

### Use reasoning models (o3-mini, o1) for:
- Mathematical or logical problems
- Code that needs to be provably correct
- Tasks where the model needs to plan deeply before acting
- Generally: when you'd tell a human "think carefully before answering"
- **Avoid** for simple tasks — they're slow and expensive, and over-think easy problems

### Use local models (Ollama, HuggingFace) for:
- Development and testing where accuracy doesn't matter yet
- Privacy-sensitive data that can't leave your machine
- High-volume low-stakes tasks where API costs add up
- When you need to run offline

---

## The layered model strategy

The strongest pipelines use different models for different roles:

```
Cheap model (gpt-4o-mini)
├── Routing / triage
├── Domain validation (guardrails)
├── Structured extraction
└── Summarising tool results

Capable model (gpt-4o)
├── Final synthesis
├── Complex reasoning steps
└── Outputs the user sees directly
```

```python
from crewai import Agent, LLM

cheap_llm = LLM(model="gpt-4o-mini")
capable_llm = LLM(model="gpt-4o")

router = Agent(
    role="Triage",
    goal="Route the request to the right specialist.",
    llm=cheap_llm    # routing is a classification task — doesn't need gpt-4o
)

synthesiser = Agent(
    role="Report Writer",
    goal="Synthesise findings into a clear executive summary.",
    llm=capable_llm  # final output quality matters
)
```

This is the pattern used in `medical_deep_research` from the
[community contributions](community-contributions.md) — cheap model guards the gate,
capable model does the expensive work only when it's warranted.

---

## Avoiding runaway costs in development

### Set max iterations everywhere

```python
# CrewAI
agent = Agent(..., max_iter=5)          # default is 25 — too high
crew = Crew(..., max_iterations=10)

# LangGraph
graph.compile(recursion_limit=10)       # hard stop on graph recursion

# AutoGen
user_proxy = UserProxyAgent(..., max_consecutive_auto_reply=5)

# OpenAI Agents SDK
result = await Runner.run(agent, input, max_turns=10)
```

A 25-iteration loop with gpt-4o at 2,000 tokens per turn costs ~$1 per run.
At 100 dev runs, that's £80 before you've shipped anything.

### Use a cheap model during development

Switch to gpt-4o-mini (or even a local model) while building and testing.
Only switch to the production model once the logic is right.

```python
import os

# In development, override via environment variable
MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

agent = Agent(name="Assistant", model=MODEL, ...)
```

Then in production: `LLM_MODEL=gpt-4o python run.py`

### Cache repeated calls

If the same prompt with the same input runs multiple times (e.g., during testing),
cache the response rather than paying for it again:

```python
import hashlib, json, os

def cached_llm_call(prompt: str, model: str = "gpt-4o-mini") -> str:
    cache_key = hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
    cache_file = f".cache/{cache_key}.json"

    if os.path.exists(cache_file):
        return json.load(open(cache_file))["response"]

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
    os.makedirs(".cache", exist_ok=True)
    json.dump({"response": result}, open(cache_file, "w"))
    return result
```

### Monitor spend with usage callbacks

```python
# Track token usage across a run
total_tokens = {"input": 0, "output": 0}

def on_llm_end(response):
    usage = response.llm_output.get("token_usage", {})
    total_tokens["input"] += usage.get("prompt_tokens", 0)
    total_tokens["output"] += usage.get("completion_tokens", 0)

# After your run:
cost = (total_tokens["input"] / 1_000_000 * 0.15 +
        total_tokens["output"] / 1_000_000 * 0.60)
print(f"Run cost: ${cost:.4f}  ({total_tokens['input']} in / {total_tokens['output']} out)")
```

---

## Known gotchas

**gpt-4.1-nano fails at tool calling.** Tested in the financial pipeline project —
it cannot reliably use tools. Use gpt-4o-mini as the minimum for any tool-using agent.

**Output tokens are 4× the price of input tokens (gpt-4o).** A model that produces
long verbose answers costs significantly more than one that's concise. Add "be concise"
or "reply in bullet points" to system prompts when verbosity doesn't add value.

**Reasoning models (o1, o3) use "thinking tokens"** that aren't visible in the response
but are billed. A single o1 call can consume 10,000+ thinking tokens on a hard problem.
Check `usage.completion_tokens_details.reasoning_tokens` if you're tracking costs closely.

**Context caching** — OpenAI automatically caches the prefix of long prompts if they're
repeated within a short window. You pay 50% of the normal input price for cached tokens.
Structure your prompts so the static parts (system prompt, tool schemas) come first and
the dynamic parts (user message, conversation history) come last.

---

## Quick reference

| Situation | Model choice |
|---|---|
| Development / testing | gpt-4o-mini or local |
| Routing / triage / classification | gpt-4o-mini |
| Structured extraction | gpt-4o-mini |
| Complex reasoning | gpt-4o or o3-mini |
| Final user-facing output | gpt-4o |
| Maths / logic / code correctness | o3-mini |
| Privacy-sensitive / offline | Ollama + local model |
| High volume, low stakes | gpt-4.1-nano (text only — no tools) |

---

## Resources

- [OpenAI pricing](https://openai.com/pricing)
- [Anthropic pricing](https://www.anthropic.com/pricing)
- [tiktoken](https://github.com/openai/tiktoken) — OpenAI's tokeniser, for counting tokens before you send
- [OpenAI usage dashboard](https://platform.openai.com/usage) — track spend by day/model

---

[Back to index](index.md)
