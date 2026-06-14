---
layout: page
title: MCP — Model Context Protocol
---

## What it is

An open standard (from Anthropic) for connecting AI models to external tools and data sources.
Think of it as a plug socket: you write an MCP server once, and any MCP-compatible client
(Claude, Cursor, Claude Code, and increasingly other tools) can use it without extra glue code.

You're probably already using MCP without realising — Claude Code uses MCP servers under the hood
to give the model access to tools like file reading, web search, and Google Drive.

---

## The model

```
┌─────────────────┐        MCP protocol        ┌─────────────────┐
│   MCP Client    │ ◄─────────────────────────► │   MCP Server    │
│  (Claude, app)  │                             │  (your tools)   │
└─────────────────┘                             └─────────────────┘
```

- **Server** — exposes tools, resources, and prompts over a standard interface
- **Client** — the LLM host (e.g. Claude Desktop, your Python app); calls the server
- **Tool** — a function the model can invoke (like `search_database`, `read_file`)
- **Resource** — a data source the model can read (like a file, a URL, a DB table)
- **Prompt** — a reusable prompt template the server exposes

---

## Simple MCP server in Python

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Tools")

@mcp.tool()
def get_word_count(text: str) -> int:
    """Count the number of words in a text string."""
    return len(text.split())

@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

if __name__ == "__main__":
    mcp.run()
```

That's a valid MCP server. Any MCP client can now discover and call `get_word_count` and `reverse_string`.

---

## Connecting a server to Claude Desktop

In `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or equivalent:

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["/path/to/your/server.py"]
    }
  }
}
```

Restart Claude Desktop — your tools appear automatically in the conversation.

---

## MCP vs tool calling

Both let an LLM call external functions. The difference:

| | OpenAI tool calling | MCP |
|---|---|---|
| Scope | One app, one model | Any client, any model |
| Portability | Write per-app | Write once, use anywhere |
| Discovery | You define the schema in code | Server advertises its own tools |
| Best for | Tight integration in one app | Reusable tools across many clients |

---

## Key concepts to understand next

- **Transports** — how client and server communicate (stdio for local, HTTP/SSE for remote)
- **Sampling** — server can ask the client to run an LLM call (advanced)
- **Resources vs Tools** — tools are called on demand; resources are like readable files/URIs

---

## Resources

- [MCP official docs](https://modelcontextprotocol.io) — spec, quickstart, Python SDK
- [MCP Python SDK — GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [MCP servers registry](https://github.com/modelcontextprotocol/servers) — pre-built servers for common tools (GitHub, Slack, Postgres, Google Drive, etc.)
- [DeepLearning.AI — MCP: Build Rich-Context AI Apps](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/) — free short course from Anthropic

---

[Back to index](index.md)
