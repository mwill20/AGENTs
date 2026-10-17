# Security: Assignment 8 (Travel Assistant Agent)

A coursework agent that sends user input to an LLM and reads untrusted web content. It is not a
deployed service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> `validate_destination` | Destination string | Untrusted; validated before anything else |
| Agent -> OpenAI | System prompt, query, tool results | Third-party processing |
| Agent -> WeatherAPI.com | Destination, weather API key | Third-party; **sent over plain HTTP, see below** |
| Agent -> Tavily | Query, Tavily key | Third-party processing |
| Tavily -> agent | Titles, URLs and page text from arbitrary sites | **Untrusted, attacker-influenceable** |
| LLM -> agent | Tool-call requests and the final answer | Untrusted model output |

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Keys from Colab Secrets, then environment, then `getpass`. Only `loaded` or `MISSING` is ever printed |
| Key leaking through error messages | Weather errors report the HTTP status only, never the URL, because the URL carries the key |
| URL parameter injection through the destination | The destination is passed as `params=`, not interpolated into the URL, and the allowlist rejects `?`, `&` and `=` |
| Markup or script in the destination | Character allowlist (letters including accented, spaces, `.-',`) |
| Sentence-shaped prompt injection in the destination | Maximum 5 words and 60 characters |
| Newline-smuggled instruction | Control characters rejected on the **raw** input before whitespace normalisation |
| Non-string input | Rejected with `ValueError` |
| Runaway agent loop and cost | `max_iterations=6`, `early_stopping_method="force"` |
| Hanging upstream | `timeout=10` on the weather request |
| Indirect prompt injection via search results | System prompt says to treat results as data and ignore embedded orders. Prompt-level only |
| Blast radius of a successful injection | Both tools are read-only. An injection can produce a wrong answer but cannot trigger an action |
| Dependency drift | Packages pinned in `requirements.txt` |

The validator controls are tested without keys by `test_validator.py` (20 of 20 cases pass), which
runs the notebook's own `validate_destination`.

## Known gaps

- **The weather API is called over `http://`, not `https://`** (`WEATHER_URL =
  "http://api.weatherapi.com/v1/current.json"`), and the API key travels as a query parameter. On an
  untrusted network the key and the destination can be read in transit. WeatherAPI.com may support
  HTTPS; check their documentation before changing it. The code is left as submitted.
- **The input gate is not a general injection defence.** A short injected phrase satisfies both the
  allowlist and the word cap. The real bound is that every tool is read-only.
- **No test feeds adversarial search results to a real model.** The injection controls on that path
  are untested.
- **Format-level validation only.** A fake place name passes the gate.
- **Data leaves your machine.** Destinations and search content go to OpenAI, Tavily and WeatherAPI.com.
- **Search result URLs** are included in the answer. They are never fetched by the code, but a user
  who opens one is exposed to that site.
- **No audit log** and **no spend cap** beyond the iteration limit.
- **`verbose=True`** prints tool arguments and results to the notebook output. That is fine for a
  demo; do not leave it on where output is shared.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
