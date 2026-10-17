# Assignment 9 - Rubric

Requirements extracted line by line from the assignment's **Problem Statement** and **Intended
Beneficiaries** sections. Rows R1-R11 are the assignment's own words. Rows S1-S5 are the
engineering / security standards applied on top of it.

Deliverable: `Competitor_Intel_Agent.ipynb`

## Requirements taken from the problem statement

| # | Requirement (assignment wording) | Where it lives | How it is proven |
|---|---|---|---|
| R1 | "creating a **conversational** AI pipeline" - the system holds a conversation, not one-shot Q&A | Notebook S8, `SQLChatMessageHistory` + `RunnableWithMessageHistory` | S10 runs three dependent turns; turns 2 and 3 only resolve if turn 1 is remembered |
| R2 | "allows **users** to query" - plural users, each with their own thread | Notebook S8, memory keyed by `session_id` | S11 runs a second session; it is asked what it was asked first and cannot see session 1 |
| R3 | "**query** ... a report" - free-text conversational entry point | Notebook S9, `chat_with_analyst(prompt, session_id)` | Used for every turn in S10 and S11 |
| R4 | "**generate a report** on nearby clothing store competitors" | Notebook S9, `competitor_report(location, session_id)`; report format fixed in `SYS_PROMPT` | S10 Run 1 produces the six-section report |
| R5 | "**nearby clothing store** competitors" - scoped to apparel retail in one locality | Notebook S5, `search_competitors` | Tool invoked standalone in S5 before any agent exists |
| R6 | "integrates a **language model** with a **search tool**" | Notebook S6 `ChatOpenAI(model="gpt-4o", temperature=0)`; S5 two Tavily-backed tools | `verify_rubric.py` asserts both tools are bound in one `create_tool_calling_agent` call |
| R7 | "**real-time data**" - facts come from live web search, not model memory | Notebook S5, `_run_search` | Every report section must cite a URL that came back from a tool this turn |
| R8 | "including store **footfall** and **busiest times**" | Notebook S5, `get_store_traffic` | Tool invoked standalone in S5; its output carries an explicit `provenance` field |
| R9 | "giving **actionable insights** to enhance business strategies" | Notebook S6, `SYS_PROMPT` mandates a "Recommended Actions" section | Present in S10 Run 1; S10 Run 3 asks for a promotion window and gets one |
| R10 | Serves the 4 named beneficiary groups (owners, marketing, location analysts, investors) | Notebook S6, report format has one section per group | `verify_rubric.py` asserts all four section headings are in the prompt |
| R11 | Runnable in Google Colab | Notebook S1-S2: pinned installs, Colab Secrets key loader | `verify_rubric.py` parses every code cell with `ast`; no local-only paths |

## Engineering / security standards applied

| # | Standard | Where it lives | How it is proven |
|---|---|---|---|
| S1 | No hardcoded secrets - keys via Colab Secrets, then environment, then `getpass`; never printed | Notebook S2 | `verify_rubric.py` asserts `getpass` is used and no key literals appear |
| S2 | Deterministic input validation ahead of the LLM, with should-fail cases | Notebook S3, `validate_query` / `validate_location` | `test_guardrails.py` - reject and accept cases, run against the notebook's own functions |
| S3 | Memory key is validated - `session_id` addresses another user's conversation history | Notebook S3, `validate_session_id` | `test_guardrails.py` traversal and wildcard cases |
| S4 | Output validation: every URL the report cites must have come from a tool result this turn | Notebook S4, `check_report_grounding`; enforced in S9 | `test_guardrails.py` fabricated-source case |
| S5 | Bounded agent loop (`max_iterations`) and bounded tool output (snippet cap) | Notebook S5, S7 | `verify_rubric.py` |

## Data provenance - stated, not glossed over

R8 asks for footfall and busiest times. There is no free, official API that returns **measured**
footfall for a retail store. Google's "Popular Times" is not exposed by the Places API, and the
libraries that surface it scrape Google.

This deliverable therefore sources busy-hours signal from public web search - business listings,
review text, published opening hours - and every such record carries a `provenance` field marking
it `ESTIMATED`. The report is required to repeat that label. What the notebook does **not** do is
present an estimate as a measurement. See `docs` section S16 of the notebook for the full
limitation.

## Verification

```bash
python verify_rubric.py     # static: maps each rubric row to the notebook - no API keys needed
python test_guardrails.py   # behavioural: input gates + grounding check - no API keys needed
```

Both scripts read `Competitor_Intel_Agent.ipynb` directly. `test_guardrails.py` extracts and
executes the notebook's real functions rather than re-implementing them, so a test cannot pass
against code that is not in the deliverable.
