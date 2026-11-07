# Assignment 18 — Python Code Analysis and Correction with CrewAI

A CrewAI crew finds and fixes the errors in the assignment's `fibonacci_iterative` function. Two worker agents do the work, a **Code Analyzer** that evaluates the code with a `CodeInterpreterTool` and a **Code Corrector** that applies the fixes, overseen by a **Manager** agent. Tasks run with `Process.sequential`, planning is enabled, and the notebook verifies the corrected code deterministically instead of trusting the model.

The notebook has been run end to end in Google Colab; the saved outputs show the full run ending in `VERIFICATION: PASS` and `OVERALL: PASS`.

## Files

| File | Purpose |
|---|---|
| `Assignment_18_Code_Analysis_Correction_CrewAI.ipynb` | The notebook, with outputs from a completed Colab run. |

## Run it in Colab

1. Open the notebook in Colab.
2. Provide the OpenAI key either way:
   - **Colab Secrets (recommended):** key icon in the left sidebar → add `OPENAI_API_KEY` → enable *Notebook access*.
   - **Paste it:** if no secret is found, Section 2 asks for the key with a hidden prompt. Reviewers can run the notebook without touching Secrets.
3. `Runtime → Run all`. The run is unattended: uv installs `crewai==1.15.33` (one to two minutes), the key is loaded, the first reachable model in `MODEL_CANDIDATES` (`gpt-4o-mini`, then `gpt-4o`) is selected, the crew runs, then verification and the rubric print `PASS`/`FAIL` lines.

The key is never printed. CrewAI's trace upload, telemetry and version check are disabled in Section 3, so the only network traffic is to the OpenAI API and no first-run prompt can stall the run.

## Notebook walkthrough

| Section | What it does |
|---|---|
| 1 Install | `uv pip install crewai==1.15.33` into the Colab interpreter. |
| 2 API key | Colab Secrets → environment variable → hidden `getpass` prompt. |
| 3 Settings | Model probe, tool timeout (10 s), input size cap (20 000 chars), telemetry off. |
| 4 Input code | The buggy function exactly as given, plus `validate_code` (type, non-empty, size) with a should-fail self-test. |
| 5 CodeInterpreterTool | Runs Python in a separate `python -I` process with a timeout and returns stdout, stderr and exit code. Self-tests: a good snippet runs, the buggy code reports `IndentationError`, an infinite loop is stopped by the timeout. |
| 6 Agents | `code_analyzer` (owns the tool), `code_corrector`, `manager` (`allow_delegation=True`). |
| 7 Tasks | `analysis_task` (numbered error list) → `correction_task` (`context=[analysis_task]`, must answer with one ```` ```python ```` block plus a change list). |
| 8 Crew | `Crew(process=Process.sequential, planning=True, planning_llm=llm, manager_agent=manager)`, started with `await crew.kickoff_async()` so it runs inside the notebook's existing event loop. Raw task outputs are printed. |
| 9 Results | Both agent outputs rendered as Markdown. |
| 10 Verification | Extracts the fenced code block, runs it through the same tool and compares `fibonacci_iterative(n)` with fixed expected lists for `n = -1, 0, 1, 2, 5, 10`. |
| 11 Rubric | Nine automated structure and verification checks; `OVERALL: PASS`. |

## What the crew found and fixed

The input code has two real defects:

- **Syntax:** the body of the `for` loop is not indented, so the file does not compile (`IndentationError: expected an indented block after 'for' statement`).
- **Logical:** `n == 0` is not handled; once the indentation is fixed the function would return `[0, 1]` for `n = 0` instead of `[]`.

In the saved run the Code Analyzer reported both (it also listed a third, cosmetic item about the `n == 1` / `n == 2` branches that the Corrector correctly left unchanged). The Code Corrector changed `if n < 0` to `if n <= 0` and indented the loop body. The verification cell confirmed the corrected function returns the right list for every tested `n`.

## Design notes

- **CrewAI 1.15.33**, current release, pinned, installed with uv.
- **`CodeInterpreterTool`:** the Docker-based `crewai_tools.CodeInterpreterTool` was removed in the CrewAI 1.15 line, and `Agent(allow_code_execution=True)` is now a deprecated no-op that reports "CodeInterpreterTool is no longer available". The notebook defines its own `CodeInterpreterTool` on `crewai.tools.BaseTool`: same name and role, runs in a subprocess with a timeout, works in Colab without Docker.
- **Sequential process with a manager:** with `Process.sequential` CrewAI runs the tasks in order itself; the Manager is attached as `manager_agent` (as in the course's fraud-detection example) and coordination comes from `planning=True`, which drafts a plan per task before execution. Changing one line to `Process.hierarchical` makes the manager delegate the tasks itself.
- **Trust boundary:** the input code is validated before it reaches the model, and the model's answer is not trusted. Section 10 extracts the code with an exact regex and executes it against fixed expected values, so the LLM never decides whether the fix passed.
- **Should-fail cases proven in the notebook:** validation rejects empty, non-string and oversized code; the tool reports the buggy code's `IndentationError` and kills an infinite loop by timeout.

## Running locally (optional)

CrewAI requires Python 3.10 to 3.13 (3.14 is rejected).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe "crewai==1.15.33" jupyter
```

Set `OPENAI_API_KEY` in the environment and open the notebook with Jupyter.
