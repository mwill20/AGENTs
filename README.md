# AGENTs

Eleven coursework projects that build AI agents with different frameworks and patterns: LangChain,
LangGraph, CrewAI and AutoGen, plus one from-scratch ReAct loop. Each project is a notebook with a
README, a security note and pinned dependencies. Six also carry offline checks that need no API key.

## Purpose

These projects show how the main agent patterns work and, for each one, where the trust boundary
sits: what the model is allowed to decide, what plain Python decides instead, and what an attacker
could influence. They are learning builds with a security focus, not production systems.

## Intended audience

- Readers comparing agent frameworks on small, complete examples
- Reviewers who want to see how input validation, output checks and bounded loops were applied to
  agents

Expected background: intermediate Python, and a rough idea of how LLM APIs and tool calling work.

## Projects

| # | Folder | Framework | Pattern | What it does |
|---|---|---|---|---|
| 4 | [04-yahoo-finance-api](04-yahoo-finance-api) | FastAPI, `yfinance` | Validated data API (no LLM) | Four endpoints for company, market, historical and analysis data |
| 5 | [05-study-assistant-quiz-generator](05-study-assistant-quiz-generator) | LangChain | Prompt chain, structured output | Summarises study material and writes a quiz |
| 6 | [06-financial-image-scans](06-financial-image-scans) | LangChain, vision | Chained multimodal prompts | Reads report pages from images and summarises them for a chosen reader |
| 7 | [07-web-research-react-agent](07-web-research-react-agent) | OpenAI client, Tavily | ReAct + Planning, built from scratch | Plans questions, searches the web, writes a report |
| 8 | [08-travel-assistant-agent](08-travel-assistant-agent) | LangChain | Tool-calling agent | Weather plus attractions for a destination |
| 9 | [09-competitor-intel-agent](09-competitor-intel-agent) | LangChain | Tool use + conversational memory | Competitor analysis with an output grounding check |
| 10 | [10-logistics-optimization-crew](10-logistics-optimization-crew) | CrewAI | Two-agent sequential crew | Inventory turnover analysis and strategy |
| 11 | [11-eda-multiagent-autogen](11-eda-multiagent-autogen) | AutoGen (AG2) | Six-agent group chat with a code gate | Automated exploratory data analysis |
| 12 | [12-langgraph-math-agent](12-langgraph-math-agent) | LangGraph | Tool-calling graph | LLM decides, Python computes arithmetic |
| 13 | [13-langgraph-multiagent-research](13-langgraph-multiagent-research) | LangGraph | Router + specialist agents | Routes a query to LLM, web search or a small knowledge base |
| 14 | [14-reflection-agents-autogen](14-reflection-agents-autogen) | AutoGen | Reflection (draft, critique, revise) | Two agents refine a draft on Agentic AI |

Folder numbers follow the original assignment numbers. Assignments 1 to 3 are not part of this
repository.

## Project status

Learning builds / coursework deliverables. Each notebook was run by the author and reported to work
as expected. The table below records what was **re-checked offline while preparing this
repository** and what was not. No live API call was repeated.

| # | Offline checks re-run for this repository | Saved notebook outputs |
|---|---|---|
| 4 | None available | Present |
| 5 | None available | Present |
| 6 | None available | Present; the chart-reading output does not match the source image (see its README) |
| 7 | `test_notebook.py`: 11 of 11 pass (stub clients) | Present |
| 8 | `verify_rubric.py` 14 of 14; `test_validator.py` 20 of 20 | Present |
| 9 | `verify_rubric.py` 21 of 21; `test_guardrails.py` 54 of 54; `test_pipeline.py` 23 of 23 | Present |
| 10 | `verify_assignment.py`: 76 of 76 with `crewai` installed (67 of 67 without) | Present |
| 11 | `verify_assignment.py` 55 of 55; `test_pipeline.py` passes with `ag2` installed | Present |
| 12 | Not re-run. The author's recorded result is 25 of 25 offline checks | Present |
| 13 | None available | **Cleared** |
| 14 | None available | **Cleared** |

"Pass" here means the project's own checks pass. These checks prove control flow and guards, not the
quality of what a live model produces. Model-output quality is **not yet measured** for any of the
projects.

Two checking scripts were stale against their own notebooks and needed a small fix: 
`07-web-research-react-agent/test_notebook.py` (skipped cells by position) and
`09-competitor-intel-agent/verify_rubric.py` (matched a `!pip install` string the notebook no longer
used). In both cases the notebook was right and the check was out of date. The notebooks themselves
were not modified. Project 11's README also contradicted itself on its check count and was
corrected. Compare any folder against the `raw-import` tag to see exactly what changed.

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
cd 08-travel-assistant-agent
python verify_rubric.py
python test_validator.py
```

The `requirements.txt` files for Projects 5, 13 and 14 were written from those notebooks' own
install cells. The others came with the original assignments.

## Requirements

| Requirement | Notes |
|---|---|
| Python | Varies by project; each README states what is known. AutoGen (AG2) 0.9.10 needs `>=3.10,<3.14` |
| LLM access | Projects 5 to 14 call hosted LLM APIs, mostly OpenAI (**paid, pay-as-you-go**). Project 12 can use Groq or Google free tiers |
| Other services | Tavily (free tier) for 7, 8, 9 and 13. WeatherAPI.com (free tier) for 8. Serper (optional) for 10 |
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
- Results from live models vary between runs.

## License

MIT. See [LICENSE](LICENSE).

## Support

Open an issue on this repository. Report security problems as described in [SECURITY.md](SECURITY.md).
