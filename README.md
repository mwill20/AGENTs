# AGENTs

Sixteen small AI-agent projects, each built to exercise one pattern on one framework: LangChain,
LangGraph, CrewAI, AutoGen and AG2 1.x, plus one ReAct loop written from scratch. Each project is a
notebook with a README, a security note and pinned dependencies. Six carry offline check scripts
that need no API key; the rest embed their self-tests in the notebook.

The problem statements came from an agentic AI course I took while building these. The designs,
input gates, deterministic checks, tests and write-ups are my own, and in several projects they go
well past what was asked.

## Purpose

These projects show how the main agent patterns work and, for each one, where the trust boundary
sits: what the model is allowed to decide, what plain Python decides instead, and what an attacker
could influence. They are focused demonstrations with a security emphasis, not production systems.

## Intended audience

- Readers comparing agent frameworks on small, complete examples
- Reviewers who want to see how input validation, output checks and bounded loops were applied to
  agents

Expected background: intermediate Python, and a rough idea of how LLM APIs and tool calling work.

## Projects

### Single agent, tool use

| Folder | Framework | Pattern | What it does |
|---|---|---|---|
| [travel-assistant-agent](travel-assistant-agent) | LangChain | Tool-calling agent | Weather plus attractions for a destination, behind a deterministic input gate |
| [competitor-intel-agent](competitor-intel-agent) | LangChain | Tool use + conversational memory | Competitor analysis with an output grounding check |
| [langgraph-math-agent](langgraph-math-agent) | LangGraph | Tool-calling graph | LLM decides, Python computes arithmetic |
| [web-research-react-agent](web-research-react-agent) | OpenAI client, Tavily | ReAct + Planning, built from scratch | Plans questions, searches the web, writes a report |

### Multi-agent orchestration

| Folder | Framework | Pattern | What it does |
|---|---|---|---|
| [langgraph-multiagent-research](langgraph-multiagent-research) | LangGraph | Router + specialist agents | Routes a query to LLM, web search or a small knowledge base |
| [logistics-optimization-crew](logistics-optimization-crew) | CrewAI | Two-agent sequential crew | Inventory turnover analysis and strategy, arithmetic kept in Python |
| [personalized-education-crewai](personalized-education-crewai) | CrewAI | Sequential crew, Pydantic outputs, custom tool | Learning materials, quiz and sized project ideas |
| [code-analysis-correction-crewai](code-analysis-correction-crewai) | CrewAI | Code-executing tool + deterministic verification | Finds and fixes bugs in a function, then proves the fix |
| [eda-multiagent-autogen](eda-multiagent-autogen) | AutoGen (AG2 0.9) | Six-agent group chat with a code gate | Automated exploratory data analysis |
| [reflection-agents-autogen](reflection-agents-autogen) | AutoGen 0.7 | Reflection (draft, critique, revise) | Two agents refine a draft |
| [smart-health-assistant-ag2](smart-health-assistant-ag2) | AG2 1.x | Sequential chat + registered tool | BMI tool, diet plan and workout schedule from five validated inputs |
| [financial-portfolio-manager-ag2](financial-portfolio-manager-ag2) | AG2 1.x | Group chat + StateFlow routing | Portfolio analysis routed to a Growth or Value specialist, then a report |
| [bill-management-agent-ag2](bill-management-agent-ag2) | AG2 1.x, vision | Group chat with image input | Reads receipt images, categorises expenses, re-checks totals in Python |

### Prompting and data, no agent loop

| Folder | Framework | Pattern | What it does |
|---|---|---|---|
| [study-assistant-quiz-generator](study-assistant-quiz-generator) | LangChain | Prompt chain, structured output | Summarises study material and writes a quiz |
| [financial-image-scans](financial-image-scans) | LangChain, vision | Chained multimodal prompts | Reads report pages from images and summarises them for a chosen reader |
| [yahoo-finance-api](yahoo-finance-api) | FastAPI, `yfinance` | Validated data API (no LLM) | Four endpoints for company, market, historical and analysis data |

## Verification

Every project was run end to end by the author, submitted for independent assessment, and passed.
Six projects also ship offline check scripts that run with no API key and no network:

| Folder | Offline checks |
|---|---|
| web-research-react-agent | `test_notebook.py`: 11 of 11 (stub clients) |
| travel-assistant-agent | `verify_notebook.py` 14 of 14; `test_validator.py` 20 of 20 |
| competitor-intel-agent | `verify_notebook.py` 21 of 21; `test_guardrails.py` 54 of 54; `test_pipeline.py` 23 of 23 |
| logistics-optimization-crew | `verify_notebook.py` 76 of 76 (67 of 67 without `crewai`) |
| eda-multiagent-autogen | `verify_notebook.py` 55 of 55; `test_pipeline.py` all orchestration tests |
| langgraph-math-agent | 25 of 25 offline checks in the notebook |

The other projects carry their self-tests inside the notebook: input validation with should-fail
cases, tool self-tests, and a closing check cell with one row per requirement. "Pass" means the
project's own checks pass; they cover control flow and guards.

## Quickstart

Every project is self-contained. To try one:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/<project-folder>
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then follow that folder's README. Most notebooks are written for Google Colab and read keys from
Colab Secrets. For the projects with offline tests, run the tests first; they need no keys. For
example:

```bash
cd travel-assistant-agent
python verify_notebook.py
python test_validator.py
```

Where a notebook has an install cell, its `requirements.txt` pins the same versions.

## Requirements

| Requirement | Notes |
|---|---|
| Python | Varies by project; each README states what is known. AutoGen (AG2) 0.9.10 and CrewAI 1.15.33 need `>=3.10,<3.14`; AG2 1.1.2 needs `>=3.10` |
| LLM access | Every project except `yahoo-finance-api` calls a hosted LLM API, mostly OpenAI (**paid, pay-as-you-go**). `langgraph-math-agent` can use Groq or Google free tiers. `bill-management-agent-ag2` needs a vision-capable model |
| Other services | Tavily (free tier) for the web-research, travel, competitor and LangGraph research projects. WeatherAPI.com (free tier) for the travel assistant. Serper (optional) for the logistics crew; read but unused by the education crew |
| Environment | Google Colab for most. Local runs need small changes in a few projects, noted in their READMEs |

## Security considerations

See [SECURITY.md](SECURITY.md) for repository-level policy and each folder's `SECURITY.md` for the
project-specific trust boundaries, controls and known gaps. No project contains a credential, and
all read keys at runtime.

## Limitations

- These are small demonstrations. None has authentication, rate limiting, persistent audit logging
  or a spend cap, and none should be exposed to untrusted users as it stands.
- Prompt-injection controls that rely on prompt wording are mitigations, not guarantees. The
  stronger controls here are structural: read-only tools, input gates in plain code, and bounded
  loops.
- `eda-multiagent-autogen` and `code-analysis-correction-crewai` execute model-written Python on
  the host behind a static gate or a subprocess timeout. Neither is a sandbox. Read those two
  `SECURITY.md` files before running them.
- Results from live models vary between runs.

## License

MIT. See [LICENSE](LICENSE).

## Support

Open an issue on this repository. Report security problems as described in [SECURITY.md](SECURITY.md).
