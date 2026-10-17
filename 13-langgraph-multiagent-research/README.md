# Assignment 13: Multi-Agent Research and Summarization System (LangGraph)

A router agent decides how each question is answered, one of three specialist agents gathers the
information, and a summarizer writes the final structured response. Built as a LangGraph
`StateGraph`.

## Purpose

This assignment demonstrates **routing** and **multi-agent composition** in LangGraph. It solves
"answer different kinds of questions from the right source" by sending each query to exactly one
specialist (the model's own knowledge, live web search, or a small knowledge base) and funnelling all
three through one summarizer so the output format is consistent.

## Architecture

```text
START -> router --+--> llm_agent ----------+
                  +--> web_research_agent -+--> summarizer -> END
                  +--> rag_agent ----------+
```

| Agent | Job |
|---|---|
| Router Agent | Picks `llm`, `web` or `rag` for the query, with a one-sentence reason. Output is a typed schema (`Literal["llm", "web", "rag"]`) |
| LLM Agent | Answers from the model's own knowledge |
| Web Research Agent | Tavily search (news topic, last week), then extracts the relevant details with source URLs |
| RAG Agent | Retrieves the top 3 documents from an in-memory vector store of a small fictional FAQ ("NovaAI") |
| Summarization Agent | Writes the final answer from the gathered information only, in a fixed Markdown format |

The knowledge base is fictional on purpose. The model cannot know these facts, so a correct answer
shows that retrieval actually worked.

## Intended audience

Learners who want a compact LangGraph example with a conditional edge, typed state, and three
different information sources behind one interface.

Expected background: basic Python, and the idea of an LLM API call.

## Project status

Prototype / coursework deliverable. The author ran the notebook and reports that it works as
expected. **The notebook was saved with its outputs cleared**, so this repository contains no
recorded run output for it, and it was not re-run during repository preparation.

## What's here

| File | Purpose |
|---|---|
| `Assignment_13_LangGraph_Multi_Agent_Research.ipynb` | The deliverable |
| `requirements.txt` | Pinned dependencies, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

The assignment brief PDF is course material and is not included in this repository.

## Requirements

| Requirement | Notes |
|---|---|
| Python | Not stated in the notebook. Written for Google Colab |
| Packages | Pinned in `requirements.txt` |
| LLM and embeddings | OpenAI: chat model `gpt-4.1-mini` and embeddings `text-embedding-3-small`. **Paid, pay-as-you-go** |
| Search | Tavily API key (free tier available) |
| Environment | Google Colab or local. Keys load from environment variables, then Colab Secrets, then a hidden `getpass` prompt |

## Quickstart (Google Colab)

1. Open `Assignment_13_LangGraph_Multi_Agent_Research.ipynb` in Google Colab.
2. Add `OPENAI_API_KEY` and `TAVILY_API_KEY` to the **Secrets** panel with **Notebook access** on,
   or just run the notebook and paste them when prompted.
3. Run all cells in order.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/13-langgraph-multiagent-research
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` and `TAVILY_API_KEY` in your environment and open the notebook. The
notebook's install cell uses `!pip` and its example cells use `IPython.display`, so run it in
Jupyter, VS Code or Colab rather than as a plain script.

Success looks like this: section 6 prints the graph as a Mermaid diagram, section 7 answers four
queries with a `route = ...` line and a structured answer, and section 8 prints `PASS` for each
route and then `All checks passed.`

## Example queries and expected routes

These are in the notebook, with the route each is expected to take.

| Query | Expected route |
|---|---|
| What is the difference between supervised and unsupervised learning? | `llm` |
| What are the biggest AI news stories from this week? | `web` |
| What is NovaAI's refund policy for annual plans? | `rag` |
| Does NovaAI support a Rust SDK? | `rag`, and the answer should say the documentation does not mention it |

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for routing, answering and summarising
- Run a Tavily search (up to 4 results, news topic, last week) when the router picks `web`
- Query an in-memory vector store of 10 documents when the router picks `rag`

This system is not allowed to:

- Write files, send messages or take any action in the world. No node does
- Follow instructions found inside web results or retrieved documents. The web and summary prompts
  tell the model to treat them as data. This is a prompt-level mitigation only

Human approval is required for: nothing today, because there are no consequential actions.

## Evaluation

The notebook's final cell contains checks that run after the four example queries:

| Check in the notebook | Recorded result |
|---|---|
| Routes are `llm`, `web`, `rag`, `rag` for the four queries | Not recorded (outputs cleared) |
| The RAG answer on annual refunds contains "30" | Not recorded |
| Every answer is non-empty | Not recorded |
| The web answer lists at least one source URL | Not recorded |
| The Rust answer says the docs do not confirm support | Not recorded |

These are four example queries with simple assertions. They are not a routing-accuracy evaluation.
Routing accuracy over a larger query set, answer quality and retrieval quality are **not yet
measured**.

## Security considerations

See [SECURITY.md](SECURITY.md). The main risk is indirect prompt injection: web pages and
retrieved text enter the model's context.

## Limitations

- The router is an LLM call. Its choice is probabilistic, so a query can be sent to the wrong
  source. Nothing checks the route afterwards.
- One route per query. A question that needs both web data and the knowledge base is answered from
  only one of them.
- The knowledge base is 10 fictional FAQ entries held in memory, rebuilt on every run, with no
  persistence and no update path.
- Web search is restricted to the news topic and the past week by the notebook's settings
  (`WEB_TOPIC`, `WEB_TIME_RANGE`). Change them for general questions.
- No conversation memory. Each query is independent.
- The summarizer is told to use only the gathered information, but nothing verifies that it did.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
