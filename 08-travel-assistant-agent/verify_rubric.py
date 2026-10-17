"""Check Travel_Assistant_Agent.ipynb against the assignment rubric.

Static checks only - no API keys and no network calls needed. Each check maps to one
rubric row, so a pass here means the deliverable satisfies that stated requirement,
not merely that the file parses.

Run:  python verify_rubric.py
"""

import ast
import json
import pathlib
import sys

NOTEBOOK = pathlib.Path(__file__).with_name("Travel_Assistant_Agent.ipynb")


def load():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = nb["cells"]
    code = "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "code")
    text = "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "markdown")
    return nb, cells, code, text


def main() -> int:
    if not NOTEBOOK.exists():
        print(f"FAIL  notebook not found: {NOTEBOOK}")
        return 1

    nb, cells, code, text = load()

    # Every code cell must be syntactically valid Python (ignoring ! magics).
    syntax_ok, syntax_detail = True, "all code cells parse"
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        stripped = "\n".join("" if ln.lstrip().startswith("!") else ln for ln in src.splitlines())
        try:
            ast.parse(stripped)
        except SyntaxError as exc:
            syntax_ok, syntax_detail = False, f"cell {i}: {exc}"
            break

    checks = [
        ("R1", "custom weather tool via @tool decorator",
         "@tool" in code and "def get_weather(" in code and "weatherapi.com" in code.lower()),
        ("R2", "attractions search tool (Tavily)",
         "def search_attractions(" in code and "TavilySearchResults" in code),
        ("R3", "both tools bound with create_tool_calling_agent",
         "create_tool_calling_agent(llm, tools, prompt_template)" in code
         and "tools = [get_weather, search_attractions]" in code),
        ("R4", "invoked through AgentExecutor",
         "AgentExecutor(" in code and "agent_executor.invoke(" in code),
        ("R5", "LLM used for reasoning / summarising",
         "ChatOpenAI(" in code and "temperature=0" in code),
        ("R6", "one destination yields weather AND attractions",
         "def travel_assistant(" in code and 'travel_assistant("Kyoto")' in code),
        ("R7", "deliverable is a valid .ipynb",
         nb.get("nbformat") == 4 and len(cells) > 0 and syntax_ok),
        ("R8", "report explains LLM reasoning",
         "how the LLM is used for reasoning" in text and "agent_scratchpad" in text),
        ("R9", "report explains code and program flow",
         "code and program flow" in text and "Cell by cell" in text),
        ("S1", "no hardcoded secrets",
         "getpass" in code
         and not any(m in code for m in ("sk-", "tvly-"))),
        ("S2", "should-fail case is exercised",
         "should_reject" in code and "should_accept" in code
         and "prompt injection" in code and "validate_destination" in code),
        ("S3", "agent iteration cap and request timeout present",
         "max_iterations=" in code and "timeout=10" in code),
        ("S4", "control chars rejected before whitespace normalisation",
         "control characters" in code and "ord(ch) < 32" in code),
        ("--", f"python syntax: {syntax_detail}", syntax_ok),
    ]

    failed = 0
    for rid, label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {rid}  {label}")
        failed += not ok

    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
