# Security: Assignment 11 (Multi-Agent EDA with AutoGen)

This project's central risk is stated plainly: **an LLM writes Python and the notebook runs it on
the host.** Everything below follows from that. It is a coursework notebook on synthetic data, not
a deployed service. The full design is explained in the README's "The security design" section;
this file summarises it as a threat table and lists what is not covered.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Agents -> `scan_code()` gate | Python code blocks written by the LLM | **Untrusted code** |
| Gate -> `GuardedExecutor` -> local interpreter | Approved code, run in a scoped working directory | Trusted only after the gate passes |
| Agents -> OpenAI | Prompts, dataset excerpts, API key | Third-party processing |
| Executor output -> agents | stdout, errors, files written | Untrusted |
| Agents -> report | Model-written prose and chart references | Untrusted until `validate_report()` passes |
| Cleaned data -> analysis | `cleaned_sales_data.csv` | Untrusted until `validate_clean_data()` passes |

## Controls present in the code

| Threat | Control |
|---|---|
| LLM-written code touching the system | `scan_code()` parses every block with `ast` and applies default-deny rules: Python only (no shell, `!pip`, `%magic`), one block per message, an import allowlist (pandas, numpy, matplotlib, seaborn and 11 stdlib modules), blocked calls (`eval`, `exec`, `compile`, `__import__`, `getattr`, `globals`, `locals`), relative paths only, no URL-scheme literals, 20,000-character cap |
| Policy that exists only in the prompt | The gate is enforced inside `GuardedExecutor.execute_code_blocks()` before `super()` runs. A refusal returns `exit_code=1` with a fix-it message |
| Runaway agents | 90 s per code block, 2 fix retries per stage, 30 turns maximum, `human_input_mode="NEVER"`, and `is_termination_msg` forced to `False` so an agent cannot end the run with a magic word |
| LLM deciding who speaks next | Speaker selection is a plain Python state machine, so control flow is deterministic |
| Exfiltration or hallucinated citations in the report | `validate_report()` rejects any external URL, missing sections, fewer than 3 embedded charts, chart references to files that do not exist, and a dataset shape that does not match the baseline profile computed before any agent ran |
| Silently wrong cleaned data | `validate_clean_data()` post-condition: required columns, no duplicates, no nulls in numeric columns, `discount_pct` within `[0, 0.30]`, `unit_price > 0`, no unparsed dates, row count between half and all of the original. Failures flow back through the retry path |
| Hardcoded or leaked keys | Colab Secrets, then environment, then `getpass`; only a boolean is printed |
| No forensic trail | Audit log with run id, UTC timestamp, actor, SHA-256 prefix of each code block, gate decision, exit code, post-condition result, state transitions and final validation |
| Dependency drift and API-confusion risk | `ag2[openai]==0.9.10` and `openai<4`. The README explains why the pin must not float |

## Test evidence

`python verify_assignment.py` needs no key and no network. Run in this repository with the
standard library only: **55 passed, 0 failed.** The behavioural rows extract and execute the
notebook's own `scan_code()`, `validate_report()` and `validate_clean_data()`, covering 17
should-fail code cases, 6 should-pass cases, 7 should-fail reports, and 8 should-fail datasets.
`test_pipeline.py` covers the speaker state machine; see the README for its recorded result.

The defect log in `RUBRIC.md` records a real run that shipped wrong revenue figures because
`discount_pct` was treated as a percentage instead of a fraction. The post-condition above exists
because of it.

## Known gaps

- **The code gate is not a sandbox.** It is a static AST check plus a scoped working directory. It
  stops the failure modes it enumerates; it is not a proof of containment. Colab offers no Docker
  daemon, so a container executor was not an option. A production deployment should run the
  executor in a container with no network namespace and keep this gate as defence in depth.
- **The local executor shells out to `python` on `PATH`**, not the notebook kernel's interpreter.
  Run it only in an environment you are comfortable letting model-written code execute in.
- **No arithmetic verification.** Neither gate re-derives the agents' numbers. A wrong figure that
  respects the schema can pass. The baseline profile in section 3 is the ground truth to check by
  hand.
- **One critic revision cycle.** Not a convergence guarantee.
- **The audit log has no integrity protection.**
- **Data leaves your machine.** Dataset excerpts and agent messages go to OpenAI. The shipped
  dataset is synthetic; do not point this at real data without reviewing what is sent.
- **No spend cap** beyond the turn and retry limits.

## Do not

- Run this on a machine where model-written code executing locally is unacceptable.
- Loosen the import allowlist or remove the URL rule without re-running the verification script.
- Replace the synthetic dataset with sensitive data.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
