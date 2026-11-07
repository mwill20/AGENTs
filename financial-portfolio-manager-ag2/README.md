# Financial Portfolio Manager (Group Chat + StateFlow, AG2)

A User Proxy Agent collects a salary and a portfolio summary and opens a group chat with a Group
Chat Manager. A **Portfolio Analysis Agent** summarises the holdings and ends with a
machine-readable `CATEGORY: Growth` or `CATEGORY: Value` line. A deterministic **StateFlow**
function reads that line and routes the chat to either the **Growth Investment Agent** or the
**Value Investment Agent**, never both. The **Investment Advisor Agent** then compiles a report with
fixed headings, which is displayed as the final output.

## Purpose

This project demonstrates **group chat collaboration** (every speaker sees the whole transcript)
and **dynamic workflow management with StateFlow** in AG2 1.x. It solves "route a conversation on
the model's own conclusion without letting the model do the routing": the Portfolio agent states a
category, plain Python parses it with a regular expression, and a state machine picks the next
speaker.

## Pattern

**Group chat + StateFlow.** AG2 1.x has no `GroupChat` / `GroupChatManager` classes (those are in
AG2 Classic, and the 1.x native equivalent is the opt-in `ag2.network` module). The notebook
rebuilds both in about sixty lines of plain Python on top of AG2 agents, keeping the AG2 Classic
`state_transition(last_speaker, groupchat)` signature. The transitions are:

```text
User Proxy -> Portfolio Analysis -> (Growth | Value) -> Investment Advisor -> None (end)
```

A missing or malformed `CATEGORY:` line falls back to Value, the conservative branch, and prints
that it did so.

## Intended audience

Learners who want to see a StateFlow-style speaker selector implemented and unit-tested without an
LLM, and who are moving from AG2 Classic to the 1.x API.

Expected background: basic Python, and comfort with Jupyter or Colab (top-level `await`, `input()`
prompts).

## What's here

| File | Purpose |
|---|---|
| `Financial_Portfolio_Manager_AG2.ipynb` | The notebook |
| `requirements.txt` | Pinned dependency, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

## Requirements

| Requirement | Notes |
|---|---|
| Python | `ag2` 1.1.2 declares `>=3.10` on PyPI. Written for Google Colab |
| Packages | `ag2[openai]==1.1.2` (AG2 1.x API, not `ag2-classic`) |
| LLM | OpenAI (**paid, pay-as-you-go**). `MODEL_CANDIDATES` are probed in order |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script |

## Quickstart (Google Colab)

1. Open `Financial_Portfolio_Manager_AG2.ipynb` in Google Colab.
2. Add `OPENAI_API_KEY` to the **Secrets** panel with **Notebook access** on. Without it, the
   notebook checks the environment variable and then asks you to paste a key (hidden, never
   printed).
3. Runtime -> Run all. Press Enter to accept the default salary, currency and portfolio summary,
   or type your own. Set `INTERACTIVE_INPUT = False` for an unattended run.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/financial-portfolio-manager-ag2
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` in your environment and open the notebook in Jupyter or VS Code.

Success looks like this: two `PASS` self-test lines, a `User_Proxy_Agent -> Group_Chat_Manager`
block, three manager rounds (`Portfolio_Analysis_Agent`, then exactly one of the two specialists
after a `[StateFlow] Portfolio category = ...` line, then `Investment_Advisor_Agent`), a
`StateFlow returned None ... conversation complete` line, a rendered report, and a check block ending in
`12/12 checks passed`.

## Settings

| Setting | Default | Notes |
|---|---|---|
| `MODEL_CANDIDATES` | `["gpt-5.4-mini", "gpt-5-mini", "gpt-4.1-mini"]` | First reachable model is used for every agent |
| `MAX_ROUND` | `6` | Safety cap on group-chat rounds. StateFlow normally ends the chat after 3 speakers |
| `INTERACTIVE_INPUT` | `True` | `False` uses `DEFAULT_INPUTS` as-is |
| `DEFAULT_INPUTS` | 95,000 USD and a six-item portfolio summary | Accepted with Enter |

## Architecture

```text
User Proxy Agent (no LLM): collect() -> validate_inputs() -> initiate_chat(manager, message)
   |
GroupChatManager.run()
   round 1  state_transition(user_proxy)      -> Portfolio_Analysis_Agent  (sees 1 message)
   round 2  state_transition(portfolio agent) -> parse_category() -> Growth_ or Value_Investment_Agent (sees 2)
   round 3  state_transition(specialist)      -> Investment_Advisor_Agent  (sees 3)
   round 4  state_transition(advisor)         -> None: stop
   |
final_report = advisor's message -> Markdown display -> 12 automated checks
```

Every speaker receives the full transcript, and each message records how many messages were
visible when it was written. Checks R10 checks that this count increases by one each round.

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for the model probe and up to `MAX_ROUND` speakers (normally three)
- Read the user's salary and portfolio summary, which the user typed themselves

This system is not allowed to:

- Use any tool, browse, run code or write files. No agent has tools
- Decide the routing. The Growth / Value branch is chosen by `parse_category` and
  `state_transition` in Python, with a unit-tested fallback
- Let both specialists speak. R5 asserts the other specialist never appears in the speaker order
- Run past `MAX_ROUND` rounds

Human approval is required for: acting on any recommendation. The report carries a disclaimer and
the notebook states it is educational, not licensed financial advice.

## Evaluation

The last cell is a twelve automated checks (R1-R12): inputs validated and should-fail cases rejected,
the User Proxy opened the chat, the manager called the Portfolio agent first, a category was
determined, StateFlow routed to the matching specialist only, the state machine self-test passed,
the specialist recommended something substantive, the advisor spoke last, StateFlow ended the chat,
every speaker saw every earlier message, and the report contains all five required headings.

| Check | Recorded result |
|---|---|
| Validation and StateFlow self-tests (cells 4 and 6) | PASS |

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limitations

- The financial content is model-generated and unreviewed. Allocations and "action plan" amounts
  are not checked against the salary or holdings.
- The portfolio summary is free text written by the user and is pasted verbatim into every prompt.
  That is fine for a single user running their own notebook; see `SECURITY.md` before exposing it to
  anyone else.
- The advisor is asked to use the specialist's recommendations but nothing verifies that the report
  table matches them.
- Non-deterministic: no seed or temperature is set.
- Needs a Jupyter-style environment because of top-level `await` and `input()`.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
