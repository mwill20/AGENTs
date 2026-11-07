# Security Policy

## Scope

This repository holds notebooks that call hosted LLM and search APIs. It contains no
server, no deployed service and no stored user data. Each project has its own `SECURITY.md` with
its trust boundaries, controls and known gaps. This file covers the repository as a whole.

## Supported versions

| Version | Supported |
|---|---|
| `main` | Best effort |

## Secrets

- No project contains an API key. Every notebook reads keys at runtime from Colab Secrets, an
  environment variable, or a hidden `getpass` prompt, and prints at most a yes/no.
- `.env` files are ignored by `.gitignore`. `web-research-react-agent/.env.example` holds
  placeholder names only.
- Before this repository was assembled, and again when the five AG2 1.x and CrewAI projects were added, the
  notebooks, scripts and documents were scanned for common key patterns, email addresses and local
  user paths. No credentials were found. A pattern
  scan is not a guarantee. If you find a credential anywhere in the history, report it using the process
  below and **rotate it immediately**.

## Data handling

- Running a notebook sends your prompts and any text or images you supply to the API providers it
  uses (mainly OpenAI, plus Tavily, WeatherAPI.com or Serper in some projects). Do not use
  confidential or regulated data.
- `competitor-intel-agent` writes a plaintext SQLite conversation file (`competitor_memory.db`). It is ignored by
  `.gitignore`. Keep it out of commits.
- `eda-multiagent-autogen` has an LLM write Python that is executed locally behind a static code gate. The gate is
  not a sandbox. Read that project's `SECURITY.md` before running it.
- `code-analysis-correction-crewai` does the same through a `CodeInterpreterTool` that runs model-written code in a
  `python -I` subprocess with a timeout. Also not a sandbox. The code under test is a constant in the
  notebook; do not make it user-supplied without real isolation.
- The three AG2 1.x projects send personal data to the model: body measurements
  (`smart-health-assistant-ag2`), salary and holdings (`financial-portfolio-manager-ag2`), and
  receipt images (`bill-management-agent-ag2`). Use the built-in defaults and synthetic receipts unless
  you accept that. The receipt project's `my_bills/` and generated `sample_bills/` are ignored by
  `.gitignore`.
- `personalized-education-crewai` writes `education_plan.json` from validated model output. It is ignored by
  `.gitignore`. Its key cell also offers to accept pasted keys; the values are empty in this
  repository and must stay that way.

## Supply chain

Dependencies are pinned to exact versions in each project's `requirements.txt`, except where a
README explains a deliberate exception (for example, packages left to Colab's preinstalled
versions). Review a new version before changing a pin. Several of these frameworks have had
breaking API changes between minor releases.

## Responsible use

These projects are for demonstration and authorised experimentation. Do not point the web-research or
search-based agents at content or systems you are not permitted to query, and do not extend an
agent with write, send, purchase or delete tools without a human-approval step and code-level
validation in front of them.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, such as an exposed credential,
contact the maintainer through the GitHub profile at https://github.com/mwill20 rather than
posting details publicly.
