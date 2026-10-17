"""
Executes the notebook's code cells against stub LLM / Tavily clients to prove the
plan -> research -> report flow works end to end, plus the should-fail paths.
No network calls, no API keys.
"""

import json
import pathlib
import re
import types
from dataclasses import dataclass
from typing import Callable

NB = pathlib.Path(__file__).parent / "Web_Research_ReAct_Agent.ipynb"

notebook = json.loads(NB.read_text(encoding="utf-8"))
code_cells = ["".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code"]

# Every code cell must at least parse (cell 0 is the `!pip install` magic).
for index, cell in enumerate(code_cells[1:], start=1):
    compile(cell, f"<cell {index}>", "exec")
print(f"PASS: all {len(code_cells) - 1} Python code cells compile")


# ---------------------------------------------------------------- stubs
class FakeMessage:
    def __init__(self, content):
        self.message = types.SimpleNamespace(content=content)


class FakeCompletions:
    def __init__(self, owner):
        self.owner = owner

    def create(self, messages, model):
        return types.SimpleNamespace(choices=[FakeMessage(self.owner.reply(messages))])


class FakeLLM:
    """Scripted OpenAI-compatible client."""

    def __init__(self):
        self.chat = types.SimpleNamespace(completions=FakeCompletions(self))
        self.calls = 0
        self.plan_reply = (
            '<questions>["What causes X?", "How has X changed?", "What policies address X?", '
            '"Who is most affected by X?", "What is the outlook for X?"]</questions>'
        )

    def reply(self, messages):
        self.calls += 1
        text = "\n".join(m["content"] for m in messages)

        if "You are a research planner" in text:
            return self.plan_reply
        if "You are a research report writer" in text:
            return "# Report on X\n\n## Introduction\n...\n\n## Conclusion\n..."
        # ReAct conversation: search on the first turn, answer once an observation is back.
        if any(m["role"] == "assistant" for m in messages):
            return "<thought>I have enough.</thought><response>- Fact one (http://a)</response>"
        return (
            "<thought>I should search.</thought>"
            '<tool_call>{"name": "web_search", "arguments": {"query": "X", "max_results": "3"}, "id": 0}</tool_call>'
        )


class FakeTavily:
    def __init__(self):
        self.queries = []

    def search(self, query, max_results=None):
        self.queries.append((query, max_results))
        return {
            "results": [
                {"title": "Source A", "url": "http://a", "content": "Content A"},
                {"title": "Source B", "url": "http://b", "content": "Content B"},
            ]
        }


# ---------------------------------------------------------------- exec cells
llm_client = FakeLLM()
tavily_client = FakeTavily()

ns = {
    "json": json,
    "re": re,
    "dataclass": dataclass,
    "Callable": Callable,
    "OpenAI": object,
    "llm_client": llm_client,
    "tavily_client": tavily_client,
    "LLM_MODEL": "stub-model",
}

# Skip cell 0 (pip install) and cell 1 (config: reads env vars, builds real clients).
for index, cell in enumerate(code_cells):
    if index < 2:
        continue
    exec(compile(cell, f"<cell {index}>", "exec"), ns)

print("PASS: notebook executed end to end against stubs")

# ---------------------------------------------------------------- assertions
agent = ns["agent"]
report = ns["report"]

assert len(agent.questions) == 5, agent.questions
assert len(agent.findings) == 5, agent.findings
assert all(set(f) == {"question", "answer"} for f in agent.findings)
assert agent.findings[0]["question"] == "What causes X?"
assert "Fact one" in agent.findings[0]["answer"]
print("PASS: plan produced 5 questions, each with a stored finding")

assert len(tavily_client.queries) == 5, tavily_client.queries
assert tavily_client.queries[0] == ("X", 3), tavily_client.queries[0]
print("PASS: web_search called once per question; max_results coerced '3' -> int 3")

assert report.startswith("# "), report[:40]
assert "## Introduction" in report and "## Conclusion" in report
print("PASS: report is Markdown with introduction and conclusion")

# ---------------------------------------------------------------- should-fail cases
ReactAgent = ns["ReactAgent"]
WebResearchAgent = ns["WebResearchAgent"]
web_search = ns["web_search"]

# 1. Hallucinated tool name must not crash the loop.
probe = ReactAgent(tools=[web_search], client=llm_client, model="stub", verbose=False)
observations = probe.process_tool_calls(['{"name": "delete_everything", "arguments": {}, "id": 0}'])
assert "Tool call failed" in observations[0] and "Unknown tool" in observations[0], observations
print("PASS: unknown tool name returns an error observation instead of executing")

# 2. Hallucinated argument name must be rejected.
observations = probe.process_tool_calls(
    ['{"name": "web_search", "arguments": {"qeury": "typo"}, "id": 0}']
)
assert "Unknown argument" in observations[0], observations
print("PASS: unknown argument name rejected before the function is called")

# 3. Malformed JSON tool call must not crash the loop.
observations = probe.process_tool_calls(["{not json"])
assert "Tool call failed" in observations[0], observations
print("PASS: malformed tool call JSON handled")

# 4. Planner that omits the <questions> tag must fail loudly.
llm_client.plan_reply = "Here are some questions: 1. What causes X?"
try:
    WebResearchAgent(topic="X", client=llm_client, model="stub", verbose=False).plan()
    raise AssertionError("expected ValueError")
except ValueError as error:
    assert "No <questions> tag" in str(error), error
print("PASS: unparseable plan raises instead of proceeding with an empty plan")

# 5. Invalid topic input rejected at the boundary.
for bad_topic in ["", "   ", 42, "x" * 201]:
    try:
        WebResearchAgent(topic=bad_topic, client=llm_client, model="stub", verbose=False)
        raise AssertionError(f"expected ValueError for {bad_topic!r}")
    except ValueError:
        pass
print("PASS: empty, whitespace, non-string and over-long topics rejected")

# 6. Search failure surfaces to the model as text, not a traceback.
class BrokenTavily:
    def search(self, query, max_results=None):
        raise RuntimeError("connection refused")


ns["tavily_client"] = BrokenTavily()
result = web_search.run(query="X", max_results=3)
assert result.startswith("Search failed") and "connection refused" in result, result
print("PASS: Tavily failure returned as a readable observation")

# 7. Repeated run() must not stack duplicate system prompts.
ns["tavily_client"] = FakeTavily()
before = probe.system_prompt
probe.run("question one", max_rounds=2)
probe.run("question two", max_rounds=2)
assert probe.system_prompt == before, "system_prompt mutated across runs"
print("PASS: system prompt is not mutated across repeated runs")

print("\nALL CHECKS PASSED")
