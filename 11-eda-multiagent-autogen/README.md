# Assignment 11 — Streamlining EDA with a Multi-Agent System (AutoGen)

Six AutoGen agents collaborate to take a messy dataset from raw CSV to a finished,
critic-reviewed EDA report — with a deterministic security gate in front of every line of code
the agents write.

## Purpose

This assignment demonstrates a multi-agent AutoGen workflow in which an LLM writes Python and the
notebook runs it, and shows what it takes to do that safely. It solves "take a messy dataset to a
critic-reviewed EDA report" with six agents, a turn order decided by plain Python instead of an LLM,
a static code gate in front of the executor, and output and data validators behind it.

## Intended audience

Learners and reviewers interested in agentic code execution, AutoGen's group chat, and how to bound
an agent that writes code.

Expected background: intermediate Python, pandas basics, and an OpenAI API key.

## Project status

Prototype / coursework deliverable. The notebook was run end to end by the author and behaved as
expected. During repository preparation, `verify_assignment.py` and `test_pipeline.py` were re-run
(see Verification); the six-agent LLM run was **not** repeated.

## Requirements

| Requirement | Notes |
|---|---|
| Python | `>=3.10,<3.14` (the `ag2` 0.9.10 constraint). Colab currently runs 3.13 |
| Packages | `ag2[openai]==0.9.10` and `openai<4` pinned in `requirements.txt`; pandas, numpy and matplotlib are left to Colab's preinstalled versions |
| LLM | OpenAI (**paid, pay-as-you-go**), `gpt-4o-mini` |
| Data | A synthetic dataset generated inside the notebook with a fixed seed. No external dataset |
| Environment | Google Colab. Running locally needs `python` on `PATH` to have pandas and matplotlib |

| File | What it is |
|---|---|
| `EDA_MultiAgent_AutoGen.ipynb` | **The deliverable.** Runs end to end in Google Colab. |
| `RUBRIC.md` | Requirement-by-requirement rubric and the pre-submission checklist |
| `verify_assignment.py` | 55 automated checks against the rubric. No API key, no network |
| `test_pipeline.py` | Behavioural test of the orchestration state machine. No API key, no model call |
| `requirements.txt` | Pinned dependency, with the reasoning for the pin |

---

## Quickstart (Google Colab)

1. Upload `EDA_MultiAgent_AutoGen.ipynb` to Colab.
2. Open the **Secrets** panel — the key icon in the left sidebar.
3. Add a secret named `OPENAI_API_KEY` and toggle **Notebook access** on.
4. `Runtime → Run all`.

Nothing else to edit. Expect a few minutes of wall time and a few cents on `gpt-4o-mini`.

**Running it locally instead?** The key loader falls back to the `OPENAI_API_KEY` environment
variable, then to a `getpass` prompt that does not echo. One caveat: AutoGen's
`LocalCommandLineCodeExecutor` shells out to `python` from `PATH`, not to the kernel's own
interpreter. In Colab those are the same; in a local venv they may not be, and agent code will then
fail on missing packages. Run the notebook from an environment where `python` on `PATH` has pandas
and matplotlib.

---

## The agents

| Agent | Type | Responsibility |
|---|---|---|
| `Admin` | `UserProxyAgent` | Owns the task statement, starts the run, runs the final acceptance gate |
| `Data_Preparation_Agent` | `AssistantAgent` | Data cleaning and preprocessing |
| `EDA_Agent` | `AssistantAgent` | Statistical summarisation, insights, visualisations |
| `Report_Generator_Agent` | `AssistantAgent` | Writes the structured EDA report |
| `Critic_Agent` | `AssistantAgent` | Reviews for clarity, accuracy, actionability. Writes no code |
| `Executor` | `UserProxyAgent` + `GuardedExecutor` | Gates and runs every code block, reports the result back |

All six share one `GroupChat`. Turn order is decided by a plain Python function, not by a model:

```
Admin -> Prep   -> Executor --+
         EDA    -> Executor --+--> exitcode != 0 : back to the same author (max 2 fixes)
         Report -> Executor --+
                               \
                                -> Critic -> Report -> Executor -> done
```

AutoGen's default `speaker_selection_method="auto"` asks an LLM who talks next. That costs a call
per turn, is not reproducible, and puts a probabilistic model in charge of control flow. A state
machine is cheaper, deterministic, and makes the critic revision hop a *guarantee* rather than a
hope — which is exactly what the assignment's "iteratively refine the analysis based on feedback"
asks for.

---

## The security design

The trust boundary is **an LLM writes Python and this notebook runs it on the host.** Everything
below hangs off that one fact.

**1. A deterministic gate ahead of the model.** `scan_code()` parses every block with `ast` and
applies default-deny rules before execution:

- Python only, one block per message — shell blocks, `!pip`, and `%magic` are refused
- Import **allowlist** (pandas, numpy, matplotlib, seaborn, and 11 stdlib modules). `os`,
  `subprocess`, `socket`, `requests`, `shutil`, `pickle` are simply not on it
- Blocked call names: `eval`, `exec`, `compile`, `__import__`, `getattr`, `globals`, `locals`
- Relative paths only — no absolute path, no `..`
- No `http://`, `https://`, `ftp://`, `file://` string literals anywhere — no network at all
- 20,000 character cap per block

**2. Enforced at the executor, not in the prompt.** The same policy appears in the agents' system
messages, but `GuardedExecutor.execute_code_blocks()` refuses a violating block *before*
`super()` is reached. The prompt makes compliance likely; the gate makes it true. A refusal comes
back as `exit_code=1` with a fix-it message, so the agent self-corrects rather than the run dying.

**3. Bounded autonomy.** 90s per block, 2 retries per stage, 30 turns maximum,
`human_input_mode="NEVER"` so nothing blocks on a console prompt, and `is_termination_msg` forced
to `False` so no agent can end the run by emitting a magic word.

**4. Output validation before display.** The report is untrusted model output until
`validate_report()` passes it. Critical findings block acceptance: a missing section, fewer than
three embedded charts, a chart reference pointing at a file that does not exist, any external URL,
or a dataset shape that does not match the baseline profile computed *before any agent existed*.
The URL rule matters: this analysis is entirely local, so a link is either a hallucinated citation
or an exfiltration path.

**5. A deterministic post-condition on the cleaned data.** `validate_clean_data()` runs inside
`GuardedExecutor` immediately after a successful execution: required columns present, no duplicates
left, no nulls in the numeric columns, `discount_pct` within `[0, 0.30]` (it is a fraction, not a
percentage), `unit_price > 0`, no unparsed date strings, and a row count between half and all of the
original. A failure is returned to the agent as `exit_code=1` with the reasons, so it flows through
the retry path that already existed — the agent fixes its cleaning and resends. Every rule maps to a
data-quality problem the task statement names, so this is the machine-checkable form of that
contract rather than a new opinion. It exists because a real run shipped wrong revenue figures —
see the defect log in `RUBRIC.md`.

**6. No hardcoded secrets.** Colab Secrets → environment → `getpass`. Only a boolean is printed.

**7. Audit log on every consequential action.** Run id, UTC timestamp, actor, SHA-256 prefix of
each code block, gate decision, exit code, post-condition outcome, every state transition, and the
final validation. Dumped in section 11.

---

## Verification

```bash
python verify_assignment.py
```

55 checks, no API key and no network required. The structural rows are checked by parsing the
notebook. The behavioural rows **extract and execute the notebook's own** `scan_code()` and
`validate_report()` and `validate_clean_data()` — 17 should-fail code cases, 6 should-pass cases,
7 should-fail reports and one should-pass, 8 should-fail datasets and one should-pass — so a check
cannot pass against code that is not in the deliverable.

Then the orchestration, which a static check cannot prove:

```bash
python test_pipeline.py
```

This loads the notebook's real agents and state machine and plays scripted transcripts through
`select_speaker()` — the happy path with a retry, a should-fail path where a stage never succeeds,
and a check that the critic is never routed to the executor. It needs `autogen` installed but
makes no model call.

Status recorded by the author: **45 verification checks passed, 0 failed. All orchestration tests passed**, run on Python 3.13.5 with `ag2==0.9.10`, the same Python major/minor Colab uses. That figure predates later additions; `verify_assignment.py` now has 55 checks.

### Re-run during repository preparation

| Script | Environment | Result |
|---|---|---|
| `verify_assignment.py` | Python 3.12, standard library only | 55 passed, 0 failed |
| `test_pipeline.py` | Python 3.12, fresh virtualenv, `ag2[openai]==0.9.10`, `openai` 3.33.0, no API key, no model call | All orchestration tests passed |

Python 3.12 is inside the `>=3.10,<3.14` range that `ag2` 0.9.10 supports. The six-agent LLM run was
not repeated.

---

## What was tested, and what was not

**Verified by running it, on Python 3.13.5 — the same major/minor Colab runs:**
- A clean-room install of the notebook's exact pin (`ag2[openai]==0.9.10` + `openai<4`) into a
  fresh 3.13 virtualenv, then importing the full classic API off it
- Every code cell parses; the no-API-key path (install, keys, dataset, gate, gate self-test, report
  contract, validator self-test) executes cleanly
- The speaker state machine, played through a scripted happy path with a retry and through a
  should-fail path where a stage never succeeds — the run aborts with a reason instead of looping
- `GuardedExecutor` refusing `import os; os.system(...)` before execution
- Realistic pandas cleaning code passing the gate and running correctly (1235 → 1200 rows after
  dedupe, `region` and `returned` normalised)
- The report validator accepting a well-formed report and rejecting seven malformed ones
- The data post-condition: incomplete cleaning returns `exit_code=1` naming the out-of-range
  discounts and the remaining nulls; correct cleaning returns `exit_code=0`. Eight should-fail
  datasets rejected, one should-pass accepted

**Not executed locally:** the full six-agent LLM run, which needs an API key. Chart generation was
checked at the gate rather than by execution, because the interpreter this machine's executor shells
out to has no matplotlib. Colab ships matplotlib, so the agents produce charts there.

---

## Limitations

- **The dataset is synthetic.** Generated in section 3 with a fixed seed, deliberately dirty so the
  Data Preparation Agent has real work. The report describes that generated data and nothing else —
  no real retail data, no benchmark claims.
- **The code gate is not a sandbox.** It is a static AST check over a scoped working directory. It
  stops the failure modes it enumerates; it is not a proof of containment. Colab offers no Docker
  daemon, so `DockerCommandLineCodeExecutor` was not an option. A production deployment would run
  the executor in a container with no network namespace and keep this gate as defence in depth.
- **The report is model-written prose.** The report gate checks structure, chart existence, the true
  dataset shape, and the absence of URLs. The data post-condition now constrains the *inputs* to the
  analysis, but neither gate re-derives the agents' arithmetic — a wrong number that respects the
  schema can still pass. The baseline profile in section 3 is the ground truth to check by hand.
  This is not hypothetical: see the defect log in `RUBRIC.md` for one that shipped.
- **One revision cycle.** The critic speaks once and the report is rewritten once. Enough to
  demonstrate feedback-driven refinement; not a convergence guarantee.
- **Dependency pinning.** `ag2[openai]` is pinned exactly at `0.9.10`. Three mutually incompatible
  APIs share the AutoGen name: the classic 0.2 API (what the course teaches, continued by AG2 0.x),
  Microsoft's async `autogen-agentchat` 0.4+, and AG2 1.x. Floating this pin in either direction
  breaks the notebook. pandas, numpy and matplotlib are deliberately left to Colab's preinstalled
  versions — forcing a reinstall there destabilises the runtime for no benefit.
- **Python range.** ag2 0.9.10 supports `>=3.10,<3.14`. The notebook checks the runtime version
  before pip runs and says what to do if Colab moves past 3.13.
- **Reproducibility.** `temperature=0` and `cache_seed=42` make re-runs cheap and close to
  deterministic, but LLM output is never byte-identical across model versions.

---

## Security considerations

See [SECURITY.md](SECURITY.md). The "security design" section above is the detailed explanation.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
