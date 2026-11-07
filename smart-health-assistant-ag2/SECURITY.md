# Security: Smart Health Assistant with AG2

A single-user notebook with one user, three LLM agents and one read-only arithmetic tool. It reads
no external content, writes no files and takes no action in the world. It is not a deployed
service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> notebook | Weight, height, age, gender, dietary preference (typed at `input()` prompts or taken from `DEFAULT_PROFILE`) | Untrusted until validated |
| Notebook -> OpenAI | The validated profile, each agent's prompt, the previous agent's reply, API key (as auth header) | Third-party processing of **personal health data** |
| OpenAI -> notebook | BMI reply, meal plan, workout plan, tool-call requests | Untrusted model output |
| BMI Agent -> `calculate_bmi` | Two numbers chosen by the model from the prompt | Model-controlled arguments to local code |
| Notebook -> reader | Rendered Markdown | Untrusted until a human reads it |

The user's five values are the only free input. They pass through `validate_profile` (type, range,
allowed set) before they reach a prompt, so free text never enters the conversation: gender and
diet are normalised to one of a fixed set, and the three numbers are bounded.

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Lookup order is Colab Secrets, then environment variable, then hidden `getpass`. Only "API key loaded." is printed |
| Key fragment echoed in a provider error | The model probe prints `type(exc).__name__` only, never the error text |
| Empty key | Raises `ValueError` before any call |
| Bad input reaching the model | `validate_profile`: weight 20-400 kg, height 100-250 cm, age 10-120, gender and diet from fixed tuples. Four should-fail cases are asserted in the notebook |
| Tool called with bad arguments | `calculate_bmi` raises on non-positive inputs; AG2 builds the schema from the type hints |
| Model skipping the tool and guessing | Checks R6 compares the tool's returned BMI with an independent recomputation and requires that value in the reply |
| Tool reachable from the wrong agent | Only the BMI Agent is built with `tools=[bmi_tool]`; R5 asserts the other two have none |
| Runaway cost | Exactly one probe plus three agent calls per run; no loops around the model |
| Dependency drift | `ag2[openai]==1.1.2` pinned in the notebook and `requirements.txt` |

## Known gaps

- **Health data leaves your machine.** Weight, height, age and gender are sent to OpenAI. Do not
  enter another person's data without their consent, and treat the plan as general wellness text.
- **No output validation beyond structure.** The check cell checks for words such as "recommend" and
  the day names. Nothing checks that a "Vegan" plan has no animal products or that exercises are
  safe for the stated age.
- **Rendered Markdown.** Model-written Markdown is displayed with `IPython.display`. Notebook
  frontends sanitise HTML, but do not publish outputs without reading them.
- **Interactive input retries.** Invalid input is re-prompted up to three times and then raises;
  in a non-interactive run a bad `DEFAULT_PROFILE` raises immediately. That is fail-closed, but the
  error message echoes the rejected value.
- **No audit logging** beyond the printed transcript, and **no spend cap** beyond the fixed call
  count.

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Add tools that write, send or purchase without a code-level gate and a human step in front of
  them. That would change the threat model completely.
- Use this for anyone's real medical decisions.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
