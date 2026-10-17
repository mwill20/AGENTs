# Assignment 10 - Rubric

Requirements extracted line by line from the assignment brief. Rows **A1-A9** are the
assignment's own words. Rows **S1-S6** are the engineering / security standards applied
on top of it.

**Deliverable:** `Logistics_Optimization_Crew.ipynb`

---

## Requirements taken from the assignment brief

| # | Requirement (assignment wording) | Where it lives | How it is proven |
|---|---|---|---|
| A1 | "Create a **Crew AI** system" | Notebook S10, `Crew(agents=..., tasks=..., process=Process.sequential)` | `verify_assignment.py` asserts a single `Crew(...)` is constructed with both agents and both tasks |
| A2 | "for **analysing logistics data**" | Notebook S3 `INVENTORY` catalog; S4 `compute_metrics()` | S4 prints the computed metric table for all 10 SKUs before any agent exists |
| A3 | "and **developing optimization strategies**" | Notebook S9 `strategy_task`; S12/S13 runs | Run output ends in a ranked action table produced by the Optimization Strategist |
| A4 | "for a **specific** logistics industry problem, such as ... **inventory management**" | Scope fixed to inventory turnover for one distributor - Notebook S0 and S3 | Every task description names inventory turnover, days of supply and stockout exposure; nothing in the notebook is generic |
| A5 | "Create **two agents**: a **Logistics Analyst** and an **Optimization Strategist**" | Notebook S8, `build_agents()` | `verify_assignment.py` asserts exactly two `Agent(...)` constructions and checks both role strings |
| A6 | "Assign a task to the **Logistics Analyst** to **research the current state of logistics operations**, focusing on **route efficiency or inventory turnover trends**" | Notebook S9, `analysis_task` -> `analyst` | Task 1 is bound to the analyst agent; its description names inventory turnover trends explicitly |
| A7 | "Assign a **second task** to the **Optimization Strategist** to create an optimization strategy **based on the insights provided by the Logistics Analyst**" | Notebook S9, `strategy_task` -> `strategist`, `context=[analysis_task]` | `verify_assignment.py` asserts `context=[analysis_task]` is present - the dependency is explicit, not just implied by ordering |
| A8 | "**Parametrize** the Tasks so it is possible to provide a **list of products** to optimize" | Notebook S9 uses `{products}` / `{metrics_table}` placeholders; S10 `run_optimization(products=[...])` | S12 and S13 run the *same* crew against two different product lists and produce different analyses |
| A9 | "Ensure each agent has a **clear goal and backstory** that aligns with their roles in logistics" | Notebook S8 | `verify_assignment.py` asserts every agent has a non-empty `role`, `goal` and `backstory`, and that each backstory is domain-specific (mentions distribution / supply chain terms) |

---

## Engineering / security standards applied

| # | Standard | Where it lives | How it is proven |
|---|---|---|---|
| S1 | **No hardcoded secrets.** Key read from Colab Secrets, then environment, then `getpass`; never printed | Notebook S2, `load_key()` | `verify_assignment.py` scans every code cell for key-shaped literals and asserts `getpass` is present |
| S2 | **Input validation at the trust boundary.** The product list is untrusted text that reaches an LLM prompt. Deterministic gate ahead of the model, with should-fail cases | Notebook S5, `validate_products()` | `verify_assignment.py` behavioural block: 9 reject cases + 4 accept cases, run against the notebook's own function |
| S3 | **Catalog resolution, not string echo.** Only canonical catalog names are interpolated into the prompt - free text never reaches the model | Notebook S5, `validate_products()` returns catalog keys | Prompt-injection string is rejected because it resolves to no catalog entry |
| S4 | **Output validation before display.** Every SKU code in the strategy must be one that was actually requested | Notebook S6, `check_strategy_scope()`; enforced in S10 | Behavioural test feeds a fabricated `SKU-9999` and asserts rejection |
| S5 | **Bounded agent loop and no delegation.** `max_iter`, `max_execution_time`, `allow_delegation=False` | Notebook S8 | `verify_assignment.py` asserts all three are set on both agents |
| S6 | **Audit log on every consequential action** - run id, timestamp, requested products, validation outcome, model, token usage | Notebook S7, `AUDIT_LOG` / `audit()`; dumped in S14 | Audit entries appear for rejected runs as well as successful ones |

---

## Deliberate non-goals

Recorded so a reviewer does not read them as gaps:

- **No web search tool.** "Research the current state of logistics operations" is read as *this
  distributor's* operations, sourced from the supplied dataset - which is what "analysing logistics
  data" in the objective line asks for. An optional `SerperDevTool` hook is included for external
  benchmark context, but it stays off unless a `SERPER_API_KEY` is present, so the notebook needs
  exactly one key to run.
- **No route optimization.** The assignment offers route efficiency *or* inventory turnover. The
  product-list parameter (A8) is an inventory axis, so the inventory branch is the coherent one.
- **Synthetic dataset.** The inventory figures are fabricated for the exercise and labelled as such
  in the notebook. No real distributor data, and no claim that the numbers are benchmarks.
- **No Flow, no memory, no planning.** Two agents, two tasks, one linear dependency. `Crew.kickoff()`
  is the right abstraction; a Flow would add state machinery this problem does not use.

---

## Verification

```bash
python verify_assignment.py
```

No API key and no network required. The script parses `Logistics_Optimization_Crew.ipynb`,
runs static checks for the structural rows, then extracts and **executes the notebook's own
validation functions** for the behavioural rows - so a check cannot pass against code that is
not in the deliverable.
