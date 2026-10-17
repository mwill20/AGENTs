# Security: Assignment 9 (Competitor Intelligence Agent)

A coursework agent with persistent conversation memory that reads untrusted web content. It is not
a deployed service. The controls below are traced to the rubric in `RUBRIC.md`.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> gates (`validate_query`, `validate_location`, session id check) | Query, location, `session_id` | Untrusted; validated before any model call |
| Agent -> OpenAI | Prompts, search snippets, conversation history, API key | Third-party processing |
| Agent -> Tavily | Search queries, Tavily key | Third-party processing |
| Tavily -> agent | Titles, URLs, snippets from arbitrary web pages | **Untrusted, attacker-influenceable** |
| Agent <-> `competitor_memory.db` | Full conversation history keyed by `session_id` | Local file, **unencrypted** |
| LLM -> user | Report with cited URLs | Untrusted until the grounding check runs |

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Colab Secrets, then environment, then `getpass`; never printed |
| Prompt injection through the query or location | Deterministic gates: query max 300 characters; location max 60 characters and 6 words; control characters rejected on the raw input before whitespace is normalised; caller-supplied URLs rejected |
| Reading another user's conversation by guessing a `session_id` | The memory key is validated against an allowed format before it reaches the database |
| Invented sources in the report | `check_report_grounding`: every URL cited in the report must have been returned by a tool on that turn (`SEEN_URLS`). Look-alikes, such as a real URL with an appended path, count as not grounded and are flagged |
| Runaway loop and cost per turn | `max_iterations=10`; search snippets capped at 700 characters |
| Estimates presented as measurements | Footfall records are stamped `provenance: ESTIMATED` and the report is instructed to carry the label |
| Blast radius of a successful injection | Both tools are read-only |
| Dependency drift | Packages pinned in `requirements.txt` |

## Test evidence

Run in this repository, offline, with no keys:

| Suite | Result |
|---|---|
| `verify_rubric.py` | 21 of 21 |
| `test_guardrails.py` | 54 of 54 cases, including should-reject inputs and fabricated-source cases |
| `test_pipeline.py` | 23 of 23 checks, running the notebook's real tools and `chat_with_analyst` with only the Tavily call and the agent stubbed |

These prove the guards behave as designed. They do not show how a real model reacts to an
adversarial web page.

## Known gaps

- **Grounding checks the citation, not the claim.** A URL can be real and still not say what the
  report says. This needs per-claim quote checking or a human reader.
- **Conversation memory is plaintext.** `competitor_memory.db` stores user conversations in SQLite
  with no encryption, no retention limit and no ownership check beyond the session key itself. The
  file is covered by the repository `.gitignore`; keep it out of any commit.
- **No cost ceiling beyond one turn.** Nothing limits turns per session or spend per user.
- **Process-global state.** `SEEN_URLS` is module-level and cleared each turn. It is correct in a
  notebook and wrong under concurrent requests.
- **The input gate is a bound, not an injection filter.** It rejects sentence-shaped input where a
  place name belongs. It does not detect injection in general.
- **Search data is not verified.** Results skew to sites with strong SEO, and listings may be
  stale.
- **Data leaves your machine.** Queries, conversation history and search content go to OpenAI and
  Tavily.
- **Footfall is an estimate.** No free official API returns measured retail footfall. See the
  README.

## Do not

- Put real customer or business-confidential data into conversations. The memory file is
  unencrypted.
- Treat `ESTIMATED` footfall as a measurement.
- Run this behind a web server without making the per-turn state request-scoped and adding
  authentication.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
