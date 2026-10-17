# Security: Assignment 5 (Study Assistant)

A coursework notebook that sends document text to a hosted language model. It is not a deployed
service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| User -> notebook | PDF file or pasted text | Untrusted content |
| Notebook -> OpenAI API | Study material, summary, API key (as auth header) | Third-party processing |
| OpenAI API -> notebook | Summary text, structured quiz | Untrusted model output |

## Controls present in the code

| Threat | Control |
|---|---|
| API key leaked in the saved notebook | Key read with `getpass` into an environment variable; never written into a cell. The saved output shows only masked dots |
| Malformed model output reaching the display step | The quiz is requested as a Pydantic schema, and `validate_quiz` drops any question without exactly four options or with an answer index outside 0-3 |
| Model inventing content | Both prompts say to use only facts stated in the material. This is an instruction, not an enforced control |
| Run-to-run drift | `temperature=0` |
| Dependency drift | Packages pinned in `requirements.txt` |

## Known gaps

- **Indirect prompt injection.** The study material is untrusted text placed straight into the
  prompt. A document that contains instructions could steer the summary or the quiz. The blast
  radius is small because the model has no tools and takes no actions, but the output can still be
  wrong or misleading.
- **No semantic validation.** `validate_quiz` checks structure only. A question with a wrong marked
  answer passes. Read the answer key before relying on it.
- **Data leaves your machine.** The full document text is sent to OpenAI. Do not use confidential
  or regulated documents.
- **No input limits.** There is no check on PDF size or text length, and no cost cap on API use.
- **No audit logging.**

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Run sensitive documents through the notebook.
- Hand the generated answer key to learners without reviewing it.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
