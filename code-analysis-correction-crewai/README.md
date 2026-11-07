# Python Code Analysis and Correction with CrewAI

A CrewAI crew finds and fixes the errors in a deliberately broken `fibonacci_iterative` function. Two worker agents do the work, a **Code Analyzer** that evaluates the code with a `CodeInterpreterTool` and a **Code Corrector** that applies the fixes, overseen by a **Manager** agent. Tasks run with `Process.sequential`, planning is enabled, and the notebook verifies the corrected code deterministically instead of trusting the model.

The notebook has been run end to end in Google Colab; the saved outputs show the full run ending in `VERIFICATION: PASS` and `OVERALL: PASS`.

## Purpose

This project demonstrates **tool-using agents that execute code**, **task context** and
**planning** in CrewAI 1.15, with the model kept out of the pass/fail decision. It solves "find and
fix bugs in a function" by letting the Analyzer run the code to see real tracebacks, letting the
Corrector propose a fix, and then having plain Python run the fix against fixed expected values.

## Pattern

**Sequential two-task crew with a manager and planning.** Analysis -> Correction, the second task
receiving the first's output through `context`. The Manager is attached as `manager_agent`;
with `Process.sequential` it does not delegate (see Design notes), and `planning=True` drafts a plan
per task before execution.

## Intended audience

Learners who want to see a custom `BaseTool` that runs code with a timeout, and a verification step
that treats the agent's answer as a hypothesis to test.

Expected background: intermediate Python (subprocesses, regular expressions) and comfort with
Jupyter or Colab (top-level `await`).

## Project status

Prototype. **The notebook was saved with outputs from a completed Colab
run** on `gpt-4o-mini`: both self-tests `PASS`, the crew finished two tasks, the verification cell
printed seven `PASS` lines and `VERIFICATION: PASS`, and the check block printed nine `PASS` lines and
`OVERALL: PASS`. The live cells were not re-run during repository preparation.

What **was** re-checked offline while preparing this repository, with no API key, using CrewAI
1.15.20 (the version available locally; the notebook pins 1.15.33): the section 4 and 5 self-tests
were extracted and executed. `validate_code` rejected all four should-fail inputs; the
`CodeInterpreterTool` ran a good snippet, reported the buggy code's `IndentationError`, and killed an
infinite loop at the 2-second timeout. The corrected function recorded in the saved output was then
run through the notebook's own section 10 harness and passed all six expected values.

## Files

| File | Purpose |
|---|---|
| `Code_Analysis_Correction_CrewAI.ipynb` | The notebook, with outputs from a completed Colab run. |
| `requirements.txt` | Pinned dependency, copied from the notebook's install cell. |
| `SECURITY.md` | Trust boundaries, controls and known gaps. |

## Run it in Colab

1. Open the notebook in Colab.
2. Provide the OpenAI key either way:
   - **Colab Secrets (recommended):** key icon in the left sidebar -> add `OPENAI_API_KEY` -> enable *Notebook access*.
   - **Paste it:** if no secret is found, Section 2 asks for the key with a hidden prompt. Reviewers can run the notebook without touching Secrets.
3. `Runtime -> Run all`. The run is unattended: uv installs `crewai==1.15.33` (one to two minutes), the key is loaded, the first reachable model in `MODEL_CANDIDATES` (`gpt-4o-mini`, then `gpt-4o`) is selected, the crew runs, then the verification and check cells print `PASS`/`FAIL` lines.

The key is never printed. CrewAI's trace upload, telemetry and version check are disabled in Section 3, so the only network traffic is to the OpenAI API and no first-run prompt can stall the run.

## Requirements

| Requirement | Notes |
|---|---|
| Python | `crewai` 1.15.33 declares `>=3.10,<3.14` on PyPI (3.14 is rejected). Written for Google Colab |
| Packages | `crewai==1.15.33`. The tool is built on `crewai.tools.BaseTool`, so no `crewai-tools` extra is needed |
| LLM | OpenAI (**paid, pay-as-you-go**), `gpt-4o-mini` then `gpt-4o`, `temperature=0` |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script (top-level `await`) |

## Settings

| Setting | Default | Notes |
|---|---|---|
| `MODEL_CANDIDATES` | `["gpt-4o-mini", "gpt-4o"]` | Probed with `client.models.retrieve`; first reachable wins |
| `TOOL_TIMEOUT_SECONDS` | `10` | Hard limit for one code-interpreter run |
| `MAX_CODE_CHARS` | `20_000` | Input size cap, applied in `validate_code` and again inside the tool |

## Notebook walkthrough

| Section | What it does |
|---|---|
| 1 Install | `uv pip install crewai==1.15.33` into the Colab interpreter. |
| 2 API key | Colab Secrets -> environment variable -> hidden `getpass` prompt. |
| 3 Settings | Model probe, tool timeout (10 s), input size cap (20 000 chars), telemetry off. |
| 4 Input code | The buggy function exactly as given, plus `validate_code` (type, non-empty, size) with a should-fail self-test. |
| 5 CodeInterpreterTool | Runs Python in a separate `python -I` process with a timeout and returns stdout, stderr and exit code. Self-tests: a good snippet runs, the buggy code reports `IndentationError`, an infinite loop is stopped by the timeout. |
| 6 Agents | `code_analyzer` (owns the tool), `code_corrector`, `manager` (`allow_delegation=True`). |
| 7 Tasks | `analysis_task` (numbered error list) -> `correction_task` (`context=[analysis_task]`, must answer with one ```` ```python ```` block plus a change list). |
| 8 Crew | `Crew(process=Process.sequential, planning=True, planning_llm=llm, manager_agent=manager)`, started with `await crew.kickoff_async()` so it runs inside the notebook's existing event loop. Raw task outputs are printed. |
| 9 Results | Both agent outputs rendered as Markdown. |
| 10 Verification | Extracts the fenced code block, runs it through the same tool and compares `fibonacci_iterative(n)` with fixed expected lists for `n = -1, 0, 1, 2, 5, 10`. |
| 11 Checks | Nine automated structure and verification checks; `OVERALL: PASS`. |

## What the crew found and fixed

The input code has two real defects:

- **Syntax:** the body of the `for` loop is not indented, so the file does not compile (`IndentationError: expected an indented block after 'for' statement`).
- **Logical:** `n == 0` is not handled; once the indentation is fixed the function would return `[0, 1]` for `n = 0` instead of `[]`.

In the saved run the Code Analyzer reported both (it also listed a third, cosmetic item about the `n == 1` / `n == 2` branches that the Corrector correctly left unchanged). The Code Corrector changed `if n < 0` to `if n <= 0` and indented the loop body. The verification cell confirmed the corrected function returns the right list for every tested `n`.

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for the model probe, the planning step and two tasks, each bounded by
  `max_iter`
- Execute Python written by the Code Analyzer, and later the Corrector's fix, in a subprocess with
  a 10-second timeout, in isolated mode, in a temporary directory

This system is not allowed to:

- Run code from the Code Corrector during the crew run. Only the Analyzer owns the tool, and the
  check cell asserts that
- Accept input code that is not a non-empty string under 20,000 characters
- Decide whether the fix worked. Section 10 does that with fixed expected values

Human approval is required for: nothing in the delivered build, because the code under test is a
constant in the notebook. **If the input code ever comes from outside, read `SECURITY.md` first:**
the subprocess is a timeout and an import guard, not a sandbox.

## Design notes

- **CrewAI 1.15.33**, current release at the time of writing, pinned, installed with uv.
- **`CodeInterpreterTool`:** the Docker-based `crewai_tools.CodeInterpreterTool` was removed in the CrewAI 1.15 line, and `Agent(allow_code_execution=True)` is now a deprecated no-op that reports "CodeInterpreterTool is no longer available". The notebook defines its own `CodeInterpreterTool` on `crewai.tools.BaseTool`: same name and role, runs in a subprocess with a timeout, works in Colab without Docker.
- **Sequential process with a manager:** with `Process.sequential` CrewAI runs the tasks in order itself; the Manager is attached as `manager_agent` (as in the AG2 Classic fraud-detection example) and coordination comes from `planning=True`, which drafts a plan per task before execution. Changing one line to `Process.hierarchical` makes the manager delegate the tasks itself.
- **Trust boundary:** the input code is validated before it reaches the model, and the model's answer is not trusted. Section 10 extracts the code with an exact regex and executes it against fixed expected values, so the LLM never decides whether the fix passed.
- **Should-fail cases proven in the notebook:** validation rejects empty, non-string and oversized code; the tool reports the buggy code's `IndentationError` and kills an infinite loop by timeout.

## Evaluation

Section 11 is a nine automated checks: two worker agents with the expected roles, a manager attached,
sequential process, planning on, the Analyzer alone owns the tool, task order and `context` are
right, the analysis mentions indentation and the `n == 0` case, the correction contains the
function, and the section 10 verification passed.

| Check | Recorded result |
|---|---|
| Validation and tool self-tests (sections 4 and 5) | PASS in the saved run; PASS re-run offline for this repository |
| Section 10 verification of the saved corrected code | PASS (7 of 7) in the saved run; PASS re-run offline for this repository |
| Checks (section 11) | 9 of 9 PASS in the saved run. Not re-run (needs a live crew) |
| Whether the approach generalises to other buggy code | Not yet measured. One fixed input |

## Running locally (optional)

CrewAI requires Python 3.10 to 3.13 (3.14 is rejected).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe "crewai==1.15.33" jupyter
```

Set `OPENAI_API_KEY` in the environment and open the notebook with Jupyter.

## Security considerations

See [SECURITY.md](SECURITY.md). The short version: the model writes code and the notebook runs it.
The subprocess has a timeout and isolated mode, not a sandbox.

## Limitations

- One fixed input. The crew has only ever been asked to fix one eleven-line function.
- The verification checks six return values; it does not inspect the corrected code for anything
  else it might do.
- The Manager is present but, under `Process.sequential`, does not delegate.
- Non-deterministic in the agents' prose even at `temperature=0`; the verified result is what is
  stable.
- Needs a Jupyter-style environment because of top-level `await`.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
