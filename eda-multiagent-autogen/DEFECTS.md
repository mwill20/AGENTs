# Defect log: EDA Multi-Agent System

Kept because a record that only shows what went right is not evidence of anything.

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

**Proof.** `verify_notebook.py` reproduces the exact defect against the notebook's own function
and asserts it is now rejected with `"It is a fraction, not a percentage"`.
