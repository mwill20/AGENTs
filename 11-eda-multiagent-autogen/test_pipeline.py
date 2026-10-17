"""Behavioural test for the notebook's orchestration — rubric rows A9 and S4.

verify_assignment.py checks the state machine statically. This script actually runs it: it loads
the notebook's agent and orchestration cells, then plays scripted transcripts through
select_speaker() and asserts the pipeline goes where it is supposed to go.

Requires autogen installed (see requirements.txt). No API key is used and no model is called -
agents are constructed, never invoked.

    python test_pipeline.py
"""

from __future__ import annotations

import atexit
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

try:
    import autogen  # noqa: F401
except ImportError:
    print("SKIP: autogen is not installed. pip install -r requirements.txt")
    sys.exit(0)

# Agents are constructed but never invoked, so no real key is needed and no request is made.
os.environ.setdefault("OPENAI_API_KEY", "not-used-no-model-call-is-made")

NOTEBOOK = Path(__file__).with_name("EDA_MultiAgent_AutoGen.ipynb")
nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

# The notebook cells write a workspace and a model cache relative to the working directory.
# Run them in a scratch directory so this test leaves the deliverable folder untouched.
# Cleanup chdirs out first - Windows refuses to remove a directory that is the current one.
_home = Path.cwd()
_scratch = tempfile.mkdtemp()
os.chdir(_scratch)
atexit.register(lambda: (os.chdir(_home), shutil.rmtree(_scratch, ignore_errors=True)))

# The cells needed to stand the pipeline up: key/config, dataset, audit, gate, executor, contract,
# agents, orchestration. Identified by content so cell renumbering cannot silently break this.
NEEDED = [
    "def load_key(",
    "def make_raw_dataframe(",
    "def audit(",
    "def scan_code(",
    "class GuardedExecutor(",
    "def validate_report(",
    "def validate_clean_data(",
    "def build_agents(",
    "def select_speaker(",
]

ns: dict = {}
for needle in NEEDED:
    src = next(
        ("".join(c["source"]) for c in nb["cells"]
         if c["cell_type"] == "code" and needle in "".join(c["source"])),
        None,
    )
    if src is None:
        sys.exit(f"FATAL: no cell defines {needle}")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, f"<notebook {needle}>", "exec"), ns)

select_speaker = ns["select_speaker"]
groupchat = ns["groupchat"]
STATE = ns["STATE"]
AGENTS = ns["AGENTS"]

OK = "exitcode: 0 (execution succeeded)\nCode output: fine"
ERR = "exitcode: 1 (execution failed)\nCode output: NameError: name 'df' is not defined"

failures: list[str] = []


def play(label: str, script: list[tuple[str, str, str | None]]) -> None:
    """script: (speaker_key, that speaker's message, expected next speaker key or None)."""
    print(f"\n{label}")
    STATE.run_id = "test"
    STATE.reset()
    groupchat.messages.clear()

    for speaker_key, message, expected in script:
        groupchat.messages.append({"name": AGENTS[speaker_key].name, "content": message})
        nxt = select_speaker(AGENTS[speaker_key], groupchat)
        got = None if nxt is None else next(k for k, v in AGENTS.items() if v is nxt)
        ok = got == expected
        if not ok:
            failures.append(f"{label}: after {speaker_key}, expected {expected}, got {got}")
        print(f"  [{'ok  ' if ok else 'FAIL'}] {speaker_key:<8} -> {str(got):<8} (expected {expected})")


# A9: the critic hop and the revision are not optional.
play(
    "happy path - one retry in the prep stage, then the mandatory critic revision",
    [
        ("admin", "task statement", "prep"),
        ("prep", "```python\nprint(1)\n```", "executor"),
        ("executor", ERR, "prep"),                              # retry 1 of 2
        ("prep", "corrected cleaning code", "executor"),
        ("executor", OK, "eda"),
        ("eda", "stats and charts", "executor"),
        ("executor", OK, "report"),
        ("report", "first report", "executor"),
        ("executor", OK, "critic"),                             # first report always goes to review
        ("critic", "1. ...\nFEEDBACK COMPLETE", "report"),      # A9: feedback drives a rewrite
        ("report", "revised report", "executor"),
        ("executor", OK, None),                                 # revised report accepted, run ends
    ],
)
if not STATE.revised:
    failures.append("happy path: the revision flag was never set")

# S4: a stage that never succeeds must abort with a reason, not loop until max_round.
play(
    "should-fail path - a stage that never succeeds aborts within its retry budget",
    [
        ("admin", "task statement", "prep"),
        ("prep", "broken", "executor"),
        ("executor", ERR, "prep"),      # fix 1
        ("prep", "still broken", "executor"),
        ("executor", ERR, "prep"),      # fix 2
        ("prep", "still broken", "executor"),
        ("executor", ERR, None),        # budget exhausted
    ],
)
print(f"  STATE.aborted = {STATE.aborted!r}")
if not STATE.aborted:
    failures.append("abort path: STATE.aborted was not set")

# S4: the critic writes no code, so it must never be routed to the executor.
play(
    "the critic is never routed to the executor",
    [
        ("admin", "task statement", "prep"),
        ("prep", "code", "executor"),
        ("executor", OK, "eda"),
        ("eda", "code", "executor"),
        ("executor", OK, "report"),
        ("report", "first report", "executor"),
        ("executor", OK, "critic"),
        ("critic", "findings", "report"),
    ],
)

# S8: the data post-condition must actually be wired into the executor the agents use.
print("\nthe executor carries the data post-condition")
executor = ns["CODE_EXECUTOR"]
if executor.post_condition is None:
    failures.append("post-condition: CODE_EXECUTOR was built without one")
    print("  [FAIL] CODE_EXECUTOR.post_condition is None")
else:
    ok, reasons = executor.post_condition()
    print(f"  [ok  ] wired and callable -> ok={ok}, reasons={len(reasons)}")
    if not isinstance(ok, bool) or not isinstance(reasons, list):
        failures.append("post-condition: did not return (bool, list)")
    # No cleaned file exists in this scratch dir, so it must refuse rather than pass by default.
    if ok:
        failures.append("post-condition: passed with no cleaned file present - fails open")

print()
if failures:
    print(f"FAILURES ({len(failures)}):")
    for failure in failures:
        print("  -", failure)
    sys.exit(1)
print("ALL ORCHESTRATION TESTS PASSED")
