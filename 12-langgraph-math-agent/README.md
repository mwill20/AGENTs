# Assignment 12 — A LangGraph Agent with LLM Reasoning and Custom Math Tools

A single agent that answers general questions with an LLM and, when asked to do arithmetic, calls
one of four predefined Python functions (`plus`, `subtract`, `multiply`, `divide`) instead.

**Deliverable:** [`LangGraph_Math_Agent.ipynb`](LangGraph_Math_Agent.ipynb) — runs top-to-bottom in
Google Colab.

---

## The design in one line

**The LLM decides. Python computes.**

The model classifies the query and extracts the operands; a plain Python function produces the
number; the model writes the sentence around it. The model never does the arithmetic, so the
answer's correctness does not depend on a probabilistic system getting a token right.

```
                    +-------------------------------+
                    |                               |
                    v                               |
   START ---> +-----------+  tools_condition    +---+---+
              |  chatbot  | ---------+--------> | tools |
              |   (LLM)   |          |          +-------+
              +-----------+          |          feedback edge: the tool
                                     |          result returns to the LLM
                                     +-------->  END
                                    (no tool call needed)
```

One conditional edge handles all routing. A reply carrying `tool_calls` goes to the `tools` node; a
reply without one ends the run. The edge back from `tools` to `chatbot` is what turns a bare `96`
into *"12 times 8 is 96"*, and what lets a chained expression like `(5+3)*2` resolve in two hops.

## How to run it

### Google Colab (recommended)

1. Upload `LangGraph_Math_Agent.ipynb`, or open it from Drive.
2. Open the **Secrets** panel (key icon, left sidebar) and add **one** of:
   - `GROQ_API_KEY` — free tier, [console.groq.com](https://console.groq.com)
   - `GOOGLE_API_KEY` — free tier, [aistudio.google.com](https://aistudio.google.com/app/apikey)
   - `OPENAI_API_KEY` — paid
3. Turn **Notebook access** on for that secret.
4. **Runtime → Run all.**

Section 1 detects whichever key is present and configures that provider automatically. **An
assessor can supply their own key from any of the three vendors without editing a line.** To force a
specific vendor, set `PROVIDER` in section 1 to `"groq"`, `"google"`, or `"openai"`.

Expected wall time is about a minute, and a fraction of a cent on the default models.

### Locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY=...        # or GOOGLE_API_KEY / OPENAI_API_KEY
jupyter notebook LangGraph_Math_Agent.ipynb
```

Outside Colab the key loader falls back to an environment variable, then to a `getpass` prompt that
does not echo. Nothing is hardcoded and no key is ever printed — only a boolean.

## Requirement coverage

| # | Requirement from the brief | Where | Verified by |
|---|---|---|---|
| R1 | Use an LLM API (Groq / Gemini) or a local LLM | §1–2, §5 | Runs against Groq, Google or OpenAI |
| R2 | Four custom functions; `divide` handles division by zero | §3 | 12 checks in §9a, incl. 5 should-fail cases |
| R3 | A math query calls the corresponding function | §6–7 | 3 offline + 8 live checks |
| R4 | A non-math query is forwarded to the LLM | §6–7 | 2 offline + 2 live checks |
| R5 | Graph building, tool integration, graph flow | §5–6 | 4 structural checks + a chained-expression test |
| D1 | Report: how the LLM is used, how the agent works | §10a | — |
| D2 | Report: explanation of code and flow | §10b | — |

## Tests

Section 9 of the notebook is the verification, split in two:

- **§9a runs with no API key at all.** A scripted stand-in replays fixed LLM replies, so the graph,
  the routing, the tools and the model fallback are exercised with nothing probabilistic in the loop. **25 checks.**
- **§9b needs a key**, because it tests the part that genuinely requires a model: whether a real LLM
  reading a real question picks the right tool and the right operands. Assertions are tolerant about
  wording, strict about which tool ran and what number it returned.

Every check names the requirement it traces to. The should-fail cases — division by zero, a
non-finite operand, an out-of-range magnitude, a non-numeric operand — are the ones that matter;
happy paths are easy.

**Status:** §9a — 25/25 passing, executed against `langgraph 1.2.11` / `langchain-core 1.6.3` on
Python 3.12. §9b requires a key and has not been executed in this environment; run it to confirm.

## Security notes

| Control | Where | Why |
|---|---|---|
| No hardcoded secrets | §1 | Colab Secrets → env var → no-echo prompt; only a boolean printed |
| Input validation at the tool boundary | §3 | Tool arguments are LLM-generated JSON — untrusted input entering code execution |
| Two validation layers | §3 | Pydantic rejects non-numeric input but **accepts `nan` and `inf`**; `validate_operands` closes that gap and bounds magnitude |
| Deterministic computation | §3 | The checkable result comes from Python, never from the probabilistic component |
| Fail closed, not silent | §3, §6 | Tools return explicit `ERROR:` strings; the system prompt forbids substituting a number |
| Audit logging | §3, §8 | Actor, timestamp, input and output for every tool invocation |
| Bounded autonomy | §6 | Four tools only; `recursion_limit=12` caps the hops per query |
| Pinned dependencies | §2 | Reproducibility, and a defence against dependency substitution |

Full discussion, including the prompt-injection surface, is in §10c of the notebook and in
[SECURITY.md](SECURITY.md).

## Two implementation details worth knowing

**A tool must return its errors, never raise them.** LangGraph catches *schema* violations and hands
the LLM a readable error message, but an exception raised inside a tool body propagates out of
`graph.invoke()` and terminates the whole run. This was verified directly, and it is why `divide`
returns an `ERROR:` string rather than raising `ZeroDivisionError`.

**Pydantic's `float` accepts `nan` and `inf`.** `{"a": "inf"}` from the model passes type validation
untouched. Type coercion is not input validation — hence the second layer.

## Limitations

Stated in full in §11 of the notebook. The short version: two operands per call (longer expressions
need chaining), routing is probabilistic so tool use is reliable rather than guaranteed, float
arithmetic rather than `Decimal`, operands capped at 1e12, no memory across separate calls, and no
rate limiting.

**Model IDs have a shelf life.** Defaults (checked 2026-09-19): Groq `openai/gpt-oss-120b`, Google
`gemini-3.6-flash`, OpenAI `gpt-4o-mini`. The originals — `llama-3.3-70b-versatile` (shut down
2026-08-16) and `gemini-2.0-flash` (shut down 2026-06-01) — were retired. If you hit
"model not found", the notebook now falls back automatically to the next listed model (section 5). If every candidate is retired, add a Colab secret named **`LLM_MODEL`** with a current ID; no code edit needed.
Check each vendor's *deprecations* page, not its models page — Groq's models page still listed
`llama-3.3-70b-versatile` after its shutdown.

## Files

```
Assignment 12/
├── LangGraph_Math_Agent.ipynb   # the deliverable
├── README.md
├── SECURITY.md
├── requirements.txt
└── Assignment_Building Advanced AI Agents with LangGraph.pdf
```
