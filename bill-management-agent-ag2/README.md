# Bill Management Agent (Group Chat with Bill Images, AG2)

A User Proxy Agent validates a set of receipt images and opens a group chat with a Group Manager.
The **Bill Processing Agent** (a vision model) reads every receipt and returns a categorised table
plus a machine-readable JSON block. The **Expense Summarization Agent** then reports spending per
category, names the highest category and flags unusual spending. Python re-parses the JSON,
recomputes the totals and the highest category, and the check cell compares the agents' claims with
those numbers.

## Purpose

This project demonstrates **multimodal input** (images passed to an agent with AG2's
`ImageInput`) inside a **sequential group chat**. It solves "turn receipts into a categorised
spending report you can check" by making the vision agent emit structured data and verifying that
data arithmetically, so the model never gets the last word on a total.

## Pattern

**Group chat, sequential routing.** The same plain-Python `GroupChat` / `GroupChatManager` /
`state_transition` trio as `financial-portfolio-manager-ag2`, extended so the manager attaches the images only to the
agents listed in `vision_agents`. The transitions are fixed:

```text
User Proxy -> Bill Processing (with images) -> Expense Summarization -> None (end)
```

The number of image parts actually sent is read back from AG2's own `ModelRequest` event, so check
R3 proves the images reached the model rather than assuming it.

## Intended audience

Learners who want a small example of sending images to an AG2 1.x agent, and of validating a
vision model's output with code instead of trust.

Expected background: basic Python, and comfort with Jupyter or Colab (top-level `await`).

## What's here

| File | Purpose |
|---|---|
| `Bill_Management_Agent_AG2.ipynb` | The notebook |
| `requirements.txt` | Dependencies, copied from the notebook's install cell |
| `SECURITY.md` | Trust boundaries, controls and known gaps |

Running the notebook creates `sample_bills/` (three PNG receipts) and `not_an_image.txt` (used by
the should-fail self-test) in the working directory. Both are ignored by the repository's
`.gitignore`.

## Requirements

| Requirement | Notes |
|---|---|
| Python | `ag2` 1.1.2 declares `>=3.10` on PyPI. Written for Google Colab |
| Packages | `ag2[openai]==1.1.2` and `pillow>=10.1`. Pillow is a lower bound in the notebook and is reproduced as such; pin it yourself for a reproducible local environment |
| LLM | OpenAI (**paid, pay-as-you-go**). All `MODEL_CANDIDATES` must accept image input |
| Environment | Jupyter, VS Code or Google Colab. Not a plain script |

## Quickstart (Google Colab)

1. Open `Bill_Management_Agent_AG2.ipynb` in Google Colab.
2. Add `OPENAI_API_KEY` to the **Secrets** panel with **Notebook access** on. Without it, the
   notebook checks the environment variable and then asks you to paste a key (hidden, never
   printed).
3. Runtime -> Run all. With the default `USE_SAMPLE_BILLS = True` no upload is needed. To use your
   own receipts set it to `False`; Colab opens an upload dialog, and a local run reads
   `./my_bills/*`.

Locally:

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/bill-management-agent-ag2
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Then set `OPENAI_API_KEY` in your environment and open the notebook in Jupyter or VS Code.

Success looks like this: three receipts displayed with a ground-truth line (`grand total: 144.92`),
a `PASS` validation self-test, a `User_Proxy_Agent -> Group_Manager (+3 image(s))` block, round 1
to `Bill_Processing_Agent` with `3 image(s)`, round 2 to `Expense_Summarization_Agent`, a
`Flow complete` line, a rendered report ending in a deterministic-check line, and a check block ending
in `12/12 checks passed`.

## Settings

| Setting | Default | Notes |
|---|---|---|
| `MODEL_CANDIDATES` | `["gpt-5.4-mini", "gpt-5-mini", "gpt-4.1-mini"]` | Vision-capable; first reachable is used |
| `MAX_ROUND` | `4` | Safety cap; the flow normally ends after 2 speakers |
| `USE_SAMPLE_BILLS` | `True` | `False` uses your own images; check R6 (ground truth) is then skipped |
| `MAX_IMAGE_MB` | `10` | Per-file size limit in `validate_bill_images` |

## Architecture

```text
SAMPLE_BILLS (3 receipts, line items, ground-truth totals)  --Pillow-->  sample_bills/*.png
   |
User Proxy Agent (no LLM): validate_bill_images() -> ImageInput(...) -> initiate_chat(manager)
   |
GroupChatManager.run()
   round 1  Bill_Processing_Agent   gets transcript + images  -> table + "Total amount spent" + ```json block
   round 2  Expense_Summarization_Agent gets transcript only  -> per-category table, Highest category, Insights
   round 3  state_transition -> None: stop
   |
parse_expenses() -> by_category, computed_total, highest_category   (plain Python)
   |
Markdown report + deterministic-check line + 12 automated checks
```

## Agent safety boundaries

This system is allowed to:

- Send the validated receipt images and the transcript to OpenAI, for up to `MAX_ROUND` speakers
- Read files the user chose (sample receipts, or uploads / `./my_bills`)

This system is not allowed to:

- Use any tool, browse, run code or write files. Neither agent has tools. The only files written
  are the sample receipts and the self-test text file, by the notebook itself before any model call
- Send images to the summarisation agent. Only `Bill_Processing_Agent` is in `vision_agents`
- Accept a missing file, a non-image extension or a file over `MAX_IMAGE_MB`
- Have the final say on totals. The stated total must equal the sum of the parsed items (R5), and
  the stated highest category must equal the computed one (R9)

Human approval is required for: nothing today, because the output is a text report.

## Evaluation

The last cell is a twelve automated checks (R1-R12): validated images and should-fail cases, the User
Proxy opened the chat, the Bill agent went first and received all images, the JSON has at least
three items with allowed categories and positive amounts, the stated total equals the item sum, the
computed total is within 1% of the ground truth (sample bills only), the Summarization agent saw the
Bill agent's message, every category is named in the summary, the highest category matches the
computation, insights are present, the speaker order and visibility are right, and both outputs are
non-empty.

| Check | Recorded result |
|---|---|
| Sample bills, validation self-test, `parse_expenses` (cells 3-5, 9) | PASS |

## Security considerations

See [SECURITY.md](SECURITY.md).

## Limitations

- The sample receipts are clean, high-contrast synthetic images. Photographed receipts with tax lines,
  discounts and folds are outside the sample set.
- Category assignment is the model's judgement against a fixed list; the deterministic check only
  confirms the category is in the list, not that it is right.
- `validate_bill_images` checks the extension, not the file content. A renamed non-image passes
  validation and is rejected (or misread) only by the model.
- Non-deterministic: no seed or temperature is set.
- Needs a Jupyter-style environment because of top-level `await`.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
