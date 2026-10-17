# Yahoo Finance API: Assignment Deliverable

Four FastAPI endpoints that pull company and market data from Yahoo Finance (via the
[`yfinance`](https://pypi.org/project/yfinance/) library) and produce a simple deterministic
analysis. Packaged as a single notebook per the assignment's "one file" deliverable requirement.

## What's here

- `Yahoo_Finance_API.ipynb`: the deliverable. Defines the FastAPI app, all four endpoints,
  and demonstrates each one (happy path plus error path) using FastAPI's `TestClient`. No
  server or port needed, it's fully self-contained and runs in-process.
- `requirements.txt`: pinned dependency versions.

## How to run

```bash
pip install -r requirements.txt
jupyter notebook Yahoo_Finance_API.ipynb
```

Then Run All. Every cell's output is already populated from a real execution, but re-running
confirms it still works against live Yahoo Finance data.

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

## Limitations

- `yfinance` uses Yahoo Finance's unofficial, undocumented endpoints. No API key is required,
  but there is no uptime or schema guarantee. If Yahoo changes a field name, the affected
  endpoint's `.info` lookup will need updating (see the notes cell at the end of the notebook).
- This is a demo/assignment deliverable: no authentication, no rate limiting, no persistence.
  Not intended for production use.
- Analytical Insights is deterministic (moving averages, volatility, return, drawdown). No LLM
  call is involved, so results are reproducible from the same input data.
