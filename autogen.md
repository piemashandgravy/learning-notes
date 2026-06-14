---
layout: page
title: AutoGen
---

## What it is

Microsoft's multi-agent framework — built around the idea of **conversational agents**
that talk to each other to solve problems. Where CrewAI uses roles and tasks and LangGraph
uses graphs and state, AutoGen frames everything as a structured conversation between agents.

The key abstraction: every agent is a participant in a chat. Agents take turns sending
messages, and the conversation continues until a termination condition is met.

```bash
pip install pyautogen
```

---

## Core pattern — two-agent conversation

The simplest and most common setup: an `AssistantAgent` (LLM-powered) and a
`UserProxyAgent` (represents the human and can execute code).

```python
import autogen

config_list = [{"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}]
llm_config = {"config_list": config_list}

assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config=llm_config,
    system_message="You are a helpful AI assistant. Solve tasks step by step."
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",     # fully automated; "ALWAYS" to prompt for input each turn
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

user_proxy.initiate_chat(
    assistant,
    message="Write a Python function that checks if a number is prime, then test it."
)
```

The assistant writes code, the user proxy executes it, the result goes back to the
assistant, and the conversation continues until the task is done.

**`human_input_mode` options:**
- `"NEVER"` — fully automated, no prompts
- `"TERMINATE"` — only prompts when the conversation is about to end
- `"ALWAYS"` — prompts you every turn (useful for debugging)

---

## Code execution

`UserProxyAgent` can execute Python and shell code blocks that the assistant writes.
This is built-in — no extra wiring needed.

```python
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "coding",       # where code files are saved
        "use_docker": False,        # True for isolated execution (recommended for production)
        "timeout": 60               # max seconds per execution
    },
    is_termination_msg=lambda msg: "TASK COMPLETE" in msg.get("content", "")
)
```

The conversation loop:
1. Assistant produces a message with a ```python code block
2. `UserProxyAgent` extracts and runs it
3. Output goes back to the assistant as the next message
4. Assistant decides: done, or write more code

**In production:** use `use_docker=True` to run code in an isolated container.
Without Docker, arbitrary code runs in your process.

---

## Termination conditions

Conversations need a stopping condition — otherwise they loop forever.

```python
# Option 1: keyword in message
is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "")

# Option 2: max turns
user_proxy = autogen.UserProxyAgent(
    name="User",
    max_consecutive_auto_reply=5   # stops after 5 auto-replies
)

# Option 3: no more code to execute
# UserProxyAgent stops when it receives a message with no code block
# (default behaviour when human_input_mode="NEVER")
```

Tell the assistant to say "TERMINATE" when done — put it in the system message:
`"When the task is complete, end your message with TERMINATE."`

---

## GroupChat — multi-agent conversations

For more than two agents, `GroupChat` manages who speaks next.

```python
researcher = autogen.AssistantAgent(
    name="Researcher",
    llm_config=llm_config,
    system_message="You find and summarise relevant information."
)

writer = autogen.AssistantAgent(
    name="Writer",
    llm_config=llm_config,
    system_message="You turn research notes into clear, readable prose."
)

critic = autogen.AssistantAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="You review drafts and suggest specific improvements."
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False   # no code execution needed here
)

group_chat = autogen.GroupChat(
    agents=[user_proxy, researcher, writer, critic],
    messages=[],
    max_round=12,
    speaker_selection_method="auto"  # LLM decides who speaks next
)

manager = autogen.GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

user_proxy.initiate_chat(manager, message="Write a short article about LangGraph.")
```

**Speaker selection methods:**
- `"auto"` — a manager LLM decides who speaks next based on context (most flexible)
- `"round_robin"` — agents take turns in order
- `"random"` — random selection
- A custom function `f(last_speaker, groupchat) -> Agent` for full control

---

## Nested chats

An agent can trigger a separate two-agent conversation as a subtask — the result comes
back as a message in the outer conversation.

```python
# Register a nested chat: when the researcher needs to verify a fact,
# it triggers a separate conversation with a fact-checker
researcher.register_nested_chats(
    [{"recipient": fact_checker, "message": "Please verify: {last_msg}", "max_turns": 3}],
    trigger=lambda sender: sender.name == "Writer"  # only when Writer sends to Researcher
)
```

Useful for: encapsulating complex subtasks, running quality checks without polluting
the main conversation thread, or calling a specialist that the other agents don't need to see.

---

## Vs other frameworks

| | AutoGen | CrewAI | LangGraph |
|---|---|---|---|
| Core abstraction | Conversation between agents | Roles, tasks, crew | State graph with nodes and edges |
| Code execution | Built-in, first-class | Via tools | Via tool nodes |
| Control flow | Conversation + termination conditions | Sequential or parallel tasks | Explicit graph edges + routing |
| Multi-agent | GroupChat with speaker selection | Hierarchical or parallel process | Manual subgraph wiring |
| Best for | Tasks that need iterative code generation and execution | Role-based pipelines | Complex stateful workflows |

**AutoGen's distinctive strength** is the code execution loop — it's the natural choice when
the task involves writing, running, and debugging code iteratively. CrewAI and LangGraph
treat code execution as just another tool; AutoGen treats it as the primary interaction mode.

---

## Gotchas

- `human_input_mode="NEVER"` with no termination condition → infinite loop. Always set one.
- Code execution without Docker runs in your process — untrusted or generated code can do damage. Use Docker for anything beyond dev/learning.
- `GroupChat` with `speaker_selection_method="auto"` costs extra tokens per turn — the manager LLM reads the full conversation to pick the next speaker. Budget accordingly.
- Agents in a GroupChat see the full conversation history — long threads get expensive fast. Set `max_round` conservatively.
- AutoGen has had significant API changes between versions (0.2 vs 0.4+). Ed Donner's course uses 0.2-style API (`pyautogen`). The newer `autogen-agentchat` package has a different import structure.

---

## Resources

- [AutoGen docs](https://microsoft.github.io/autogen/)
- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [Ed Donner — Agentic AI course, Week 5](ed-donner.md) — dedicated AutoGen week
- [AutoGen examples](https://github.com/microsoft/autogen/tree/main/samples)

---

[Back to index](index.md)
