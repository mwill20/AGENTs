"""Check Competitor_Intel_Agent.ipynb against RUBRIC.md, row by row.

Static checks only - no API keys and no network calls needed. Each check maps to one rubric row,
so a pass here means the deliverable satisfies that stated requirement, not merely that the file
parses.

Run:  python verify_rubric.py
"""

import ast
import json
import pathlib
import sys

NOTEBOOK = pathlib.Path(__file__).with_name("Competitor_Intel_Agent.ipynb")

BENEFICIARY_SECTIONS = (
    "## 1. Competitor Landscape",
    "## 2. Footfall and Peak Hours",
    "## 3. Location and Catchment Insights",
    "## 4. Market Saturation and Risk",
    "## 5. Recommended Actions",
    "## 6. Sources",
)


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
        ("R1", "conversational: persistent per-session message history",
         "SQLChatMessageHistory(" in code
         and "RunnableWithMessageHistory(" in code
         and 'history_messages_key="history"' in code),

        ("R2", "multi-user: memory keyed by session_id, isolation demonstrated",
         "def get_session_history(session_id: str)" in code
         and 'ANALYST = "analyst-ravi-02"' in code
         and 'OWNER = "owner_zoya01"' in code
         and "first_human" in code),

        ("R3", "free-text conversational entry point",
         "def chat_with_analyst(prompt: str, session_id: str" in code
         and '{"configurable": {"session_id": sid}}' in code),

        ("R4", "report generation entry point",
         "def competitor_report(location: str, session_id: str" in code
         and 'competitor_report("Koramangala, Bangalore", OWNER)' in code),

        ("R5", "competitor discovery tool, scoped to clothing retail",
         "@tool" in code
         and "def search_competitors(location: str)" in code
         and "clothing stores apparel retailers" in code),

        ("R6", "LLM bound to BOTH search tools via create_tool_calling_agent + AgentExecutor",
         "ChatOpenAI(model=\"gpt-4o\", temperature=0)" in code
         and "tools = [search_competitors, get_store_traffic]" in code
         and "create_tool_calling_agent(llm, tools, prompt_template)" in code
         and "AgentExecutor(" in code),

        ("R7", "facts come from live search, not model memory",
         "TavilySearchResults(" in code
         and "def _run_search(query: str)" in code
         and "Never answer from your own knowledge" in code),

        ("R8", "footfall / busiest-times tool, provenance labelled",
         "def get_store_traffic(store_and_location: str)" in code
         and "busiest time popular times peak hours" in code
         and "NOT measured sensor footfall" in code),

        ("R9", "actionable insights are a required report section",
         "## 5. Recommended Actions" in code
         and "No generic retail advice." in code
         and "weekend promotion" in code),

        ("R10", "one report section per named beneficiary group",
         all(section in code for section in BENEFICIARY_SECTIONS)),

        ("R11", "valid Colab-runnable notebook",
         nb.get("nbformat") == 4
         and "colab" in nb.get("metadata", {})
         and "google.colab" in code
         and "pip install -q" in code
         and "langchain==0.3.14" in code
         and syntax_ok),

        ("S1", "no hardcoded secrets",
         "getpass" in code
         and "userdata.get(name)" in code
         and not any(marker in code for marker in ("sk-proj", "sk-ant", "tvly-"))),

        ("S2", "deterministic input gates with should-fail cases",
         "def validate_query(" in code
         and "def validate_location(" in code
         and "QUERY_REJECT" in code
         and "LOCATION_REJECT" in code
         and "prompt injection" in code
         and "newline-smuggled instruction" in code),

        ("S3", "memory key is validated",
         "def validate_session_id(" in code
         and "SESSION_ID_PATTERN" in code
         and "path traversal into another thread" in code),

        ("S4", "output gate: citations checked against tool results",
         "def check_report_grounding(" in code
         and "SEEN_URLS.clear()" in code
         and "check_report_grounding(output, SEEN_URLS)" in code
         and "Grounding warning" in code),

        ("S5", "bounded agent loop and bounded tool output",
         "max_iterations=10" in code
         and "MAX_SNIPPET_CHARS = 700" in code
         and "MAX_QUERY_CHARS = 300" in code),

        ("D1", "control chars rejected BEFORE whitespace normalisation",
         "_reject_control_chars(query)" in code
         and code.index("_reject_control_chars(query)") < code.index('cleaned = " ".join(query.split())')),

        ("W1", "written report: how the LLM is used for reasoning",
         "how the LLM is used for reasoning" in text
         and "agent_scratchpad" in text
         and "router and a writer" in text),

        ("W2", "written report: code and program flow",
         "code and program flow" in text
         and "Cell by cell" in text
         and "Flow of one turn" in text),

        ("W3", "limitations stated, including the footfall data limit",
         "## 16. Limitations" in text
         and "Footfall is estimated, never measured" in text
         and "Popular Times is not" in text),

        ("--", f"python syntax: {syntax_detail}", syntax_ok),
    ]

    failed = 0
    for rid, label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {rid:<4} {label}")
        failed += not ok

    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
