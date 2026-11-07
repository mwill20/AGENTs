# Personalized Education Assistant (CrewAI)

Give the crew a short list of **topics** and an **expertise level** (`beginner`, `intermediate` or
`advanced`). Three agents run in sequence: a **Learning Material Curator** collects videos,
articles and exercises; a **Quiz Creator** writes a five-question quiz grounded in that material;
and a **Project Mentor** proposes three projects, sized by a deterministic custom tool. Every task
returns a validated Pydantic object, and the run is saved to `education_plan.json`.

## Purpose

This project demonstrates **structured outputs** (`output_pydantic`), a **custom tool**
(`BaseTool` with a typed `args_schema`) and **task context** in CrewAI 1.15. It solves "produce
usable learning data, not prose" by making each task's answer a typed object that Pydantic
validates, and by putting the one policy decision (how big a project a beginner should get) in
code rather than in the model.

## Pattern

**Sequential crew with typed hand-offs.** `Process.sequential` runs the three tasks in order.
The quiz and project tasks declare `context=[curate_task]`, so they see the curated materials. The
Project Mentor must call `ProjectSuggestionTool`, whose `expertise_level` argument is a `Literal`
of the three allowed values, so an invalid level is rejected by the schema before the tool body
runs.

## Intended audience

Learners who want a compact example of Pydantic-validated task outputs and a custom tool in
CrewAI, and who want to see which decisions were kept out of the model.

Expected background: basic Python and Pydantic, and comfort with Jupyter or Colab (top-level
`await`).

## What's here

| File | Purpose |
|---|---|
| `Personalized_Education_Assistant_CrewAI.ipynb` | The notebook, with saved outputs |
| `requirements.txt` | Pinned dependency, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

Running the notebook
writes `education_plan.json` to the working directory; it is ignored by `.gitignore`.

## Requirements

| Requirement | Notes |
|---|---|
| Python | `crewai` 1.15.33 declares `>=3.10,<3.14` on PyPI. Written for Google Colab |
| Packages | `crewai[tools]==1.15.33` (pulls in `crewai-tools`, Pydantic and the OpenAI client) |
| LLM | OpenAI (**paid, pay-as-you-go**), `MODEL = "gpt-4o-mini"`, `temperature=0.3` |
| Optional | `SERPER_API_KEY` is read but **unused** while `search_tools = []` |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script (top-level `await`) |

## Quickstart (Google Colab)

1. Open the notebook in Google Colab.
2. Add `OPENAI_API_KEY` to the **Secrets** panel with **Notebook access** on. The key cell also
   accepts an environment variable or a hidden `getpass` prompt. It prints only `True` / `False`.
3. Edit `TOPICS` and `EXPERTISE_LEVEL` in section 3 if you like, then Runtime -> Run all.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/personalized-education-crewai
python -m venv .venv            # Python 3.10 to 3.13
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` in your environment and open the notebook in Jupyter or VS Code.

Success looks like this: `Done. Tasks completed: 3`, then three printed blocks (learning materials
with URLs, a five-question quiz with answers and explanations, three projects with hours and
skills), then `Saved education_plan.json` and the start of the JSON.

## Settings

| Setting | Default | Notes |
|---|---|---|
| `TOPICS` | `["Python decorators", "SQL joins"]` | 1 to 5 topics, each at most 60 characters, no braces or newlines |
| `EXPERTISE_LEVEL` | `"beginner"` | Must be `beginner`, `intermediate` or `advanced` |
| `MODEL` | `gpt-4o-mini` | One `LLM` object shared by all agents |
| `max_iter` | 8 / 5 / 8 | Per-agent reasoning-loop cap (curator / quiz / mentor) |
| `allow_delegation` | `False` on every agent | Task order is the design |

## Architecture

```text
TOPICS + EXPERTISE_LEVEL  -> validation (allowed level, topic count and length, no braces)
   |
Crew(process=sequential)
   task 1  Learning Material Curator  (tools: none while search is disabled)  -> LearningMaterials
   task 2  Quiz Creator               context=[task 1]                         -> Quiz
   task 3  Project Mentor             context=[task 1], tools=[ProjectSuggestionTool] -> ProjectIdeas
   |
result.tasks_output[i].pydantic  ->  printed report  ->  education_plan.json
```

`ProjectSuggestionTool._run` is a dictionary lookup: level -> scope, constraints, success criteria,
typical hours. The model turns that template into concrete projects; it cannot change the template.

## Agent safety boundaries

This system is allowed to:

- Call the OpenAI API for three tasks, each bounded by `max_iter`
- Call `ProjectSuggestionTool`, a pure function with no side effects
- Write one file, `education_plan.json`, from already-validated objects

This system is not allowed to:

- Delegate between agents (`allow_delegation=False` everywhere)
- Search the web, in this build. `SerperDevTool` is imported by the `[tools]` extra but never
  attached while `search_tools = []`
- Accept an unknown expertise level or an oversized topic list. Validation raises before kickoff

Human approval is required for: nothing today, because the output is text and one local JSON file.

## Evaluation

The evidence in the notebook is: the section 3 validation, the section 5
tool self-check (template returned, invalid level rejected), Pydantic validation of all three task
outputs at kickoff, and the saved outputs of a completed run.

| Check | Recorded result |
|---|---|
| Input validation, Pydantic models, custom tool | PASS |
| Crew run | Completed (3 tasks) |

Pydantic checks shape, not truth: a `Resource.url` must be a string, not a working link.

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limitations

- With search disabled, every URL comes from model memory; check links before sharing them.
- `estimated_hours` is an `int` with no range check; the tool's "typical hours" guidance is advice
  to the model, not a constraint.
- Non-deterministic at `temperature=0.3`.
- Needs a Jupyter-style environment because of top-level `await`.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
