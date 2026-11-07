# Assignment 16 — Financial Portfolio Manager: Rubric

Every expectation in the assignment brief maps to one row. The notebook's last cell runs the automated check for each row and prints `PASS` / `FAIL`; the "Manual check" column is what a reviewer can confirm by reading the transcript.

| # | Expectation (assignment text) | Evidence in the notebook | Automated check | Manual check |
|---|---|---|---|---|
| R1 | Step 3 inputs: current salary + summary of the current investment portfolio, collected by the User Proxy Agent | Section 4: `UserProxyAgent.collect()` prompts for salary, currency and portfolio summary; `validate_inputs` enforces ranges and formats | `user_inputs` is a `UserInputs`; should-fail self-test (non-numeric salary, salary 0, bad currency code, empty portfolio) all raise `ValueError` | "Collected: {...}" line and "validation self-test: PASS" |
| R2 | Step 1: User Proxy Agent initiates the chat and informs the Group Chat Manager of the user's intention to manage their investments | Section 8: `user_proxy.initiate_chat(group_chat_manager, message=...)` | First group-chat message is from the User Proxy and contains "manage my investments" | Transcript starts with `User_Proxy_Agent -> Group_Chat_Manager` |
| R3 | Step 2: Group Chat Manager calls the Portfolio Analysis Agent to take user inputs | Section 7 manager + Section 6 StateFlow (User Proxy → Portfolio Analysis) | `speaker_order[0] == Portfolio_Analysis_Agent` | "Round 1: next speaker -> Portfolio_Analysis_Agent" |
| R4 | Step 3: Portfolio Analysis Agent summarizes the portfolio and determines Growth or Value | Section 5 prompt (summary + decision rules + mandatory `CATEGORY:` line) | `parse_category()` returns Growth or Value and the reply mentions the portfolio | Reply lists holdings and ends with `CATEGORY: ...` |
| R5 | Step 4: StateFlow dynamically directs the workflow to the Growth *or* the Value Investment Agent | Section 6 `state_transition` reads the parsed category | Second speaker is the specialist matching the category; the other specialist never appears in `speaker_order` | "[StateFlow] Portfolio category = ..." followed by the matching agent |
| R6 | Dynamic workflow management is reliable (StateFlow is a deterministic state machine, not an LLM guess) | Section 6 self-test with synthetic group chats | Both branches, the no-category fallback (defaults to Value) and the terminal state (`None`) verified without an LLM | "StateFlow self-test: PASS" |
| R7 | Step 5: Growth / Value Investment Agent provides specific investment recommendations | Section 5 prompts (4-5 options with allocation, rationale, risk) | Specialist reply contains "recommend" and is substantive (> 200 chars) | Options, allocations and risks are listed |
| R8 | Step 6: Investment Advisor Agent compiles a detailed report from the previous agents' insights | Section 6 StateFlow (specialist → advisor → end) | `speaker_order == [Portfolio_Analysis_Agent, <specialist>, Investment_Advisor_Agent]` | Advisor speaks last |
| R9 | Workflow ends cleanly (StateFlow terminates the chat) | Section 7 manager stops when StateFlow returns `None` | `ended_by_stateflow` is True and rounds ≤ `MAX_ROUND` | "StateFlow returned None ... conversation complete" |
| R10 | Group Chat for collaboration: agents collaborate through a group chat managed by the manager | Section 7: each speaker receives the full transcript | Each message's `visible_messages` equals its position (every speaker saw everything before it) | "sees N messages" increases each round |
| R11 | Expected output: a personalized report including portfolio analysis and growth/value investment suggestions | Section 5 advisor prompt with fixed headings | All five headings present (`Portfolio Analysis`, `Investment Category`, `Recommended Investments`, `Action Plan`, `Disclaimer`) and the chosen category is named | Report reads as a complete plan |
| R12 | "Display the output of the Investment Advisor Agent" | Section 9 renders the advisor's message with `IPython.display.Markdown` | `final_report` is non-empty | Rendered report visible under section 9 |

## Non-functional expectations

| Expectation | How it is met |
|---|---|
| Runs end to end in Google Colab | Top-level `await` (supported by Colab), `Runtime → Run all`, defaults accepted with Enter |
| API key via Colab Secrets with an optional manual entry | Section 2: Colab `userdata` → environment variable → hidden `getpass` prompt; key is never printed, provider errors reduced to their type name |
| Current framework and pinned dependencies | `ag2[openai]==1.1.2` (AG2 1.x) installed with `uv` |
| Model availability | `MODEL_CANDIDATES` probed in order; a clear error if none is reachable |
| Simple and easy to use | One settings cell (`MODEL_CANDIDATES`, `MAX_ROUND`, `INTERACTIVE_INPUT`, `DEFAULT_INPUTS`); group chat + StateFlow in ~60 lines of plain Python |
| Safe decision logic | Routing uses exact matching on the `CATEGORY:` line; no LLM gates the workflow decision; financial output carries a disclaimer |
