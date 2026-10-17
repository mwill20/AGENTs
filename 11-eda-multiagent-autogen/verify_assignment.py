"""Verify EDA_MultiAgent_AutoGen.ipynb against RUBRIC.md.

No API key, no network, no autogen install required.

Structural rows are checked by parsing the notebook. Behavioural rows are checked by extracting
the notebook's own scan_code() and validate_report() and executing them - so a check cannot pass
against code that is not in the deliverable.

    python verify_assignment.py
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

NOTEBOOK = Path(__file__).with_name("EDA_MultiAgent_AutoGen.ipynb")

results: list[tuple[str, bool, str]] = []


def check(row: str, passed: bool, detail: str = "") -> None:
    results.append((row, bool(passed), detail))


# --------------------------------------------------------------------------------------
# Load the notebook
# --------------------------------------------------------------------------------------

if not NOTEBOOK.exists():
    sys.exit(f"FATAL: {NOTEBOOK.name} not found next to this script")

nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
cells = nb["cells"]
code_cells = [(i, "".join(c["source"])) for i, c in enumerate(cells) if c["cell_type"] == "code"]
all_code = "\n".join(src for _, src in code_cells)
all_text = "\n".join("".join(c["source"]) for c in cells)


def cell_with(needle: str) -> tuple[int, str] | None:
    for index, src in code_cells:
        if needle in src:
            return index, src
    return None


# --------------------------------------------------------------------------------------
# Structural checks
# --------------------------------------------------------------------------------------

check("A1 autogen pinned", 'ag2[openai]==0.9.10' in all_code, "classic 0.2 API via the ag2 fork")
check("A1 pin is exact, not a range", "ag2>=" not in all_code and "ag2~=" not in all_code)
check("A1 python range guarded", "(3, 10) <= sys.version_info[:2] < (3, 14)" in all_code,
      "unsupported runtime fails with an actionable message, not a pip wall")
check("A1 import failure is actionable", "autogen did not import" in all_code)
check("A1 openai upper bound set", '"openai<4"' in all_code,
      "ag2's extra leaves openai unbounded")

AGENT_NAMES = [
    "Admin",
    "Data_Preparation_Agent",
    "EDA_Agent",
    "Report_Generator_Agent",
    "Critic_Agent",
    "Executor",
]
missing_agents = [n for n in AGENT_NAMES if f'name="{n}"' not in all_code]
check("A2-A7 six named agents", not missing_agents, f"missing: {missing_agents}" if missing_agents else "all six constructed")

check(
    "A2 prep agent does cleaning",
    "Data Preparation Agent. You handle data cleaning and preprocessing" in all_code,
)
check("A3 EDA agent does stats + charts", 'CHART: ' in all_code and "correlation matrix" in all_code)
check("A4 report agent writes the report", "You are the Report Generator Agent" in all_code)
check("A5 critic reviews", "ACTIONABILITY" in all_code and "You write NO code" in all_code)
check(
    "A6 executor gates and runs code",
    'code_execution_config={"executor": code_executor}' in all_code,
)
check(
    "A7 admin owns the task and the gate",
    "You are the Admin." in all_code and "run_eda_pipeline" in all_code,
)

group_chat = cell_with("groupchat = GroupChat(")
check("A8 GroupChat constructed", group_chat is not None)
if group_chat:
    _, src = group_chat
    in_chat = all(k in src for k in ('"admin"', '"prep"', '"eda"', '"report"', '"critic"', '"executor"'))
    check("A8 all six agents in the GroupChat", in_chat)
check("A8 GroupChatManager constructed", "manager = GroupChatManager(" in all_code)

check(
    "A9 critic feedback loop is hard-coded",
    'return go(agents["critic"], "first report ready for review")' in all_code
    and 'return go(agents["report"], "revise with critic feedback")' in all_code,
    "report -> critic -> report",
)

SECTIONS = [
    "## 1. Dataset Overview",
    "## 2. Data Preparation Summary",
    "## 3. Key Insights and Findings",
    "## 4. Visualizations",
    "## 5. Conclusions and Recommendations",
    "## 6. Critic Review Response",
]
check(
    "A10-A12 six required report sections defined once",
    all(f'"{s}"' in all_code for s in SECTIONS),
)

# --- security rows ---------------------------------------------------------------------

KEY_SHAPED = re.compile(r"(sk-[A-Za-z0-9_\-]{16,}|api[_-]?key[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-]{12,}[\"'])", re.I)
leaks = [i for i, src in code_cells if KEY_SHAPED.search(src)]
check("S1 no key-shaped literal in any code cell", not leaks, f"cells: {leaks}" if leaks else "clean")
check("S1 Colab Secrets -> env -> getpass", all(t in all_code for t in ("userdata.get", "os.environ.get", "getpass(")))
check("S1 only a boolean is printed", 'print("OPENAI_API_KEY loaded:", bool(' in all_code)

check("S2 deterministic AST gate exists", "def scan_code(" in all_code and "ast.parse(" in all_code)
check("S2 import allowlist is default-deny", "ALLOWED_IMPORTS" in all_code and "not on the allowlist" in all_code)
check("S3 gate enforced in the executor", "class GuardedExecutor(LocalCommandLineCodeExecutor)" in all_code)
check("S3 refusal precedes execution", all_code.index("GATE_REFUSAL.format") < all_code.index("result = super().execute_code_blocks"))

check("S4 per-block timeout", "CODE_EXECUTOR = GuardedExecutor(" in all_code
      and "timeout=90," in all_code)
check("S4 bounded retries", "MAX_FIXES = 2" in all_code)
check("S4 bounded rounds", "MAX_ROUND = 30" in all_code)
check("S4 unattended, never prompts", all_code.count('human_input_mode="NEVER"') >= 2)
check(
    "S4 speaker selection is deterministic",
    "speaker_selection_method=select_speaker" in all_code and '"auto"' not in all_code,
)
check(
    "S4 agents cannot terminate the run",
    "is_termination_msg=lambda message: False" in all_code,
)
check("S4 no Docker dependency", "DockerCommandLineCodeExecutor" not in all_code)

check("S5 output validation exists", "def validate_report(" in all_code)
validation_cell = cell_with("accepted, critical, advisory = validate_report(report_text")
render_cell = cell_with("display(Markdown(report_text))")
check(
    "S5 validation runs before rendering",
    validation_cell is not None and render_cell is not None and validation_cell[0] < render_cell[0],
    f"validate at cell {validation_cell[0]}, render at cell {render_cell[0]}" if validation_cell and render_cell else "",
)
check("S5 rendering is gated on acceptance", "if accepted:" in all_code)

check("S8 data post-condition exists", "def validate_clean_data(" in all_code)
check(
    "S8 post-condition injected into the executor",
    "post_condition=lambda: validate_clean_data(WORK_DIR, BASELINE)" in all_code,
)
check(
    "S8 a failed post-condition becomes a retryable exit 1",
    "DATA POST-CONDITION FAILED" in all_code
    and "output=result.output + POSTCOND_FAILURE.format(details=details)" in all_code,
    "the agent's own stdout is preserved alongside the reasons",
)
check(
    "S8 post-condition runs only after a clean execution",
    "if result.exit_code == 0 and self.post_condition is not None:" in all_code,
)
check(
    "S8 schema declares discount_pct units",
    "FRACTION, not a percentage" in all_code and "0.15 means 15% off" in all_code,
    "the ambiguity that caused the observed defect",
)
check(
    "S8 task statement announces the post-condition",
    "checked automatically after your code runs" in all_code,
)

check("S6 audit log exists", "AUDIT_LOG = []" in all_code and "def audit(" in all_code)
check(
    "S6 audit covers gate, exec, post-condition, transitions, validation",
    all(e in all_code for e in
        ('"code_gate"', '"code_exec"', '"post_condition"', '"transition"', '"report_validation"')),
)
check("S7 baseline profile precedes the agents", "BASELINE = {" in all_code and all_code.index("BASELINE = {") < all_code.index("def build_agents("))

check("honesty: dataset labelled synthetic", "synthetic" in all_text.lower())
check("honesty: limitations documented", "## 12. Limitations" in all_text)
check("honesty: gate not oversold as a sandbox", "is not a sandbox" in all_text)

# --------------------------------------------------------------------------------------
# Behavioural checks - run the notebook's own functions
# --------------------------------------------------------------------------------------

# The exec() below runs code lifted straight out of the notebook this script verifies. That is the
# point: a behavioural check must run the deliverable's own functions, not a copy that could drift.
# The input is the sibling .ipynb under version control, not untrusted data. The strings in
# SHOULD_BLOCK are inert test fixtures - they are passed to scan_code() as text and asserted to be
# refused; nothing in this file executes them.
ns: dict = {}
for needle in ("def scan_code(", "def validate_report("):
    found = cell_with(needle)
    if not found:
        sys.exit(f"FATAL: no cell defines {needle}")
    with contextlib.redirect_stdout(io.StringIO()):   # the cells print a readiness line
        exec(compile(found[1], f"<notebook {needle}>", "exec"), ns)

scan_code = ns["scan_code"]
validate_report = ns["validate_report"]

SHOULD_BLOCK = [
    ("import os; os.system('id')", "python", "os import"),
    ("import subprocess; subprocess.run(['ls'])", "python", "subprocess import"),
    ("import socket; socket.socket()", "python", "socket import"),
    ("import requests; requests.get('http://x.test')", "python", "requests import"),
    ("import shutil; shutil.rmtree('.')", "python", "shutil import"),
    ("import pickle; pickle.loads(b'')", "python", "pickle import"),
    ("import pandas as pd; pd.read_csv('https://x.test/a.csv')", "python", "URL literal"),
    ("open('/etc/passwd').read()", "python", "absolute path"),
    ("open('../../.env').read()", "python", "parent path"),
    ("exec('x=1')", "python", "exec call"),
    ("eval('1+1')", "python", "eval call"),
    ("__import__('os')", "python", "__import__ escape"),
    ("getattr(__builtins__, 'eval')", "python", "getattr escape"),
    ("pip install evil", "python", "shell-style, unparseable"),
    ("rm -rf /", "bash", "non-python language"),
    ("print('x')", "javascript", "non-python language"),
    ("x = 1\n" + "# pad\n" * 12000, "python", "oversized block"),
]

SHOULD_ALLOW = [
    ("import pandas as pd\ndf = pd.read_csv('raw_sales_data.csv')\nprint(df.describe())", "python"),
    ("import numpy as np\nprint(np.nanmean([1.0, 2.0]))", "python"),
    (
        'import matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt\n'
        'fig, ax = plt.subplots()\nax.set_title("t")\nfig.savefig("chart.png")',
        "python",
    ),
    ("import pandas as pd\npd.DataFrame({'a': [1]}).to_csv('cleaned_sales_data.csv', index=False)", "python"),
    ("with open('eda_report.md', 'w') as fh:\n    fh.write('## 1. Dataset Overview\\n')", "python"),
    ("import pandas as pd\ndf = pd.read_csv('c.csv')\nprint(df.groupby('region')['units_sold'].mean())", "python"),
]

leaked = [label for code, lang, label in SHOULD_BLOCK if scan_code(code, lang)[0]]
check("S2 behavioural: every should-fail case is blocked", not leaked, f"leaked: {leaked}" if leaked else f"{len(SHOULD_BLOCK)} cases blocked")

false_positives = [code.splitlines()[0] for code, lang in SHOULD_ALLOW if not scan_code(code, lang)[0]]
check(
    "S2 behavioural: no false positives on real EDA code",
    not false_positives,
    f"rejected: {false_positives}" if false_positives else f"{len(SHOULD_ALLOW)} cases allowed",
)

with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    for name in ("a.png", "b.png", "c.png"):
        (work / name).write_bytes(b"\x89PNG\r\n\x1a\n")

    baseline = {"rows": 1235, "columns": 9, "column_names": ["region", "units_sold", "unit_price"]}

    good = "\n".join(SECTIONS[:1]) + f"""
{baseline['rows']} rows and {baseline['columns']} columns.

{SECTIONS[1]}
Dropped duplicates.

{SECTIONS[2]}
`region` drives variance.

{SECTIONS[3]}
![a](a.png)
![b](b.png)
![c](c.png)

{SECTIONS[4]}
Rebalance discounts.

{SECTIONS[5]}
Finding 1 addressed.
"""
    accepted, critical, advisory = validate_report(good, work, baseline)
    check("S5 behavioural: a well-formed report is accepted", accepted, f"critical: {critical}")

    bad_cases = {
        "missing section": good.replace(SECTIONS[3], "## 4. Pictures"),
        "dead chart reference": good.replace("![c](c.png)", "![c](ghost.png)"),
        "too few charts": good.replace("![b](b.png)\n![c](c.png)", ""),
        "external URL": good.replace("Rebalance discounts.", "See https://example.com/benchmark"),
        "fabricated row count": good.replace(str(baseline["rows"]), "9999"),
        "fabricated column count": good.replace(f"and {baseline['columns']} columns", "and 4 columns"),
        "empty report": "   ",
    }
    survived = [label for label, text in bad_cases.items() if validate_report(text, work, baseline)[0]]
    check(
        "S5 behavioural: every should-fail report is rejected",
        not survived,
        f"accepted anyway: {survived}" if survived else f"{len(bad_cases)} cases rejected",
    )

    _, _, adv = validate_report(good.replace("`region`", "`invented_column`"), work, baseline)
    check("S5 behavioural: unknown column-like token raises an advisory", bool(adv), adv[0] if adv else "none raised")

# --- S8 behavioural: the data post-condition -------------------------------------------

try:
    import pandas as pd
except ImportError:
    check("S8 behavioural", False, "SKIPPED - pandas not installed; pip install -r requirements.txt")
else:
    # validate_clean_data's signature defaults to CLEAN_CSV, which lives in the dataset cell.
    # Read the literal out of the notebook rather than hardcoding it, so it cannot drift.
    clean_csv = re.search(r'CLEAN_CSV\s*=\s*"([^"]+)"', all_code).group(1)
    ns.setdefault("CLEAN_CSV", clean_csv)
    ns.setdefault("Path", Path)
    found = cell_with("def validate_clean_data(")
    if not found:
        sys.exit("FATAL: no cell defines validate_clean_data")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(found[1], "<notebook validate_clean_data>", "exec"), ns)

    validate_clean_data = ns["validate_clean_data"]
    discount_max = ns["DISCOUNT_MAX"]

    RAW_ROWS, RAW_COLUMNS = 1235, 9
    columns = ["order_id", "order_date", "region", "product_category", "units_sold",
               "unit_price", "discount_pct", "customer_rating", "returned"]
    data_baseline = {"rows": RAW_ROWS, "columns": RAW_COLUMNS, "column_names": columns}

    clean = pd.DataFrame({
        "order_id": range(1000, 1000 + 1200),
        "order_date": ["2024-03-01"] * 1200,
        "region": ["North"] * 1200,
        "product_category": ["Electronics"] * 1200,
        "units_sold": [3.0] * 1200,
        "unit_price": [25.0] * 1200,
        "discount_pct": [0.10] * 1200,
        "customer_rating": [4.0] * 1200,
        "returned": ["No"] * 1200,
    })

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        def run_contract(frame):
            if frame is not None:
                frame.to_csv(work / clean_csv, index=False)
            return validate_clean_data(work, data_baseline)

        check("S8 behavioural: a correctly cleaned dataset is accepted",
              run_contract(clean)[0], f"discount_pct within [0, {discount_max}]")

        # The exact defect observed in a real run: clip(0, 100) against a fraction column.
        observed = clean.copy()
        observed.loc[observed.index[:19], "discount_pct"] = 1.5
        ok, reasons = run_contract(observed)
        check("S8 behavioural: the observed clip(0,100) defect is caught",
              not ok and any("fraction, not a percentage" in r for r in reasons),
              reasons[0] if reasons else "not caught")

        bad_frames = {
            "duplicate rows left in": pd.concat([clean, clean.head(20)], ignore_index=True),
            "nulls neither imputed nor dropped": clean.assign(
                customer_rating=[None] * 10 + [4.0] * 1190),
            "unparsed date strings left": clean.assign(
                order_date=["not-a-date"] * 5 + ["2024-03-01"] * 1195),
            "negative unit price": clean.assign(unit_price=[-1.0] + [25.0] * 1199),
            "most of the dataset discarded": clean.head(100),
            "more rows than the raw file": pd.concat([clean, clean], ignore_index=True),
            "a required column dropped": clean.drop(columns=["discount_pct"]),
        }
        survived = [label for label, frame in bad_frames.items() if run_contract(frame)[0]]
        check("S8 behavioural: every should-fail dataset is rejected", not survived,
              f"accepted anyway: {survived}" if survived else f"{len(bad_frames)} cases rejected")

        (work / clean_csv).unlink()
        ok, reasons = run_contract(None)
        check("S8 behavioural: a missing cleaned file is rejected",
              not ok and "was not written" in reasons[0], reasons[0] if reasons else "")

# --------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------

width = max(len(row) for row, _, _ in results)
failed = 0

print(f"\n{NOTEBOOK.name} - {len(results)} checks\n")
for row, passed, detail in results:
    status = "PASS" if passed else "FAIL"
    failed += int(not passed)
    print(f"  [{status}] {row:<{width}}  {detail}")

print(f"\n{len(results) - failed} passed, {failed} failed")
sys.exit(1 if failed else 0)
