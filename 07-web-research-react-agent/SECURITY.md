# Security: Assignment 7 (Web Research ReAct Agent)

A coursework agent that reads untrusted web content and passes it to an LLM. It is not a deployed
service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> agent | Research topic | Untrusted; validated |
| Agent -> LLM provider | Prompts, search results, API key (as auth header) | Third-party processing |
| Agent -> Tavily | Search queries written by the model, Tavily API key | Third-party processing |
| Tavily -> agent | Titles, URLs and text snippets from arbitrary web pages | **Untrusted, attacker-influenced** |
| LLM -> agent | `<tool_call>` JSON and answers | Untrusted model output |

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Keys read from Colab Secrets; nothing in the notebook source. The saved output prints only `Yes`/`No` for key presence |
| Model calls a tool that does not exist | `process_tool_calls` checks the name against registered tools; failure becomes an error observation |
| Model invents tool arguments | `validate_arguments` rejects any argument name the function does not declare, and coerces types |
| Malformed tool-call JSON | Caught, returned as `Tool call failed: ...`; the loop continues |
| Runaway loop and cost | `max_rounds` cap (default 4 per question), then a forced final answer |
| Bad topic input | Must be a non-empty string of 200 characters or fewer; `num_questions` must be 5 or 6 |
| Planner returns unparseable output | `plan()` raises rather than proceeding with an empty plan |
| Search errors | Returned as readable text, not a traceback |
| Indirect prompt injection from search results | The researcher prompt says to treat tool output as data and ignore instructions inside it; observations arrive as a separate conversational turn; the report prompt treats findings as data. **These are prompt-level mitigations, not guarantees** |
| Blast radius of a successful injection | The only tool is a read-only search, so an injection can corrupt report content but cannot make the agent take an action |

The control flow and these guards are exercised by the offline test (`python test_notebook.py`).
That test uses stubs, so it does not show how a real model behaves against a real injection attempt.

## Known gaps

- **Prompt injection is mitigated, not solved.** No test in this repository feeds adversarial
  search results to a real model.
- **No source credibility or deduplication.** The agent can repeat a low-quality claim with a
  citation attached.
- **No output validation beyond structure.** The report is not fact-checked against the sources.
- **Data leaves your machine.** Topics, queries and search results go to the LLM provider and to
  Tavily.
- **No audit log.** Tool calls are printed when `verbose=True` but not recorded persistently.
- **No spend cap** beyond the round limit.
- **Search-result URLs are shown as text and never fetched** by this code. A user opening a cited
  link is exposed to whatever is at that URL.
- **Unused dependency.** `python-dotenv` is pinned but not used by the notebook as submitted.

## Extending this agent

If a tool that writes, sends or deletes is ever added, the validation layer in
`process_tool_calls` and `validate_arguments` has to enforce the limits, not the prompt, and
irreversible actions need a human approval step. The notebook's own security notes say the same.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
