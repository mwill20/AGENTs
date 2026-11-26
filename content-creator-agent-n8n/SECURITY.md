# Security: AI Content Creator Agent (n8n)

A manually run n8n workflow that reads topics from a Google Sheet, sends them to Tavily and OpenAI,
and writes generated posts back to the same sheet. It is not a deployed service and it never posts
anything to a social network.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Google Sheet -> workflow | Topic and Status columns | Trusted only as far as the sheet's editors are |
| Workflow -> Tavily | Topic text, Tavily API key in a header | Third-party processing |
| Tavily -> workflow | Search answer, titles, URLs and page text from arbitrary sites | **Untrusted, attacker-influenceable** |
| Workflow -> OpenAI | Topic plus the research brief | Third-party processing |
| OpenAI -> sheet | Generated LinkedIn, X and blog text | Untrusted model output |

## Controls present in the workflow

| Threat | Control |
|---|---|
| Leaked API keys | Keys live only in n8n's credential store. The exported JSON holds credential names and IDs, never values |
| Indirect prompt injection via search results | Every prompt labels the research brief as reference material and tells the model to ignore instructions inside it. Prompt-level only |
| Invented facts | Every prompt forbids invented statistics, names, quotes and dates |
| Reprocessing finished rows | Only rows with `Status = Pending` are read; Completed rows are never touched |
| Empty input reaching the APIs | Blank topics are dropped before any API call |
| Writing to the wrong row | The update is matched on `row_number` carried through the loop |
| Bad Tavily key | Tavily returns 401 and the run stops before any sheet write |
| Blast radius of a successful injection | The only write is text into the sheet. Nothing is published automatically |

## Known gaps

- **Injection defence is prompt-level.** A crafted search result could still steer the generated
  text. A human must review every post before it is published.
- **Length limits are not enforced in code.** An over-length X post would still be written.
- **Anyone who can edit the sheet controls the topics** sent to Tavily and OpenAI, and so controls
  spend.
- **No retry, no spend cap, no audit log** beyond n8n's own execution history.
- **Data leaves your environment.** Topics and search content go to Tavily and OpenAI.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
