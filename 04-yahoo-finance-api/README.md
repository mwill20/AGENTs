# Assignment 4: Yahoo Finance API

Four FastAPI endpoints that pull company and market data from Yahoo Finance (via the
[`yfinance`](https://pypi.org/project/yfinance/) library) and produce a simple deterministic
analysis. Packaged as a single notebook per the assignment's "one file" deliverable requirement.

## Purpose

This assignment demonstrates how to wrap an external data source in a small, validated HTTP API.
Each endpoint checks its input before it calls Yahoo Finance, and returns a clear `400`, `404` or
`422` instead of a raw exception. It is a data-API exercise, not an LLM agent: no model is called
anywhere.

## Intended audience

Readers who want a compact example of FastAPI request validation, `yfinance` usage, and
in-notebook API testing with `TestClient`.

Expected background: basic Python, and a rough idea of what a REST endpoint is.

## Project status

Prototype / coursework deliverable. The notebook was run end to end by the author and behaved as
expected. The saved outputs come from that run. It was **not** re-run during repository
preparation.

## What's here

| File | Purpose |
|---|---|
| `Yahoo_Finance_API.ipynb` | The deliverable. Defines the FastAPI app and all four endpoints, then demonstrates each one (happy path plus error path) using FastAPI's `TestClient`. No server or port needed; it runs in-process. |
| `requirements.txt` | Pinned dependency versions. |
| `SECURITY.md` | Trust boundaries, controls and known gaps for this assignment. |

## Requirements

| Requirement | Notes |
|---|---|
| Python | Saved output shows Python 3.12. Other versions are untested. |
| Packages | Pinned in `requirements.txt` (`fastapi`, `httpx`, `pydantic`, `yfinance`, `pandas`). |
| External services | Yahoo Finance, reached through `yfinance`. No API key needed. |
| Network | Required. Every endpoint call goes out to Yahoo Finance. |
| GPU | Not needed. |

## Quickstart

```bash
git clone https://github.com/mwill20/AGENTs.git
cd AGENTs/04-yahoo-finance-api
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
jupyter notebook Yahoo_Finance_API.ipynb
```

`jupyter` is not in `requirements.txt`; install it separately (`pip install notebook`) if you do
not already have it, or open the notebook in VS Code or Google Colab.

Then **Run All**. Success looks like this: every demo cell prints a status code, with `200` on the
happy paths and `400`, `404` or `422` on the error paths. Re-running hits live Yahoo Finance data,
so numbers such as prices will differ from the saved outputs.

## Endpoints

| # | Method & Path | Purpose |
|---|---|---|
| 1 | `GET /company/{symbol}` | Company info: name, business summary, industry, sector, officers |
| 2 | `GET /market/{symbol}` | Market snapshot: state, price, price change, % change |
| 3 | `POST /historical` | JSON body with `symbol`, `start_date`, `end_date`; returns daily OHLCV rows |
| 4 | `POST /analysis` | Same body shape; returns moving averages, volatility, return, drawdown, trend |

All four validate their input (symbol format, date ordering) before calling Yahoo Finance, and
return `400`/`404`/`422` with a clear message instead of a raw exception when the input is bad
or the symbol has no data.

### Example (from the notebook's saved output)

Request: `POST /historical` with `{"symbol": "AAPL", "start_date": "2026-06-01", "end_date": "2026-07-01"}`

Response: `200`, 21 daily rows of `Date, Open, High, Low, Close, Volume`.

Error case: the same request with `start_date` and `end_date` swapped returns `422` with
`end_date must be after start_date`, before any call to Yahoo Finance.

## Architecture

```text
Request -> input validation (symbol regex, date order)
        -> yfinance call (Yahoo Finance, unofficial endpoints)
        -> 404 if no data | deterministic maths (analysis only)
        -> JSON response
```

## Evaluation

The notebook demonstrates every endpoint once on valid input and once on invalid input, with the
outputs saved. It contains no automated test suite and no accuracy measurement of the analytics
against an independent source.

| Metric | Result |
|---|---|
| Automated tests | None in this folder |
| Analytics accuracy vs. an independent source | Not yet measured |

## Security considerations

See [SECURITY.md](SECURITY.md). In short: input is validated; there is no authentication, rate
limiting or audit logging.

## Limitations

- `yfinance` uses Yahoo Finance's unofficial, undocumented endpoints. No API key is required,
  but there is no uptime or schema guarantee. If Yahoo changes a field name, the affected
  endpoint's `.info` lookup will need updating (see the notes cell at the end of the notebook).
- This is a demo/assignment deliverable: no authentication, no rate limiting, no persistence.
  Not intended for production use.
- Analytical Insights is deterministic (moving averages, volatility, return, drawdown). No LLM
  call is involved, so results are reproducible from the same input data.
- The output is data and arithmetic, not investment advice.
- Yahoo's data terms are not reviewed here. Check them before using this beyond coursework.

## License

MIT. See the repository-root [LICENSE](../LICENSE).

## Support

Open an issue on the repository. Report security problems as described in [SECURITY.md](SECURITY.md).
