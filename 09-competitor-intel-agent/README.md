# Assignment 9 - Competitor Intelligence Analyst

A conversational AI pipeline that lets a clothing-store owner query and generate a report on nearby
competitors, their footfall and their busiest times - integrating a language model with a web
search tool.

**Deliverable:** `Competitor_Intel_Agent.ipynb` (runnable in Google Colab)

## Agentic pattern

**Tool Use + Conversational Memory** - a LangChain tool-calling agent
(`create_tool_calling_agent` + `AgentExecutor`) wrapped in `RunnableWithMessageHistory` backed by
`SQLChatMessageHistory`.

The problem statement picks the pattern: *"conversational"* forces per-session memory, and
*"integrates a language model with a search tool"* is the Tool Use pattern by name. A ReAct loop
or a multi-agent crew would add machinery the task does not use.

## Running it

1. Open `Competitor_Intel_Agent.ipynb` in Google Colab.
2. Add two keys to the Colab **Secrets** panel (key icon, left sidebar) and enable notebook access:
   - `OPENAI_API_KEY` - https://platform.openai.com/api-keys (paid, pay-as-you-go)
   - `TAVILY_API_KEY` - https://tavily.com/#api (free tier)
3. Runtime -> Run all.

If the Secrets panel is not used, the notebook falls back to an environment variable and then to a
`getpass` prompt. No key is ever hardcoded or printed.

## Verification - none of these need API keys or network

```bash
python verify_rubric.py     # 21 static checks, one per rubric row
python test_guardrails.py   # 54 behavioural cases: input gates + grounding check
python test_pipeline.py     # 23 integration checks (needs requirements.txt installed)
```

All three read `Competitor_Intel_Agent.ipynb` and execute the notebook's own functions, so a test
cannot pass against code that is not in the deliverable.

`test_pipeline.py` runs the real LangChain `@tool` objects and the real `chat_with_analyst`
wrapper, stubbing only the Tavily network call and the agent itself. Everything between those two
stubs - validation, `SEEN_URLS` bookkeeping, provenance labelling, snippet truncation, the
grounding check - is the deliverable's code, executed.

| Suite | Result |
|---|---|
| `verify_rubric.py` | 21/21 checks passed |
| `test_guardrails.py` | 54/54 cases passed |
| `test_pipeline.py` | 23/23 checks passed |

**Not executed here:** the live agent cells (sections 10 and 11), which need both API keys and
network access. Run them in Colab.

## Files

| File | What it is |
|---|---|
| `Competitor_Intel_Agent.ipynb` | The deliverable - 44 cells, 16 sections |
| `RUBRIC.md` | Every requirement traced from the problem statement to where it lives and how it is proven |
| `verify_rubric.py` | Static rubric check |
| `test_guardrails.py` | Input gates and output grounding check |
| `test_pipeline.py` | Composed-path integration test |
| `requirements.txt` | Pinned dependencies |

## Controls in the build

| Control | Where |
|---|---|
| Secrets via Colab Secrets -> env -> `getpass`, never hardcoded, never printed | notebook S2 |
| Deterministic input gates ahead of the LLM (`validate_query`, `validate_location`) | notebook S3 |
| Memory key validated - `session_id` addresses another user's conversation | notebook S3 |
| Output gate - every cited URL must have come from a tool result on that turn | notebook S4 |
| Bounded agent loop (`max_iterations=10`) and bounded tool output (700-char snippets) | notebook S5, S7 |
| Read-only tools - the actual bound on prompt injection | notebook S5 |

## The honest limitation

The assignment asks for "store footfall and busiest times". **No free, official API returns
measured footfall for a retail store.** Google's Popular Times is not exposed through the Places
API, and the libraries that surface it scrape Google.

This system derives busy-hours signal from public web search - published hours, listing metadata,
review text - and stamps every such record `provenance: ESTIMATED`. The report is instructed to
carry the label through. Measured footfall would mean a paid provider (Placer.ai, SafeGraph) or the
store's own POS and door-counter data.

Section 16 of the notebook states this and six other limitations in full.
