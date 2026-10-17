# Security: Assignment 10 (Logistics Optimization Crew)

A coursework CrewAI system. It runs on synthetic data inside a notebook and is not a deployed
service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Caller -> input gate | List of product names | Untrusted; resolved against a catalog before anything else |
| Gate -> agents | Canonical catalog names and a computed metrics table | Trusted: produced by the code, not the caller |
| Agents -> LLM provider | Task text, metrics, API key | Third-party processing |
| Search tool -> agents | Web results, **only if `SERPER_API_KEY` is set** | Untrusted, attacker-influenceable |
| Agents -> output gate | Strategy text | Untrusted until the gate runs |
| Run -> `AUDIT_LOG` | Run id, resolved SKUs, model, outcomes, rejected input | In-memory list in the notebook |

## Controls present in the code

| Threat | Control |
|---|---|
| Prompt injection through the product list | **Catalog resolution.** The caller's string selects a catalog entry; only the catalog's own canonical name is interpolated into the prompt. Free text has no path into the prompt. A pure-letters injection passes the character check and then fails because it resolves to nothing |
| Oversized or odd input | Maximum 12 products and 60 characters each; allowlist `^[A-Za-z0-9][A-Za-z0-9 \-/().]*$` |
| LLM arithmetic or classification errors | Turnover, days of supply, tied capital and the OVERSTOCKED / HEALTHY / UNDERSTOCKED status are computed in Python and passed as fixed facts |
| Strategy naming SKUs that were not requested | Output gate extracts every `SKU-nnnn` token from the final text and checks it against the requested set |
| Hardcoded or leaked keys | Colab Secrets, then environment, then `getpass`; never printed |
| Agent runaway and cost | `max_iter=5`, `max_execution_time=180`, `allow_delegation=False` |
| No forensic trail | Audit entries for accepted input, rejected input, model, search flag and outcome |
| Blast radius of a successful injection | The crew has no write, send or execute tool. Search, if enabled, is read-only |
| Dependency drift | `crewai==1.15.20` pinned |

## Test evidence

`python verify_assignment.py` needs no key and no network. In this repository:

- With the standard library only: 67 of 67 checks pass (the 9 CREW checks are skipped).
- With `crewai==1.15.20` installed: 76 of 76 checks pass.

It executes the notebook's own gate functions, including 12 reject cases and 6 accept cases. It
never calls `kickoff()`, so it does not show how the live agents behave.

## Known gaps

- **The output gate checks scope, not correctness.** It does not verify that recommended
  days-of-supply targets respect the lead-time floor. The task text asks for it, but a prompt
  requirement is not a control.
- **Indirect prompt injection if search is enabled.** With `SERPER_API_KEY` set, web results enter
  the agents' context. The default path avoids this by not enabling search.
- **The audit log is in memory.** It is lost when the notebook session ends, and it has no
  integrity protection.
- **Single-tenant.** One catalog, no users, no row-level access control. Multi-tenant use would need
  the catalog scoped per tenant before the gate resolves against it.
- **Synthetic data.** Nothing here is a benchmark for a real distributor.
- **Data leaves your machine.** Task text and metrics go to the LLM provider, and queries to Serper
  if search is enabled.
- **`verbose=True`** prints agent reasoning to the notebook output. Do not share outputs that
  contain anything sensitive.
- **No spend cap** beyond per-agent iteration and time limits. Live sections cost a few cents per
  the README.

## Do not

- Replace the synthetic catalog with real commercial data without scoping access and reviewing what
  is sent to the LLM provider.
- Let the strategy drive purchasing automatically. A human should approve it.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
