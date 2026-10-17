# Assignment 5: Study Assistant (Summarize and Quiz)

A LangChain notebook that reads study material from a PDF or pasted text, condenses it into key
points, and writes multiple-choice questions with four options and a marked answer.

## Purpose

This assignment demonstrates prompt engineering and structured output with LangChain. It solves
"turn a block of study material into a short summary and a self-test" by chaining two prompts:
summarize into key points, then generate a quiz from those key points. The quiz comes back as a
Pydantic schema, so the shape of every question is checked in code before it is shown.

There is no vector database and no retrieval step. The document text goes straight into the
prompt, which keeps the setup light for studying one document at a time.

## Pattern

**Prompt chain (summarize -> quiz) with schema-validated output.** This is a fixed two-step
pipeline. The model does not choose tools or decide what to do next, so it is not an autonomous
agent.

## Intended audience

Learners who want a small, readable example of LangChain prompt templates, `with_structured_output`,
and output validation.

Expected background: basic Python, and an OpenAI API key.

## Project status

Prototype / coursework deliverable. The notebook was run end to end by the author and behaved as
expected. The saved outputs come from that run. It was **not** re-run during repository
preparation.

## What's here

| File | Purpose |
|---|---|
| `Study_Assistant_Quiz_Generator.ipynb` | The deliverable. |
| `requirements.txt` | Pinned versions, copied from the notebook's install cell. |
| `SECURITY.md` | Trust boundaries, controls and known gaps. |

The PDF the notebook was run on (`Prompt Engineering (1).pdf`) is course material and is **not**
included in this repository. See "Supplying your own study material" below.

## Requirements

| Requirement | Notes |
|---|---|
| Python | Saved install output shows Python 3.12 (Google Colab). |
| Packages | Pinned in `requirements.txt`. |
| External services | OpenAI API (model `gpt-4o-mini`). **Paid, pay-as-you-go.** |
| Environment | Written for Google Colab. The PDF-upload cell uses `google.colab.files`. |
| GPU | Not needed. |

## Quickstart (Google Colab)

1. Open `Study_Assistant_Quiz_Generator.ipynb` in Google Colab.
2. Run the install cell.
3. Run the key cell. It asks for `OPENAI_API_KEY` through a hidden `getpass` prompt and holds it in
   an environment variable only. It is never written into a cell.
4. Run the upload cell and choose a text-based PDF, or skip it and use the pasted-text example at
   the end.
5. Run the remaining cells in order.

Success looks like this: the notebook prints a bulleted summary, then `Kept N of N generated
questions`, followed by numbered questions with options `a)` to `d)` and an answer key.

Running locally instead of in Colab:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/05-study-assistant-quiz-generator
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

The upload cell imports `google.colab` and will fail outside Colab. Locally, replace it with a
path assignment (`PDF_PATH = 'your_file.pdf'`) and skip the upload cell.

## Supplying your own study material

Any PDF with a text layer works. Set `PDF_PATH` to its filename. Or call
`study_assistant(text, num_points, num_questions)` directly with pasted text, as the last example
does.

## Example (from the notebook's saved output)

Input: a short pasted paragraph on "Prompt Engineering for Agents", with `num_points=3` and
`num_questions=2`.

Output: three summary bullets, then two multiple-choice questions with four options each and an
answer key.

## Architecture

```text
PDF or pasted text -> whitespace cleanup
                   -> summary chain  (prompt -> gpt-4o-mini -> text, temperature 0)
                   -> quiz chain     (prompt -> gpt-4o-mini -> Quiz schema)
                   -> validate_quiz  (exactly 4 options, answer index 0-3)
                   -> printed questions + answer key
```

## Evaluation

The notebook shows one PDF run (5 of 5 questions kept) and one pasted-text run. There is no test
suite, and answer correctness has not been measured against a reference.

| Metric | Result |
|---|---|
| Questions kept by `validate_quiz` (saved PDF run) | 5 of 5 |
| Answer-key correctness | Not yet measured |
| Summary faithfulness to source | Not yet measured |

## Security considerations

See [SECURITY.md](SECURITY.md). The main points: the key is entered through a hidden prompt, the
study material is untrusted text sent to a third-party model, and the quiz validator checks shape
only.

## Limitations

- The whole document goes into the prompt, so a long book will exceed the context window. Split it
  and run the assistant on one section at a time.
- PyPDF2 reads the text layer of a PDF. A scanned or image-based PDF returns empty strings and
  needs OCR before this notebook can use it.
- `validate_quiz` checks the shape of the response, not whether the marked answer is actually
  right. The answer key still comes from the model and should be read before a student relies on it.
- Quiz quality tracks summary quality. If a key point is vague, the questions built on it will be
  vague too.
- The second install cell runs `pip install PyPDF2` without a version pin. The first cell already
  pins `PyPDF2==3.0.1`, so the same version resolved in the saved run.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
