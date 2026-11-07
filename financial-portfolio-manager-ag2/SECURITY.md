# Security: Financial Portfolio Manager with AG2

A single-user notebook with one user and four LLM agents, none of which has a tool. It reads no
external content, writes no files and takes no action in the world. It is not a deployed service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> notebook | Salary, currency, free-text portfolio summary | Untrusted until validated; the summary stays free text |
| Notebook -> OpenAI | The transcript (user data plus every earlier agent reply), API key (as auth header) | Third-party processing of **personal financial data** |
| OpenAI -> notebook | Analysis with `CATEGORY:` line, recommendations, report | Untrusted model output |
| Portfolio agent reply -> `state_transition` | The `CATEGORY:` line | Model output used as a routing signal, parsed by exact regex |
| Notebook -> reader | Rendered Markdown report | Untrusted until a human reads it |

The portfolio summary is the one free-text input. It is normalised and bounded to 10-2000
characters, but its content is not inspected, so whatever the user types is pasted into every
prompt. In this single-user notebook the user is the only person who can write it.

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Colab Secrets, then environment variable, then hidden `getpass`; only "API key loaded." is printed. Provider errors are reduced to their type name |
| Bad numeric input | `validate_inputs`: salary parsed with commas stripped, bounded 1,000-100,000,000; currency must be three letters; summary length bounded. Four should-fail cases asserted |
| Model deciding the workflow | Routing is `parse_category` (regex `CATEGORY:\s*(Growth|Value)`) plus `state_transition`, both plain Python, unit-tested for seven transitions without an LLM |
| Missing or malformed category | Falls back to Value (conservative) and prints that it did |
| Unexpected speaker | `state_transition` raises `ValueError` for any speaker it has no rule for |
| Runaway conversation and cost | `MAX_ROUND = 6` cap in `GroupChatManager.run`; StateFlow normally ends after three speakers |
| Agents taking actions | No agent has tools; output is text |
| Unstructured report | The advisor prompt fixes five headings; R11 checks all five are present and the chosen category is named |
| Dependency drift | `ag2[openai]==1.1.2` pinned |

## Known gaps

- **Financial data leaves your machine.** Salary and holdings go to OpenAI in every round. Do not
  use real account numbers or anyone else's data.
- **The portfolio summary is a prompt-injection surface** if this notebook is ever adapted so that
  someone other than the operator supplies it. Text in the summary could instruct the Portfolio
  agent to emit `CATEGORY: Growth` or steer the advisor. The structural controls (regex routing,
  fixed headings, no tools) bound the effect to a biased text report, but there is no content
  filter today.
- **No grounding check.** Nothing verifies that the advisor's table matches the specialist's
  recommendations, or that amounts in the action plan are consistent with the salary.
- **The category rule is applied by the model.** The Growth / Value definitions live in the
  Portfolio agent's prompt; Python only reads the answer. A wrong classification is routed
  faithfully.
- **Rendered Markdown** from the model is displayed; read before publishing.
- **No audit logging** beyond the printed transcript, and **no spend cap** beyond `MAX_ROUND`.

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Treat the report as financial advice. The notebook says so, and so does the report's disclaimer.
- Add tools (brokerage APIs, payments, file writes) without a code-level gate and a human step.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
