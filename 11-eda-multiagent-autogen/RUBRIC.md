# Assignment 11 — Rubric & Checklist

**Assignment:** Streamlining Exploratory Data Analysis (EDA) with a Multi-Agent System using AutoGen.

**Deliverable:** `EDA_MultiAgent_AutoGen.ipynb` — runnable end to end in Google Colab, key read from Colab Secrets.

Rows **A1–A12** are requirements taken from the assignment brief itself.
Rows **S1–S7** are the engineering / security standards applied on top of it.
Every row names *where it lives* in the notebook and *how it is proven*.

---

## Part 1 — Requirements from the assignment brief

| # | Requirement (brief wording) | Where it lives | How it is proven |
|---|---|---|---|
| A1 | "a multi-agent system built with **autogen**" | S6 `build_agents()`, S7 `GroupChat` + `GroupChatManager` | `verify_assignment.py` asserts `ag2[openai]==0.9.10` is pinned exactly and that `GroupChat` / `GroupChatManager` are constructed |
| A2 | "**Data Preparation Agent:** Handles data cleaning and preprocessing" | S6 `data_prep_agent` | Its executed script prints a before/after cleaning table and writes `cleaned_sales_data.csv` |
| A3 | "**EDA Agent:** Performs statistical summarization and generates insights and visualizations" | S6 `eda_agent` | Its executed script prints descriptive statistics and correlations, and saves at least 3 `.png` charts |
| A4 | "**Report Generator Agent:** Creates a well-structured EDA report" | S6 `report_agent` | Writes `eda_report.md`; the six required sections are defined once in S5c and used both in its prompt and in `validate_report()`, so instruction and enforcement cannot drift |
| A5 | "**Critic Agent:** Reviews outputs and provides feedback to improve clarity, accuracy, and actionability" | S6 `critic_agent` | Speaks after the first report; its findings appear in the transcript and are answered in report section 6 |
| A6 | "**Executor Agent:** Validates code and ensures the accuracy of results" | S6 `executor` (`UserProxyAgent` + `GuardedExecutor`) | Every code block is gated then run; failures are fed back and the authoring agent retries, bounded by `MAX_FIXES` |
| A7 | "**Admin Agent:** Oversees the workflow, ensures coordination, and maintains alignment with project goals" | S6 `admin`, S8 `run_eda_pipeline()` | Admin owns the task statement, starts the chat, and runs the final deterministic acceptance gate before anything is displayed |
| A8 | "these agents are interconnected in a collaborative environment where they communicate, coordinate" | S7 `GroupChat(agents=[all six])` | All six agents share one message history; `verify_assignment.py` asserts all six are in the `GroupChat` |
| A9 | "iteratively refine the analysis **based on feedback**" | S7 `select_speaker()` state machine — `report -> critic -> report` | The revision hop is a hard-coded transition, not a hope; the second report must answer the critic in section 6 |
| A10 | Final output includes "**An overview of the data**" | Report section 1, Dataset Overview | `validate_report()` hard-fails if the heading is missing |
| A11 | Final output includes "**Key insights and findings**" and "**Detailed visualizations**" | Report sections 3 and 4 | `validate_report()` hard-fails on a missing heading, or on an `![](chart.png)` reference whose file does not exist |
| A12 | Final output includes "**A summary of conclusions, incorporating feedback from the Critic Agent**" | Report sections 5 and 6 | Both headings are required; section 6 exists to carry the critic's feedback into the deliverable |

---

## Part 2 — Engineering / security standards applied

The trust boundary in this assignment is **LLM-generated code executed on the host**. That is the
control point everything below hangs off.

| # | Standard | Where it lives | How it is proven |
|---|---|---|---|
| S1 | **No hardcoded secrets.** `OPENAI_API_KEY` from Colab Secrets, then environment, then `getpass`; only a boolean is printed | S2 `load_key()` | `verify_assignment.py` scans every code cell for key-shaped literals and asserts `getpass` is present |
| S2 | **Deterministic gate ahead of the model.** No LLM-authored code runs until a static AST check passes — default-deny import allowlist, blocked call names, no shell blocks, no absolute paths, no `..`, no URLs | S5 `scan_code()` | Behavioural block in `verify_assignment.py`: should-fail cases and should-pass cases run against the notebook's own function |
| S3 | **Enforcement at the executor, not in the prompt.** `GuardedExecutor.execute_code_blocks()` refuses before `super()` is ever reached | S5 `GuardedExecutor` | Refusal returns `exit_code=1` with a fix-it message, so a blocked agent self-corrects instead of the run dying |
| S4 | **Bounded autonomy.** `timeout=90` per block, `MAX_FIXES=2` retries per stage, `max_round=30`, `human_input_mode="NEVER"`, and no agent may pick its own successor | S5, S7 | `verify_assignment.py` asserts all four bounds are present |
| S5 | **Output validation before display.** The report is checked for required sections, real chart files, the true row and column counts, and zero external URLs before it is rendered | S5c `validate_report()`, applied in S9 | S5d feeds a fabricated report (missing sections, dead image, invented URL, wrong shape) and shows the rejection - it runs before any agent does, with no API key |
| S6 | **Audit log on every consequential action** — run id, UTC timestamp, actor, code SHA-256 prefix, gate decision, exit code, every state transition | S4 `audit()`, written by S5, S7 and S8 | S11 dumps the log; `verify_assignment.py` asserts gate, exec, transition and validation events are all recorded |
| S7 | **Deterministic ground truth independent of the agents.** A plain-pandas baseline profile is computed before any agent exists, and is what the acceptance gate checks agent claims against | S3 baseline profile | The true shape is asserted to appear in the final report — an agent cannot invent the dataset size |
| S8 | **Deterministic post-condition on the cleaned data.** Every rule maps to a data-quality problem the task statement names, so it is the machine-checkable form of that contract | S5e `validate_clean_data()`, injected into `GuardedExecutor` | S5f runs 7 should-fail datasets and 1 should-pass; `verify_assignment.py` re-runs them against the notebook's own function. Added after a real run shipped wrong revenue figures - see Part 5 |

---

## Part 3 — Pre-submission checklist

Run top to bottom; each line is a yes/no.

**Runnability**
- [ ] Fresh Colab runtime, `Runtime -> Run all`, finishes with no manual edits
- [ ] Only one secret needed: `OPENAI_API_KEY` in the Colab Secrets panel with notebook access on
- [ ] `ag2[openai]` pinned to `0.9.10`; no unpinned installs, no `ag2>=1.0`
- [ ] Runtime Python is >=3.10 and <3.14; the notebook says so before pip runs
- [ ] Cells S1–S5 run with **no** API key (install, keys, data, audit, gate + self-test, report contract + self-test)
- [ ] No `use_docker` dependency — `LocalCommandLineCodeExecutor` only, because Colab has no Docker
- [ ] No `plt.show()` in agent code paths; charts are files, displayed at the end

**Assignment coverage**
- [ ] All six named agents exist with the brief's roles and distinct system messages
- [ ] Group chat transcript shows prep -> EDA -> report -> critique -> revised report
- [ ] `eda_report.md` contains sections 1 Overview, 2 Preparation, 3 Insights, 4 Visualizations, 5 Conclusions, 6 Critic Review Response
- [ ] At least 3 charts generated, referenced in section 4, and displayed inline in the notebook
- [ ] Section 6 answers the critic's actual findings from this run

**Security**
- [ ] Cleaned data passes `validate_clean_data()` before the EDA stage is allowed to start
- [ ] `discount_pct` in the cleaned file is within [0, 0.30] - it is a fraction, not a percentage
- [ ] No API key, token, or key-shaped literal anywhere in code or saved output
- [ ] Code gate blocks at least one attempted violation in the demo cell, with the reason printed
- [ ] Audit log dumped at the end and contains both `allow` and `block` decisions
- [ ] Report validation runs before the report is rendered, not after

**Honesty**
- [ ] Dataset is labelled synthetic; no claim it is real retail data
- [ ] No invented benchmarks, accuracy figures, or "production-ready" claims
- [ ] Known limitations written down in `README.md`

---

## Part 4 — Deliberate non-goals

Recorded so a reviewer does not read them as gaps.

- **No Docker executor.** Colab has no Docker daemon. The isolation story here is the deterministic
  code gate plus a scoped working directory, and that is stated plainly rather than dressed up as a
  sandbox. A real deployment would run the executor in a container with no network namespace.
- **No web search and no external data.** The brief is about EDA over a dataset. Blocking network
  access is a control, not a missing feature.
- **No AutoGen 0.4+ rewrite.** The course material and the supplied example notebooks use the 0.2
  API (`AssistantAgent`, `UserProxyAgent`, `GroupChat`). Microsoft's `autogen-agentchat` 0.4+ is a
  different, async API; AG2 1.x is a third, different API again. This assignment stays on the
  classic API via `ag2[openai]==0.9.10`, which is the same code line the course teaches and the
  only one that still installs on Colab's Python 3.13.
- **Synthetic dataset.** Generated in-notebook with a fixed seed so the run is reproducible and no
  real or licensed data is redistributed. Dirt (missing values, duplicates, case-variant categories,
  out-of-range discounts, price outliers) is injected on purpose so the Data Preparation Agent has
  genuine work.
- **`auto` speaker selection is not used.** A custom `select_speaker()` function makes the pipeline a
  state machine. That is cheaper (no extra LLM call per turn), reproducible, and keeps a
  probabilistic model out of control-flow decisions.

---

## Verification

```bash
python verify_assignment.py    # 55 checks
python test_pipeline.py        # orchestration + post-condition wiring
```

No API key and no network required. `verify_assignment.py` parses the notebook, runs the static
checks, then **extracts and executes the notebook's own** `scan_code()` and `validate_report()`
functions — so a check cannot pass against code that is not in the deliverable.
`test_pipeline.py` does the same for the orchestration: it loads the real agents and state machine
and plays scripted transcripts through `select_speaker()`, proving rows A9 and S4 behaviourally
rather than by string match.


---

## Part 5 — Defect log

Kept because a rubric that only records what went right is not evidence of anything.

### D-1 — `discount_pct` read as a percentage, not a fraction *(fixed)*

**Found:** first full Colab run, 2026-09-13. Run `4297a568` completed with `accepted: True` and
`no findings`.

**What happened.** The Data Preparation Agent wrote `discount_pct.clip(lower=0, upper=100)` and
derived revenue with `(1 - discount_pct / 100)`. The column is a fraction in `[0.0, 0.25]`.

| | Result |
|---|---|
| The 19 injected out-of-range rows (`1.5`) | survived - `clip(0, 100)` is a no-op against 1.5 |
| Mean discount applied | 0.147% |
| Mean discount intended | 12.55% |

Revenue was overstated by roughly 12.5%, and every figure and chart in section 3 and 4 of the
report inherited it.

**Why nothing caught it.** The code gate reads syntax, not data. The Critic reviews prose. The
report gate checks structure, chart existence, dataset shape and URLs - all of which legitimately
passed. This is exactly the limitation recorded in notebook section 12: *"an incorrect but
well-formed number can still pass."*

**Root cause.** A contract gap, not a model failure. The task statement named the *problem*
("out-of-range values in discount_pct") without naming the *valid range* or the units. `0.15` is
ambiguous on its face - 15% or 0.15%? The agent had to guess.

**Fix.** Both ends of the contract:
1. Section 8's task statement now declares a schema with units and a worked example
   (`0.15 means 15% off`), and states the post-condition the cleaned file must satisfy.
2. Section 5e adds `validate_clean_data()`, enforced inside `GuardedExecutor` right after a
   successful execution. A failure returns `exit_code=1` with the reasons, so it flows through the
   retry path that already existed - the agent fixes its cleaning and resends, and a bad clean
   cannot reach the EDA stage.

**Proof.** `verify_assignment.py` reproduces the exact defect against the notebook's own function
and asserts it is now rejected with `"It is a fraction, not a percentage"`.
