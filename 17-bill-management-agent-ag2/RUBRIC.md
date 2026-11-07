# Assignment 17 — Bill Management Agent: Rubric

Every expectation in the assignment brief maps to one row. The notebook's last cell runs the automated check for each row and prints `PASS` / `FAIL`; the "Manual check" column is what a reviewer can confirm by reading the transcript.

| # | Expectation (assignment text) | Evidence in the notebook | Automated check | Manual check |
|---|---|---|---|---|
| R1 | User Proxy Agent "gives the image of the bills that need to be processed" (inputs are real, validated image files) | Section 4 generates or loads the bill images; Section 5 `validate_bill_images` (exists, image extension, ≤ 10 MB) | ≥ 1 image held by the proxy; should-fail self-test: missing file, `.txt` file, empty list all raise `ValueError` | Sample bills are displayed; "validation self-test: PASS" |
| R2 | User Proxy Agent initiates a conversation with the Group Manager: "a message to the group manager regarding the image that has to be processed" | Section 8 `user_proxy.initiate_chat(group_manager, message=...)` | First group-chat message is from the User Proxy and mentions the bill images | Transcript starts with `User_Proxy_Agent -> Group_Manager (+3 image(s))` |
| R3 | Bill Processing Agent "takes the input image from the Group Manager" | Section 7 manager attaches the images to vision agents; image count read back from AG2's `ModelRequest` | First speaker is the Bill Processing Agent and `images_sent` equals the number of bills | "Round 1: next speaker -> Bill_Processing_Agent (... 3 image(s))" |
| R4 | Bill Processing Agent "extracts data from uploaded bill images and organizes expenses into categories (groceries, dining, utilities, shopping, entertainment)" | Section 6 prompt with the fixed category list and a mandatory JSON block | JSON parsed; ≥ 3 items, every item has an allowed category and a positive amount | Table lists each bill's items with categories |
| R5 | Expected output: "a categorized list of all expenses with the total amount spent" (total is correct) | Section 9 recomputes the total from the items | Stated `total` equals the sum of item amounts (± 0.01) | "**Total amount spent:**" line matches the table |
| R6 | Extraction is accurate (bill data is read, not guessed) | Section 4 keeps the sample bills' ground-truth totals | Computed total within 1% of the known total 144.92 (skipped automatically when using your own bills) | Compare the table with the displayed receipts |
| R7 | "Processed data moves to Expense Summarization Agent" (input = categorized list from the Bill Processing Agent) | Section 7 manager sends the full transcript to the next speaker | Second speaker is the Summarization Agent and it saw 2 messages (user + bill agent) | "Round 2: next speaker -> Expense_Summarization_Agent (sees 2 messages)" |
| R8 | Summarization Agent "provides a breakdown of total spending per category" | Section 6 summarization prompt (table per category + grand total) | "Spending by category" section present and every category from the JSON is named | Table rows per category with totals and shares |
| R9 | Expected output: "showing which category has the highest expenditure" | Mandatory `**Highest category:**` line | Stated highest category equals the deterministic maximum computed from the JSON | Highest category line matches the table |
| R10 | "Highlights any unusual or high spending trends" | Insights section in the prompt | "Insights" section present with unusual / high / largest language | Bullets call out the biggest item and a saving suggestion |
| R11 | "Group Chat Agent Collaboration" with a "sequential conversational experience" | Section 7 `GroupChat` + `GroupChatManager` + `state_transition` | Speaker order is exactly Bill Processing → Summarization, every message saw all previous ones, flow ended via the transition function | Manager log shows the rounds and "Flow complete" |
| R12 | Final output makes bill management "insightful and actionable" and is shown to the user | Section 9 renders both agent outputs with `IPython.display.Markdown` | Both outputs non-empty | Rendered report with the categorized table, summary and deterministic check line |

## Non-functional expectations

| Expectation | How it is met |
|---|---|
| Runs end to end in Google Colab, unattended | Sample bills are generated with Pillow, so `Runtime → Run all` needs no uploads; `USE_SAMPLE_BILLS = False` switches to your own images (Colab upload dialog or `./my_bills`) |
| API key via Colab Secrets with an optional manual entry | Section 2: Colab `userdata` → environment variable → hidden `getpass` prompt; key never printed, provider errors reduced to their type name |
| Current framework and pinned dependencies | `ag2[openai]==1.1.2` (AG2 1.x, images via `ImageInput`) installed with `uv` |
| Model availability | Vision-capable `MODEL_CANDIDATES` probed in order; a clear error if none is reachable |
| Trust boundary on inputs | User files validated before anything is sent to the model; model output parsed with exact JSON/regex rules and re-checked arithmetically, so the LLM never gates the totals |
