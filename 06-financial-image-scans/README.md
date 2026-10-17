# Financial Image Scans

Reads scanned pages from a company financial report and writes a summary aimed at a chosen reader.

The model is `gpt-4o-mini` through `langchain-openai`, at `temperature=0`.

## Purpose

This assignment demonstrates multimodal prompting: sending page images to a vision-capable model
and getting structured figures and audience-specific summaries back. It solves "turn scanned
report pages into a readable summary for a chosen reader" by separating **reading** (image to
figure list) from **writing** (figure list to summary), so a misread number is visible in the
figure list instead of buried in prose.

## Pattern

**Chained prompts with a typed intermediate result.** Three fixed model calls, with no tools and
no autonomy: extract figures into a Pydantic schema, write a summary from that list, and read the
charts. It is a prompting exercise, not an autonomous agent.

## Intended audience

Learners comparing prompt designs for vision models: role and rule in the system message, tagged
sections, a schema on extraction, and a variable audience.

Expected background: basic Python and an OpenAI API key.

## Project status

Prototype / coursework deliverable. The notebook was run end to end by the author and behaved as
expected. The saved outputs come from that run. It was **not** re-run during repository
preparation. See "Evaluation" for what the saved outputs actually show.

## Requirements

| Requirement | Notes |
|---|---|
| Python | Saved install output shows Python 3.12 (Google Colab). |
| Packages | Pinned in `requirements.txt`. |
| External services | OpenAI API (model `gpt-4o-mini`, with vision). **Paid, pay-as-you-go.** |
| Environment | Written for Google Colab. The upload cell uses `google.colab.files`. |
| Disk | Images are about 225 KB in total. |

## The images

Both pages are from the ABN AMRO Q3 2024 report and ship in `images/`.

| File | What it shows |
| --- | --- |
| `balance_sheet.png` | Condensed consolidated statement of financial position, three comparative periods |
| `figures_at_a_glance.png` | Nine bar charts, five quarters each, with a printed data label on every bar |

`load_images()` takes local paths or URLs, so either source works. The images are opened with PIL
and held in a list, and that list is what the rest of the notebook works from.

## Running it in Colab

1. Open `Financial_Image_Scans.ipynb` in Colab.
2. Run the install cell.
3. Run the key cell and paste an OpenAI API key when the hidden prompt appears.
4. Run the upload cell and pick both files from `images/`.
5. Run the rest in order.

To run it on other pages, change `SOURCES` and `NAMES` in section 2. Nothing else is tied to these
two files apart from the format example, which is covered under Limits.

## The three prompts

The notebook makes three calls, each doing one job.

**Read the figures.** Returns a flat list of figures and nothing else: label, value, period, and
which page it came from. No sentences, no comparisons, no arithmetic. Asking for a Pydantic model
back means the result is Python objects, so the figures can be counted and checked in code.

**Write the summary.** Takes the figure list from the first call, not the pixels. The reader is a
variable rather than three separate prompts, so investor, analyst and auditor summaries come from
one instruction and stay comparable.

**Read the charts.** Only the charts page goes in. The instruction that does the work is the one
telling the model to read the printed data labels instead of judging a bar by its height, which is
where vision models drift on this kind of page.

Techniques used across the three:

- A role and a rule in the system message. The rule that matters is the one requiring
  "not shown in the provided pages" for anything missing, because an invented figure is
  indistinguishable from a printed one once it reaches the summary.
- `<task>`, `<audience>`, `<figures>` and `<format_example>` tags. Tags mark where the instruction
  stops more clearly than a blank line does, and they keep report text from being read as a new
  instruction.
- Reading kept separate from writing, so a misread digit shows up in the figure list where it can
  be seen.
- A schema on the extraction step.
- The audience held in a dictionary and passed as a variable.
- A short format example taken from the problem statement, which fixes the heading structure and
  bullet density without dictating content.

## Architecture

```text
page images -> PIL -> base64 data URLs
            -> call 1: extract figures      (vision model -> Extraction schema, 30 figures in the saved run)
            -> call 2: write summary        (figure list + audience + format example -> text)
            -> call 3: read the charts      (charts page only -> text)
```

## Evaluation

There is no automated test suite or scoring script in this folder. The notes below come from
checking the **saved** outputs against `images/figures_at_a_glance.png` by eye during repository
preparation.

| Check | Result |
|---|---|
| Figure extraction ran and returned a typed list | Yes (30 figures, 0 risks, in the saved run) |
| Summaries ran for investor, analyst and auditor readers | Yes |
| Chart-reading output (call 3) matches the page | **No, in the saved output.** See below |
| Accuracy of the 30 extracted figures against the balance sheet | Not yet measured |

**Saved chart-reading output does not match the page.** Each chart on the page has five bars
(Q3 23 to Q3 24). The saved output for call 3 lists four values per chart and shifts the quarter
labels. Examples:

- Net profit: the page shows 759, 545, 674, 642, 690. The saved output lists 759, 674, 642, 690
  and labels the last one "Q2 24". The 545 bar is missing.
- Cost/income ratio: the page shows 55.5, 71.6, 57.2, 58.2, 59.2. The saved output starts at 71.6
  and labels it "Q3 23".
- Return on equity: the saved output says 11.6% is "inside" the 9-10% target. 11.6% is above that
  range.

This is the failure the Limits section warns about. The notebook is kept as submitted so the
behaviour stays visible. Treat call 3's saved output as an example of the method, not as correct
data. If you extend this notebook, a simple next check is to assert that every chart returns five
values before the text is accepted.

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limits

- The figures come from a model reading an image. Check them against the source pages before using
  them for anything that matters.
- The supplied scans are about 640 pixels wide. That is enough for the printed labels on these
  pages, but a smaller or skewed scan will produce wrong digits, and a wrong digit looks exactly
  like a right one in the output.
- The format example in section 4 is drawn from the same report as the images. It is there for
  shape. Pointing the notebook at a different company means replacing it, or the headings will not
  fit what the pages contain.
- Two pages of one quarter of one bank is not a view on the business. This shows the method, not a
  finished piece of analysis.
- The charts call depends on printed data labels. A chart without them falls back to bar height,
  which is where the errors start.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
