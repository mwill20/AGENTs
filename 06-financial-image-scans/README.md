# Financial Image Scans

Reads scanned pages from a company financial report and writes a summary aimed at a chosen reader.

The model is `gpt-4o-mini` through `langchain-openai`, at `temperature=0`.

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
