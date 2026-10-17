# Assignment 14: Reflection-Based Two-Agent Conversation (AutoGen)

A Content Creator agent drafts an article on **Agentic AI**, a Content Critic agent reviews it for
language clarity and technical accuracy, and the Creator revises it. After the conversation, an LLM
"reflection" step summarises the feedback and revisions. The final draft is shown in Markdown.

## Purpose

This assignment demonstrates the **reflection** agentic pattern with AutoGen's `RoundRobinGroupChat`.
It solves "improve a draft through structured critique" by alternating two role-defined agents for
a fixed, odd number of turns, so the Creator speaks first and last and delivers the final draft.

## Pattern

**Reflection** (draft -> critique -> revise), plus a post-conversation **reflection with LLM** summary
step. With `MAX_TURNS = 5` the order is: Creator drafts, Critic evaluates, Creator revises, Critic
evaluates, Creator finalizes.

## Intended audience

Learners who want a minimal example of the AutoGen 0.4+ API: agents defined by system messages, a
round-robin team, and streaming the conversation.

Expected background: basic Python, and comfort with Jupyter or Colab (the notebook uses top-level
`await`).

## Project status

Prototype / coursework deliverable. The author ran the notebook and reports that it works as
expected. **The notebook was saved with its outputs cleared**, so this repository contains no
recorded run output for it, and it was not re-run during repository preparation.

## What's here

| File | Purpose |
|---|---|
| `Assignment_14_Reflection_Agents_AutoGen.ipynb` | The deliverable |
| `requirements.txt` | Pinned dependencies, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

## Requirements

| Requirement | Notes |
|---|---|
| Python | Not stated in the notebook. Written for Google Colab |
| Packages | `autogen-agentchat==0.7.5` and `autogen-ext[openai]==0.7.5`. These are the AutoGen 0.4+ packages and are not compatible with legacy `pyautogen` / `autogen` 0.2 |
| LLM | OpenAI (**paid, pay-as-you-go**). Default `MODEL = "gpt-5-mini"`; change the `MODEL` setting if your account uses a different model |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script: the notebook uses top-level `await` and `IPython.display` |

## Quickstart (Google Colab)

1. Open `Assignment_14_Reflection_Agents_AutoGen.ipynb` in Google Colab.
2. Add `OPENAI_API_KEY` to the **Secrets** panel with **Notebook access** on. Without it, the
   notebook checks the environment variable and then asks you to paste a key. The prompt is hidden
   and the key is never printed.
3. Run all cells in order.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/14-reflection-agents-autogen
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` in your environment and open the notebook in Jupyter or VS Code.

Success looks like this: a line saying the model is reachable, five numbered turns alternating
between `Content_Creator_Agent` and `Content_Critic_Agent`, a rendered "Final Refined Draft" and
"Conversation Reflection Summary", and a closing rubric of ten `PASS` lines ending in
`10/10 checks passed`.

## Settings

| Setting | Default | Notes |
|---|---|---|
| `MODEL` | `gpt-5-mini` | If AutoGen does not recognise the model name, the notebook supplies manual capability info and continues |
| `MAX_TURNS` | `5` | Must be 3 or 5. The notebook raises an error otherwise. Odd, so the Creator speaks last |
| `TOPIC` | `Agentic AI` | |

## Architecture

```text
TASK (topic + roles)
   -> RoundRobinGroupChat([Creator, Critic], max_turns=5)
        turn 1 Creator  draft (about 150-200 words, Markdown)
        turn 2 Critic   Language clarity / Technical accuracy / Suggested improvements
        turn 3 Creator  revise
        turn 4 Critic   evaluate again
        turn 5 Creator  final refined draft
   -> final draft = Creator's last turn, verbatim (code fence stripped if present)
   -> reflection LLM call: Feedback Received / Revisions Made / Reflection
   -> Markdown display + 10-row rubric check
```

The final draft is taken straight from the Creator's last message, so the reflection step cannot
alter it.

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for both agents and the reflection summary
- Run for exactly `MAX_TURNS` turns (3 or 5)

This system is not allowed to:

- Use tools, browse, run code or write files. Neither agent has any tool
- Run longer than the turn cap

Human approval is required for: nothing today, because the output is text only.

## Evaluation

The last cell is a ten-row rubric (R1-R10) that checks the structure of the run: two agents exist,
roles are defined by system messages, turns alternate in the expected order, the turn count is 3 or
5, the reflection summary contains its three headings, and the final draft starts with a Markdown
`#` and is longer than 200 characters.

| Check | Recorded result |
|---|---|
| Rubric R1-R10 | Not recorded (outputs cleared) |
| Whether the critique is accurate, or the revision actually better | Not yet measured |

The rubric is a structural check. It cannot tell whether the Critic's technical claims are correct
or whether the final draft is better than the first. (R5, for example, only requires the last
Creator turn to differ from the first.)

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limitations

- Output quality is whatever the model produces. Technical accuracy of the Critic's feedback is not
  verified.
- Only 3 or 5 turns, per the assignment. That is one or two revision cycles.
- The conversation is not grounded in any source. The Creator writes from model knowledge, so claims
  about Agentic AI can be stale or wrong.
- Non-deterministic: no seed or cache is set, so every run differs.
- The reflection summary is model-written and is not checked against the transcript.
- Needs a Jupyter-style environment because of top-level `await`.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
