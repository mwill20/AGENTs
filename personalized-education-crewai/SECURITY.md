# Security: Personalized Education Assistant with CrewAI

A single-user notebook with three LLM agents, one pure-function tool and one local file write. As
delivered it reads no external content (web search is disabled). It is not a deployed service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Operator -> notebook | `TOPICS`, `EXPERTISE_LEVEL` (constants edited in a cell) | Operator-controlled; validated anyway |
| Notebook -> OpenAI | Task descriptions with the topics and level, prior task outputs, API key | Third-party processing |
| OpenAI -> notebook | Learning materials, quiz, projects as JSON matching Pydantic schemas | Untrusted model output |
| Project Mentor -> `ProjectSuggestionTool` | `topic`, `expertise_level` chosen by the model | Model-controlled arguments; `expertise_level` is a `Literal` |
| Notebook -> disk | `education_plan.json` | Written from validated objects |
| (If enabled) Serper -> curator | Web search results | **Untrusted external content**; disabled as delivered |

The topics are interpolated into CrewAI task descriptions with `{topics}` placeholders. The
validation forbids braces and newlines in a topic and caps count and length, which closes the
obvious template-injection and prompt-bloat routes for the one input the operator types.

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Pasted-key variables are empty in the repository; lookup is paste, then Colab Secrets, then environment, then hidden `getpass`. Only `True` / `False` is printed |
| Telemetry and trace upload | `CREWAI_TRACING_ENABLED=false`, `OTEL_SDK_DISABLED=true` |
| Bad operator input | Level must be one of three values; 1-5 topics; each at most 60 characters with no `{`, `}` or newline. Raises before any agent exists |
| Model output in the wrong shape | `output_pydantic` on every task: missing fields or wrong types fail validation |
| Model choosing project scope | `PROJECT_TEMPLATES` is a dictionary in code; the tool's `expertise_level` is a `Literal["beginner","intermediate","advanced"]`, so a made-up level is rejected by the schema |
| Runaway reasoning and cost | `max_iter` 8 / 5 / 8 per agent; `allow_delegation=False` |
| Dependency drift | `crewai[tools]==1.15.33` pinned |

## Known gaps

- **The pasted-key option is a footgun.** Section 2 lets a user type keys into a code cell. The
  values in this repository are empty strings. Anyone who fills them in and then shares or commits
  the notebook has leaked a key. Prefer Colab Secrets.
- **The run cell references an undefined `openai_key`** and fails on a fresh run. This is a
  correctness defect rather than a security one, but it means the saved outputs cannot be
  reproduced from the notebook as delivered. See the README for the one-line workaround.
- **Unverified links.** With search disabled, URLs are generated from model memory. A learner may
  be sent to a dead or wrong page. Nothing fetches or checks them.
- **If search is re-enabled**, the curator ingests web content it did not write. That content can
  carry instructions. The Pydantic schema bounds what can come back (titles, URLs, one-sentence
  reasons), but there is no content filter and no allowlist of domains.
- **Content quality is unmeasured.** Quiz answers and explanations are not checked for
  correctness.
- **No audit logging** beyond the printed results; **no spend cap** beyond `max_iter`.
- **`SERPER_API_KEY` is loaded into the environment** even though it is unused, so it is present
  in the process for the whole run.

## Do not

- Commit a notebook with keys pasted into the section 2 cell.
- Re-enable web search without deciding how to handle untrusted search results.
- Add tools that write outside the working directory or send anything without a gate.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
