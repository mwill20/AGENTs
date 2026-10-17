# Security: Assignment 4 (Yahoo Finance API)

This is a coursework demo that runs in-process in a notebook. It is not a deployed service. This
file records what the code does and does not protect against, so nobody mistakes it for
something hardened.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Caller -> API | `symbol`, `start_date`, `end_date` | Untrusted; validated before use |
| API -> Yahoo Finance (via `yfinance`) | Ticker symbol, date range | Outbound only |
| Yahoo Finance -> API | Company info, prices, history | Untrusted third-party data |

## Controls present in the code

| Threat | Control |
|---|---|
| Malformed or oversized symbol reaching the data layer | Regex `^[A-Za-z0-9.\-]{1,10}$` on every symbol, in both the path validator and the Pydantic model |
| Invalid date ranges | Pydantic validator requires `end_date` to be after `start_date`; rejected with `422` before any network call |
| Raw stack traces leaking to the caller | Bad input returns `400`/`404`/`422` with a short message |
| Secrets in the repo | None needed. Yahoo Finance access requires no key |
| LLM prompt injection | Not applicable; no model is used |

## Known gaps (not implemented)

- **No authentication or authorization.** Anyone who can reach the app can call every endpoint.
- **No rate limiting.** Repeated calls would be forwarded to Yahoo Finance and could get the
  caller's IP throttled or blocked.
- **No audit logging.** Requests are not recorded.
- **Upstream data is not schema-validated.** Missing fields from Yahoo come back as `null`.
  Unexpected values are passed through to the response.
- **Unofficial data source.** `yfinance` scrapes undocumented endpoints; there is no integrity
  guarantee on the data.
- **Date range size is unbounded.** A very long range would pull a large amount of data.

## Do not

- Expose this app on a public network as is.
- Treat the analysis output as investment advice.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
