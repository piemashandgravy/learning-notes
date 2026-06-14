---
layout: page
title: Evaluation & Testing
---

## Why this is hard

Testing agents isn't like testing normal software. You can't just assert `output == expected`
because LLM outputs vary, tasks are open-ended, and the thing you're evaluating is often
judgement — which is hard to encode as a unit test.

The field's answer: use an LLM to judge LLM outputs. And build evals that run automatically
so you know when something regresses.

---

## The three levels

**Level 1 — Deterministic checks**
Things you can assert exactly. Start here — these are fast and free.

```python
import json

def test_output_is_valid_json(raw_output: str):
    try:
        data = json.loads(raw_output)
        assert isinstance(data, list), "Expected a list"
        assert all("ID" in item for item in data), "Every item must have an ID"
    except json.JSONDecodeError:
        raise AssertionError(f"Output is not valid JSON: {raw_output[:200]}")
```

**Level 2 — Heuristic checks**
Rules that don't need an LLM — length, keyword presence, format, range checks.

```python
def test_classification_output(result: dict):
    assert len(result["categories"]) >= 1, "Must have at least one category"
    assert len(result["reasoning"]) <= 200, "Reasoning too long"
    valid_categories = {"CODE_REFACTOR", "DATA_CLEANUP", "SNOWFLAKE", "NON_CODING_TASK"}
    unknown = set(result["categories"]) - valid_categories
    assert not unknown, f"Unknown categories: {unknown}"
```

**Level 3 — LLM-as-judge**
Use a model to evaluate whether the output is good. Slow and costs tokens, but the only
option for open-ended outputs like summaries, reasoning, or plans.

```python
def llm_judge(task: str, output: str, criteria: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",   # use a stronger model to judge a weaker one
        messages=[{
            "role": "user",
            "content": f"""Evaluate this AI output.

Task: {task}
Output: {output}
Criteria: {criteria}

Rate 1-5 and explain briefly.
Return JSON: {{"score": int, "reasoning": str, "passed": bool}}"""
        }],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

result = llm_judge(
    task="Classify this backlog item as CODE_REFACTOR or DATA_CLEANUP",
    output='{"category": "CODE_REFACTOR", "reasoning": "Involves rewriting pandas functions"}',
    criteria="Category must match the task description. Reasoning must reference specific evidence."
)
# {"score": 5, "reasoning": "Category is correct and reasoning cites the task detail", "passed": true}
```

---

## Building a test suite

The goal: a script you can run after any change to catch regressions.

```python
import json
from pathlib import Path

# Golden dataset — inputs with known-good expected outputs
TEST_CASES = [
    {
        "input": "Optimise Python loops for Snowflake migration",
        "expected_categories": ["CODE_REFACTOR", "SNOWFLAKE"],
        "must_not_contain": ["DATA_CLEANUP"]
    },
    {
        "input": "Delete duplicate tick rows via SQL script",
        "expected_categories": ["DATA_CLEANUP", "SNOWFLAKE"],
        "must_not_contain": ["CODE_REFACTOR"]
    }
]

def run_eval_suite(agent_fn):
    results = []
    for case in TEST_CASES:
        output = agent_fn(case["input"])
        categories = output.get("categories", [])

        passed = (
            all(c in categories for c in case["expected_categories"])
            and not any(c in categories for c in case["must_not_contain"])
        )
        results.append({"input": case["input"], "passed": passed, "output": output})

    passed = sum(r["passed"] for r in results)
    print(f"{passed}/{len(results)} tests passed")
    return results
```

---

## Tracing — seeing what agents actually do

Eval catches *what* went wrong. Tracing shows *where* in the pipeline it went wrong.

**LangSmith** (from LangChain team)
Works automatically with LangGraph — set two env vars and every run is logged.

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
# Now every LangGraph run appears in the LangSmith dashboard
```

**Langfuse** (open source alternative)
Works with any framework via a simple decorator or wrapper.

```python
from langfuse.decorators import observe

@observe()
def run_agent(task: str) -> str:
    # Your agent code here
    # Every call is automatically traced in Langfuse
    ...
```

Both tools show you: which node ran, what prompt was sent, what came back, token counts, latency.
Essential once your pipeline has more than 2-3 steps.

---

## A practical eval workflow

1. **Build a golden dataset** — 10-20 representative inputs with expected outputs; grow it over time
2. **Write deterministic checks first** — format, schema, required fields
3. **Add LLM-as-judge for subjective quality** — only where deterministic checks can't reach
4. **Run evals before and after changes** — treat regressions as bugs
5. **Add tracing** — so when an eval fails you can see exactly which step broke

---

## Gotchas

- **Don't evaluate on your training examples** — if you tuned prompts on 5 examples, test on different ones
- **LLM judges have biases** — they favour longer outputs, prefer their own style; calibrate by checking judge scores against human scores on a small set
- **GPT-4o-mini as judge is unreliable** — use `gpt-4o` or stronger to evaluate outputs from weaker models
- **Flaky evals are worse than no evals** — if your eval randomly passes/fails, you'll ignore it; make deterministic checks robust first

---

## Resources

- [LangSmith docs](https://docs.smith.langchain.com)
- [Langfuse docs](https://langfuse.com/docs)
- [DeepLearning.AI — Evaluating AI Agents](https://www.deeplearning.ai/courses/evaluating-ai-agents/)
- [DeepLearning.AI — Automated Testing for LLMOps](https://www.deeplearning.ai/courses/automated-testing-llmops/)

---

## From your code

**Insight — Post-Processing LLM Output**

The `parse_result` function deals with potential markdown style formatting in LLM outputs, stripping it out before processing. This demonstrates a common practical necessity for handling formatted text returned from LLMs before parsing them as JSON.

---

[Back to index](index.md)
