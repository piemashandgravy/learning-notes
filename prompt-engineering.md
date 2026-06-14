---
layout: page
title: Prompt Engineering
---

## What it is

The craft of writing instructions that reliably get the behaviour you want from an LLM.
In agentic work this matters more than in chat — agents run unsupervised, so a vague prompt
produces vague (or wrong) results at every step of the pipeline.

---

## System prompts

The system prompt sets the agent's identity, constraints, and output format.
Most of the work happens here, not in the user message.

**Weak system prompt**
```
You are a helpful assistant. Answer the user's question.
```

**Strong system prompt**
```
You are a financial data analyst. Your job is to extract structured information
from bank statement descriptions.

Rules:
- Only output valid JSON. Never include explanation or markdown.
- If a field cannot be determined, use null — never guess.
- Merchant names must be title case.
- Amounts are always positive floats.

Output schema:
{"merchant": string, "category": string, "amount": float, "currency": string}
```

The difference: the strong version constrains format, handles edge cases, and removes ambiguity.

---

## Few-shot prompting

Show the model examples of correct input/output pairs before the real task.
Dramatically improves consistency, especially for classification and extraction.

```python
system = """You classify bank transactions into categories.

Examples:
Input: "AMAZON.CO.UK PRIME"   → {"category": "Subscriptions"}
Input: "TESCO STORES 3247"    → {"category": "Groceries"}
Input: "NETFLIX.COM"          → {"category": "Subscriptions"}
Input: "SHELL OIL 00345"      → {"category": "Transport"}

Only output JSON. No explanation."""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": "DELIVEROO IRELAND"}
    ]
)
```

---

## Chain-of-thought (CoT)

Tell the model to reason step by step before giving a final answer.
Significantly improves accuracy on anything involving logic or multi-step reasoning.

```python
# Without CoT — model jumps straight to an answer, more likely to be wrong
"Is this transaction a duplicate? Transaction A: £45.00 SPOTIFY 01/03. Transaction B: £45.00 SPOTIFY 01/03"

# With CoT — model works through it
"Is this transaction a duplicate? Think step by step:
1. Compare the merchant names
2. Compare the amounts
3. Compare the dates
4. State your conclusion"
```

For extraction/classification tasks you usually *don't* want CoT — it adds tokens and
the model tends to second-guess itself. Use it for reasoning-heavy tasks.

---

## Structured output prompting

When you need JSON back, be explicit in three places: the system prompt, the format
description, and the enforcement mechanism.

```python
from pydantic import BaseModel

class Transaction(BaseModel):
    merchant: str
    category: str
    amount: float

# Pydantic + OpenAI's .parse() enforces the schema at the API level
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extract transaction data. Be precise."},
        {"role": "user", "content": "DELIVEROO IRELAND £23.50"}
    ],
    response_format=Transaction
)
result = response.choices[0].message.parsed  # typed Transaction object
```

---

## Agent-specific patterns

**Role + goal + constraint** — the three parts of a good agent prompt:
```
Role:       You are a senior equity research analyst.
Goal:       Identify the three most material risks in the provided report.
Constraint: Cite the exact paragraph. Output as JSON array. Max 50 words per risk.
```

**Negative instructions** — tell the model what *not* to do:
```
Do not summarise the whole document.
Do not include risks already flagged in previous reports.
Do not use phrases like "it is important to note".
```

**Output anchoring** — start the assistant's response for it:
```python
messages=[
    {"role": "system", "content": "Extract the company name from the text."},
    {"role": "user", "content": "The filing was submitted by Barclays PLC on..."},
    {"role": "assistant", "content": '{"company":'}  # model completes this
]
```

---

## Gotchas

- **Longer ≠ better** — a focused 5-line system prompt often outperforms a 50-line one
- **Ambiguity compounds** — in a multi-step pipeline, a vague prompt at step 1 creates garbage by step 4
- **Test with adversarial inputs** — what happens if the model sees an empty input, a foreign language, or unexpected formatting?
- **Temperature matters** — use `temperature=0` for extraction/classification; higher (0.7+) for creative tasks
- **Model-specific behaviour** — prompts tuned for GPT-4o don't always transfer cleanly to GPT-4o-mini or Claude

---

## Resources

- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic prompt engineering docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [DeepLearning.AI — ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/courses/chatgpt-prompt-eng/)

---

[Back to index](index.md)
