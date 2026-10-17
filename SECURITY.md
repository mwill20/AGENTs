# Security Policy

## Scope

This repository holds coursework notebooks that call hosted LLM and search APIs. It contains no
server, no deployed service and no stored user data. Each project has its own `SECURITY.md` with
its trust boundaries, controls and known gaps. This file covers the repository as a whole.

## Supported versions

| Version | Supported |
|---|---|
| `main` | Best effort |

## Secrets

- No project contains an API key. Every notebook reads keys at runtime from Colab Secrets, an
  environment variable, or a hidden `getpass` prompt, and prints at most a yes/no.
- `.env` files are ignored by `.gitignore`. `07-web-research-react-agent/.env.example` holds
  placeholder names only.
- Before this repository was assembled, the notebooks, scripts and documents were scanned for
  common key patterns, email addresses and local user paths. No credentials were found. A pattern
  scan is not a guarantee. If you find a credential anywhere in the history, report it using the process
  below and **rotate it immediately**.

## Data handling

- Running a notebook sends your prompts and any text or images you supply to the API providers it
  uses (mainly OpenAI, plus Tavily, WeatherAPI.com or Serper in some projects). Do not use
  confidential or regulated data.
- Project 9 writes a plaintext SQLite conversation file (`competitor_memory.db`). It is ignored by
  `.gitignore`. Keep it out of commits.
- Project 11 has an LLM write Python that is executed locally behind a static code gate. The gate is
  not a sandbox. Read that project's `SECURITY.md` before running it.

## Supply chain

Dependencies are pinned to exact versions in each project's `requirements.txt`, except where a
README explains a deliberate exception (for example, packages left to Colab's preinstalled
versions). Review a new version before changing a pin. Several of these frameworks have had
breaking API changes between minor releases.

## Responsible use

These projects are for learning and authorised experimentation. Do not point the web-research or
search-based agents at content or systems you are not permitted to query, and do not extend an
agent with write, send, purchase or delete tools without a human-approval step and code-level
validation in front of them.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, such as an exposed credential,
contact the maintainer through the GitHub profile at https://github.com/mwill20 rather than
posting details publicly.
