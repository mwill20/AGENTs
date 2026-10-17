# Assignment 7: Web Research Agent (ReAct Pattern)

An agent that takes a topic, plans 5-6 research questions, answers each one with a ReAct loop over
a Tavily web-search tool, and compiles the findings into a structured Markdown report.

## Purpose

This assignment demonstrates the **ReAct** (Thought -> Action -> Observation) loop built from
scratch, with no agent framework, and layered under a **Planning** step. It solves "research a broad
topic on the web and produce a sourced report" by splitting the work: one LLM call decomposes the
topic into searchable questions, a ReAct loop answers each question using a search tool, and one
final call writes the report with no tool access.

## Patterns

| Pattern | Where it lives | What it does |
|---|---|---|
| Planning | `WebResearchAgent.plan()` | Breaks the topic into 5-6 answerable sub-questions before any search |
| Tool Use / ReAct | `Tool`, `@tool`, `ReactAgent` | Exposes `web_search` to the model as a JSON signature; the model decides when to call it and with what arguments |

## Intended audience

Learners who want to see how a tool-calling loop works underneath a framework: how a function
becomes a JSON tool description, how tagged text becomes a control signal, and where the trust
boundary between model output and executed code sits.

Expected background: intermediate Python (classes, dataclasses, decorators), and an idea of what an
LLM API call looks like.

## Project status

Prototype / coursework deliverable. The notebook was run end to end by the author and behaved as
expected. The saved outputs come from that run. The notebook itself was **not** re-run during
repository preparation; the stub-based test described under Evaluation was.

## What's here

| File | Purpose |
|---|---|
| `Web_Research_ReAct_Agent.ipynb` | The deliverable: code, written explanation, security notes and limitations |
| `test_notebook.py` | Runs the notebook's code cells against stub LLM and Tavily clients. No network and no keys |
| `requirements.txt` | Pinned dependencies |
| `.env.example` | Placeholder variable names. See "Configuration" for how the notebook actually reads settings |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

## Requirements

| Requirement | Notes |
|---|---|
| Python | The saved install output shows Python 3.13 (Google Colab). The code uses `Tool \| list[Tool]` type syntax, which needs Python 3.10+ |
| Packages | Pinned in `requirements.txt`: `openai`, `tavily-python`, `python-dotenv` |
| LLM | Any OpenAI-compatible endpoint. Default model `gpt-4o` on OpenAI (**paid, pay-as-you-go**). Groq, Gemini and local Ollama are listed in the notebook as alternatives and were not tested here |
| Search | Tavily API key (free tier available) |
| Environment | Written for Google Colab. See "Configuration" |

## Configuration

The notebook as submitted reads keys from **Google Colab Secrets** (`google.colab.userdata`):

| Setting | Where it comes from |
|---|---|
| `LLM_API_KEY`, or `OPENAI_API_KEY` as the fallback | Colab Secret |
| `TAVILY_API_KEY` | Colab Secret |
| `LLM_BASE_URL` (optional) | Environment variable. Unset means the OpenAI default endpoint |
| `LLM_MODEL` (optional) | Environment variable. Defaults to `gpt-4o` |

Two inconsistencies in the notebook text are worth knowing about. Its markdown cell still describes
a `.env` file, but the code cells do not call `load_dotenv()`. And the notebook imports
`google.colab`, so it does not run unmodified outside Colab. To run locally you would replace the
`userdata.get(...)` calls with `os.getenv(...)`. That change is not made here.

## Quickstart (Google Colab)

1. Open `Web_Research_ReAct_Agent.ipynb` in Google Colab.
2. In the **Secrets** panel (key icon, left sidebar) add `OPENAI_API_KEY` and `TAVILY_API_KEY`, and
   turn **Notebook access** on for both.
3. Run all cells in order. The last run cell uses `TOPIC = "Climate Change"`. Change it to research
   something else.

Success looks like this: the notebook prints a plan of 6 questions, then a Thought / Action /
Observation trace for each, then renders a Markdown report with an introduction, one section per
question, and a conclusion.

### Run the offline test

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/07-web-research-react-agent
python test_notebook.py
```

This needs only the Python standard library. It never contacts an LLM or Tavily.

## Example (from the notebook's saved output)

Input: `TOPIC = "Climate Change"`

Plan produced (first two of six): "What are the primary human activities contributing to climate
change?" and "How has the average global temperature changed over the past century?"

Each question's answer is 3-6 bullet points, each ending in a source URL.

## Architecture

```text
WebResearchAgent(topic).run()
  plan()            1 LLM call  -> <questions>[...]</questions>
  research()        per question: ReactAgent.run()
                      LLM -> <thought> + <tool_call>
                      process_tool_calls() validates, then runs web_search() -> Tavily
                      observation fed back -> repeat, or <response> to finish
  compile_report()  1 LLM call, no tools -> Markdown report
```

See the notebook's own "Report" section for the component-by-component walkthrough.

## Agent safety boundaries

This agent is allowed to:

- Call one tool, `web_search`, which is read-only
- Run at most `max_rounds` (default 4) ReAct rounds per question, then be forced to answer

This agent is not allowed to:

- Execute anything other than registered tools. An unknown tool name returns an error observation
- Pass arguments the tool does not declare. Unknown argument names are rejected before the call
- Write, send or delete anything. No tool does

Human approval is required for: nothing today, because there are no consequential actions. The
notebook states that any future write, send or delete tool would need an approval step in front of
it.

## Evaluation

`test_notebook.py` executes the notebook's code cells against stubs and checks the flow plus the
should-fail paths.

| Check | Result (this repository, stub-based, no network) |
|---|---|
| All code cells compile | Pass (11 cells) |
| Plan -> research -> report runs end to end | Pass |
| One search per question; `max_results` coerced from `"3"` to `3` | Pass |
| Unknown tool name returns an error observation | Pass |
| Unknown argument name rejected | Pass |
| Malformed tool-call JSON handled | Pass |
| Planner reply without `<questions>` raises | Pass |
| Empty, whitespace, non-string and over-long topics rejected | Pass |
| Tavily failure returned as readable text | Pass |
| System prompt not mutated across repeated runs | Pass |
| Report quality and factual accuracy with a real LLM and real search | Not yet measured |

Stub tests prove the control flow and the guards. They say nothing about how good the real
reports are.

**Note on the test file.** As originally written, `test_notebook.py` skipped the first two code
cells by position. The notebook was later adapted to Colab Secrets, which added cells that import
`google.colab`, so the original test failed with `ModuleNotFoundError`. The test now skips cells by
content (`!pip` and `google.colab`). That is the only change to a code file in this folder; compare
against the `raw-import` tag to see it.

## Security considerations

See [SECURITY.md](SECURITY.md). Search results are untrusted text entering the model's context,
which makes indirect prompt injection the main risk.

## Limitations

- The report is only as good as the search snippets. `web_search` returns Tavily's content
  snippets, not full page text. Questions that need depth rather than breadth will be answered
  thinly.
- No source deduplication or credibility weighting. A claim repeated across five low-quality
  results looks the same to the agent as one from an authoritative source.
- Non-deterministic. The plan, the searches and the report will differ between runs on the same
  topic. This is a research aid, not a repeatable measurement.
- Cost scales with the plan. One planning call, up to `max_rounds` calls per question, and one
  report call: roughly 8 to 30 LLM calls per run, by the notebook's own estimate.
- Colab-only as submitted (see Configuration).

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
