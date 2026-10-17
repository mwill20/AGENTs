# Security: Assignment 6 (Financial Image Scans)

A coursework notebook that sends page images to a hosted vision model. It is not a deployed
service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Image source -> notebook | Local file or URL | Untrusted content |
| Notebook -> OpenAI API | Base64-encoded page images, extracted figures, API key (as auth header) | Third-party processing |
| OpenAI API -> notebook | Extracted figures, summaries, chart readings | Untrusted model output |

## Controls present in the code

| Threat | Control |
|---|---|
| API key leaked in the saved notebook | Key read with `getpass` into an environment variable; saved output shows only masked dots |
| Model inventing figures | System rule: write "not shown in the provided pages" for anything missing, and never estimate. This is an instruction, not an enforced control |
| Report text read as new instructions | Task, audience, figures and format example sit in separate tagged sections. This reduces the risk but does not remove it |
| Free-form extraction output | Extraction is requested as a Pydantic schema, so the figures are typed objects |
| Slow or hanging URL fetch | `requests.get(..., timeout=30)` and `raise_for_status()` |
| Dependency drift | Packages pinned in `requirements.txt` |

## Known gaps

- **No semantic validation of extracted figures.** Nothing checks the figures against the page. The
  saved chart-reading output in this repository contains errors against the source image (see the
  README's Evaluation section). A wrong digit looks identical to a right one.
- **Indirect prompt injection via images.** Text inside an image is read by the model. A crafted
  page could carry instructions. The model has no tools and takes no actions, but its output can
  still be wrong or misleading.
- **`load_images` fetches any URL it is given.** There is no allow-list and no size limit. That is
  acceptable for a notebook where you choose the sources, but not for a service that accepts URLs
  from other people (server-side request forgery risk).
- **Data leaves your machine.** The page images go to OpenAI. Do not use confidential or
  non-public financial documents.
- **No cost cap and no audit logging.**

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Use the output for investment, audit or compliance decisions without checking it against the
  source pages.
- Point `load_images` at URLs supplied by untrusted users.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
