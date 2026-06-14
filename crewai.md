---
layout: page
title: CrewAI
---

## What it is

High-level multi-agent framework. You define agents as team members with a role, goal, and backstory,
assign them tasks, and a Crew orchestrates the execution. Good for getting multi-agent pipelines
running quickly without wiring up all the plumbing yourself.

---

## Core pattern

```python
from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(model="gpt-4o-mini", temperature=0.1)

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate information on the given topic.",
    backstory="You are a meticulous analyst who only cites verified sources.",
    llm=llm
)

writer = Agent(
    role="Technical Writer",
    goal="Turn research into a clear, concise summary.",
    backstory="You write for senior engineers who value brevity.",
    llm=llm
)

research_task = Task(
    description="Research the current state of LangGraph vs CrewAI for agentic pipelines.",
    expected_output="A bullet-point summary of key differences.",
    agent=researcher
)

write_task = Task(
    description="Using the research, write a one-page comparison for a Python developer.",
    expected_output="A clear, structured comparison document.",
    agent=writer
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

result = crew.kickoff()
print(result.raw)
```

---

## Key concepts

- `Agent` — the worker. Role + goal + backstory shapes how it behaves
- `Task` — a unit of work with a description and expected output format
- `Crew` — holds agents and tasks; `kickoff()` runs the pipeline
- `Process.sequential` — tasks run in order, each gets the previous output as context
- `Process.hierarchical` — adds a manager agent that delegates and reviews

---

## LLM wiring

```python
# Personal machine (OpenAI key)
llm = LLM(model="gpt-4o-mini")

# Work (Azure OpenAI + managed identity — no API key needed)
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
llm = LLM(
    model="azure/your-deployment-name",
    api_base="https://your-company.openai.azure.com/",
    api_version="2024-08-01-preview",
    azure_ad_token_provider=token_provider
)
```

- Use `LLM(model="...")` from `crewai` — wraps LiteLLM
- Do **not** pass LangChain objects (`ChatOpenAI`, `ChatGoogleGenerativeAI`) — newer CrewAI rejects them

---

## Gotchas

- `max_iter` defaults to 25 — causes very long runs; set `max_iter=5` on extraction agents
- Don't use CrewAI for PDF→JSON extraction — use the OpenAI SDK directly with `response_format=json_object`
- `output_file` on a Task writes raw LLM output including markdown fences — strip them manually if parsing JSON
- Older tutorials use LangChain wiring — check any example is using `crewai.LLM` before following it

---

## Resources

- [Official examples repo](https://github.com/crewAIInc/crewAI-examples) — trip planner, research agent, stock analysis
- [Official docs](https://docs.crewai.com) — quickstart and core concepts are well written
- [DeepLearning.AI — Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — free short course built with the CrewAI team; the best structured starting point

---

## From your code

**Insight — LLM Initialization with Custom Model**

The LLM is initialized with a custom model 'gpt-4o-mini' and a specific temperature of 0.1, which impacts the randomness of the model's outputs. This specificity helps in understanding the precision or variability needed by the application.

**Insight — Agent Role Definition**

The code defines an agent 'triage_analyst' with a very specific role and backstory, which could influence the contextual understanding of the tasks. This suggests the importance of detailed role descriptions for agents to align with the domain-specific tasks they perform.

**Insight — Understanding of Task Dependencies**

In the `execute_classification_pipeline` method, the task description includes multi-step instructions for tag assignment and referenced IDs extraction, illustrating how Agent tasks can handle complex pipelines and decision-making based on multiple conditions.

---

[Back to index](index.md)
