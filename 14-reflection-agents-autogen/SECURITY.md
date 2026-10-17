# Security: Assignment 14 (Reflection Agents with AutoGen)

A coursework notebook with two LLM agents and no tools. It reads no external content and takes no
action in the world. It is not a deployed service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Notebook -> OpenAI | Task text, conversation, API key (as auth header) | Third-party processing |
| OpenAI -> notebook | Drafts, critiques, reflection summary | Untrusted model output |
| Notebook -> reader | Rendered Markdown | Untrusted until a human reads it |

There is no user-supplied free text: the task is built from the `TOPIC` setting, which is a
constant in the notebook. The agents also read nothing attacker-controlled, so there is no indirect
prompt-injection surface in this build.

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Lookup order is Colab Secrets, then environment variable, then hidden `getpass`. The notebook prints only "API key loaded." |
| Empty or missing key | Raises `ValueError` before any call |
| Bad key or model name | A one-token test call runs first and fails fast with a readable message. The original error is not chained, to avoid echoing request details |
| Runaway conversation and cost | `MAX_TURNS` must be 3 or 5, and the team is built with `max_turns=MAX_TURNS` |
| Agents taking actions | Neither agent has tools. Output is text |
| Reflection altering the final draft | The final draft is taken verbatim from the Creator's last turn, not from the reflection call |
| Dependency drift and API confusion | Both AutoGen packages pinned at `0.7.5`; the notebook notes they are incompatible with legacy `pyautogen` |
| HTTP client left open | `model_client.close()` in the last cell |

## Known gaps

- **No output validation beyond structure.** The rubric checks that text exists and has the expected
  headings. Nothing checks accuracy, and nothing screens the generated Markdown.
- **Rendered Markdown.** The notebook displays model-written Markdown. Notebook frontends sanitise
  HTML, but do not share or publish outputs without reading them.
- **If `TOPIC` is ever made user-supplied,** the task text becomes an injection surface and would
  need input validation first.
- **Data leaves your machine.** The conversation goes to OpenAI.
- **No audit logging** and **no spend cap** beyond the turn limit.
- **No recorded outputs.** The notebook was saved with outputs cleared, so there is no stored
  evidence of a run in this repository.

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Add tools (code execution, web access, file writes) without a gate in front of them. That would
  change the threat model completely.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
