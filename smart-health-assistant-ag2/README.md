# Smart Health Assistant (Sequential Conversation, AG2)

A User Proxy Agent collects five facts about the user (weight, height, age, gender, dietary
preference) and hands them, in a fixed order, to three LLM agents: a **BMI Agent** that must call a
registered BMI tool, a **Diet Planner Agent**, and a **Workout Scheduler Agent**. Each agent's reply
is carried forward into the next message. The result is one Markdown health plan: BMI insights, a
one-day meal plan and a seven-day workout schedule.

## Purpose

This project demonstrates the **sequential conversation** pattern and **tool registration** in
AG2 1.x. It solves "turn a few personal measurements into a coherent plan" by keeping the
arithmetic (BMI) and all input checks in plain Python, and asking the models only for the parts a
rule cannot write: categorisation wording, meals and exercises.

## Pattern

**Sequential chat.** The User Proxy Agent (no LLM) is the sender of every message. It calls
`initiate_chat` on the BMI Agent, then the Diet Planner, then the Workout Scheduler, pasting the
previous reply into the next prompt. This mirrors AG2 Classic's `initiate_chats([...])`, rebuilt on
the AG2 1.x `Agent` / `tool` API. The notebook's opening table maps each AG2 Classic concept
(`UserProxyAgent`, `AssistantAgent`, `register_for_llm`) to its 1.x equivalent.

## Intended audience

Developers moving from the AG2 Classic (`autogen.*`) API to the AG2 1.x API, who want a small
example of a registered tool, a sequential hand-off and a check cell that proves the tool was really
called.

Expected background: basic Python, and comfort with Jupyter or Colab (the notebook uses top-level
`await` and `input()` prompts).

## Project status

Prototype. The author ran the notebook and reports that it works as
expected. **The notebook was saved with its outputs cleared**, so this repository holds no recorded
run output, and the live cells were not re-run during repository preparation.

What **was** re-checked offline while preparing this repository, with no API key and `ag2`
replaced by a stub: the notebook's own self-tests in cells 4 and 5 were extracted and executed.
`validate_profile` accepted a valid profile and rejected all four should-fail cases; `calculate_bmi`
matched the three known values and rejected all four non-positive inputs. Both printed `PASS`.

## What's here

| File | Purpose |
|---|---|
| `Smart_Health_Assistant_AG2.ipynb` | The notebook |
| `requirements.txt` | Pinned dependency, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

## Requirements

| Requirement | Notes |
|---|---|
| Python | `ag2` 1.1.2 declares `>=3.10` on PyPI. Written for Google Colab |
| Packages | `ag2[openai]==1.1.2`. This is the AG2 1.x API and is **not** the `autogen` / `ag2-classic` API used in the AG2 Classic examples |
| LLM | OpenAI (**paid, pay-as-you-go**). The notebook probes `MODEL_CANDIDATES` in order and uses the first model your key can reach |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script: top-level `await`, `input()` prompts and `IPython.display` |

## Quickstart (Google Colab)

1. Open `Smart_Health_Assistant_AG2.ipynb` in Google Colab.
2. Add `OPENAI_API_KEY` to the **Secrets** panel with **Notebook access** on. Without it, the
   notebook checks the environment variable and then asks you to paste a key. The prompt is hidden
   and the key is never printed.
3. Runtime -> Run all. In the data-collection cell, press Enter to accept each default or type
   your own value. Set `INTERACTIVE_INPUT = False` for an unattended run.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/smart-health-assistant-ag2
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` in your environment and open the notebook in Jupyter or VS Code.

Success looks like this: a line naming the reachable model, two `PASS` self-test lines, three
transcript blocks (`User_Proxy_Agent -> BMI_Agent` with a `>>> BMI_Agent called tool calculate_bmi`
line, then the Diet Planner, then the Workout Scheduler), a rendered health plan, and a closing
check block ending in `12/12 checks passed`.

## Settings

| Setting | Default | Notes |
|---|---|---|
| `MODEL_CANDIDATES` | `["gpt-5.4-mini", "gpt-5-mini", "gpt-4.1-mini"]` | Tried in order with a one-word probe; the first that answers is used for every agent |
| `INTERACTIVE_INPUT` | `True` | `False` skips the prompts and uses `DEFAULT_PROFILE` |
| `DEFAULT_PROFILE` | 82 kg, 175 cm, 34, Male, Veg | Accepted with Enter |

## Architecture

```text
User Proxy Agent (no LLM)
   collect() -> validate_profile() -> UserProfile
   |
   |-- initiate_chat(BMI Agent, weight + height)
   |        BMI Agent --calls--> calculate_bmi (plain Python) --> BMI, category, recommendations
   |
   |-- initiate_chat(Diet Planner, BMI insights + dietary preference) --> one-day meal plan
   |
   |-- initiate_chat(Workout Scheduler, meal plan + age + gender) --> 7-day schedule
   |
   `-- final_plan (Markdown) + 12 automated checks
```

`initiate_chat` also walks the reply's event history, prints every `ToolCallEvent` /
`ToolResultEvent`, and stores them in `chat_log`. The check cell later compares the tool's returned BMI
with an independent recomputation from the profile, so a model that skipped the tool and guessed
would fail R6.

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for the model probe and the three agents (four or more calls per run)
- Call `calculate_bmi`, and only from the BMI Agent

This system is not allowed to:

- Browse, run arbitrary code or write files. The only tool is the BMI function
- Use the BMI tool from the Diet Planner or Workout Scheduler. Both are created with no tools, and
  check R5 checks that
- Accept out-of-range or unknown values. `validate_profile` rejects them before any model call

Human approval is required for: acting on the plan. The output is text, and the BMI Agent's prompt
states that it is general wellness guidance, not a medical diagnosis.

## Evaluation

The last cell is a twelve automated checks (R1-R12) that checks the sequence of recipients, the
validated profile, both should-fail self-tests, tool registration, that the tool's BMI value was
used in the reply, that each downstream message contains the previous output plus the right
profile fields, and that the final plan embeds all three replies.

| Check | Recorded result |
|---|---|
| Validation and BMI tool self-tests (cells 4 and 5) | PASS, re-run offline for this repository |
| Checks R1-R12 against a live run | Not recorded (outputs cleared) |
| Whether the diet really respects the preference, or the workouts suit the user | Not yet measured |

The checks are structural. R9 only requires that meal names and the preference word appear; it
cannot tell whether a "Veg" plan is actually meat-free.

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limitations

- Health content comes from the model and is not reviewed by anyone qualified. The BMI formula is
  exact; everything after it is advice-shaped text.
- Diet and workout constraints are enforced by prompt wording only. Nothing checks the meal plan
  against the dietary preference or the schedule against the user's age.
- Non-deterministic: no seed or temperature is set, so every run differs.
- Needs a Jupyter-style environment because of top-level `await` and `input()`.
- The requested models (`gpt-5.4-mini` and so on) must exist on your account; edit
  `MODEL_CANDIDATES` if none of the three is reachable.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
