"""
code_to_notes.py

Reads a Python file, extracts non-obvious patterns and gotchas,
and appends them to the relevant pages in this learning-notes repo.

Usage:
    python code_to_notes.py path/to/your_script.py

Review changes before committing:
    git diff
"""

import sys
import json
from pathlib import Path
from pydantic import BaseModel
from openai import OpenAI

NOTES_DIR = Path(__file__).parent

PAGE_MAP = {
    "crewai":               NOTES_DIR / "crewai.md",
    "langgraph":            NOTES_DIR / "langgraph.md",
    "openai_sdk":           NOTES_DIR / "openai-sdk.md",
    "mcp":                  NOTES_DIR / "mcp.md",
    "rag":                  NOTES_DIR / "rag-vector-databases.md",
    "prompt_engineering":   NOTES_DIR / "prompt-engineering.md",
    "agent_memory":         NOTES_DIR / "agent-memory.md",
    "evaluation":           NOTES_DIR / "evaluation.md",
    "supporting_libraries": NOTES_DIR / "supporting-libraries.md",
}

SYSTEM_PROMPT = f"""You analyse Python code and extract learning insights worth keeping.

Assign each insight to one of these topics:
{json.dumps(list(PAGE_MAP.keys()), indent=2)}

Extract only things that are genuinely non-obvious — patterns worth reusing,
gotchas that could waste someone's time, or decisions that aren't self-evident from the code.
Skip anything already obvious from the variable names or standard library docs.

Format 'content' as markdown. Use a code block if the insight includes a snippet.
Keep each insight to 1-4 sentences."""


# ── Schema ────────────────────────────────────────────────────────────────────

class Insight(BaseModel):
    topic: str    # must be a key in PAGE_MAP
    type: str     # "gotcha" | "pattern" | "tip"
    heading: str  # short title, e.g. "Always set max_iter on extraction agents"
    content: str  # the note body in markdown

class CodeAnalysis(BaseModel):
    summary: str          # one sentence: what this script does
    insights: list[Insight]


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyse(code: str, filename: str) -> CodeAnalysis:
    client = OpenAI()
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"File: {filename}\n\n```python\n{code}\n```"}
        ],
        response_format=CodeAnalysis
    )
    return response.choices[0].message.parsed


# ── Writing ───────────────────────────────────────────────────────────────────

SECTION_HEADER = "## From your code\n"
BACK_LINK = "\n---\n\n[Back to index](index.md)"

def append_insight(page: Path, insight: Insight):
    text = page.read_text()

    entry = f"**{insight.type.title()} — {insight.heading}**\n\n{insight.content}\n"

    if SECTION_HEADER not in text:
        # First code-derived note on this page — create the section
        insertion = f"\n---\n\n{SECTION_HEADER}\n{entry}"
        text = text.replace(BACK_LINK, insertion + BACK_LINK)
    else:
        # Section exists — append inside it
        text = text.replace(BACK_LINK, entry + BACK_LINK)

    page.write_text(text)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(filepath: str):
    source = Path(filepath)
    if not source.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    print(f"Analysing {source.name}...")
    analysis = analyse(source.read_text(), source.name)

    print(f"  {analysis.summary}")
    print(f"  {len(analysis.insights)} insight(s) found\n")

    written = 0
    for insight in analysis.insights:
        page = PAGE_MAP.get(insight.topic)
        if not page or not page.exists():
            print(f"  [SKIP] unknown topic: {insight.topic}")
            continue

        print(f"  [{insight.type.upper()}] {insight.topic} → {insight.heading}")
        append_insight(page, insight)
        written += 1

    print(f"\n{written} note(s) written. Review with: git diff")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code_to_notes.py path/to/script.py")
        sys.exit(1)
    main(sys.argv[1])
