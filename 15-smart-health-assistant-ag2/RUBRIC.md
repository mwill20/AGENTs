# Assignment 15 — Smart Health Assistant: Rubric

Every expectation in the assignment brief maps to one row. The notebook's last cell runs the automated check for each row and prints `PASS` / `FAIL`; the "Manual check" column is what a reviewer can confirm by reading the transcript.

| # | Expectation (assignment text) | Evidence in the notebook | Automated check | Manual check |
|---|---|---|---|---|
| R1 | "Use these agents in the sequence mentioned" (sequential conversation pattern) | Section 7: User Proxy calls BMI Agent → Diet Planner → Workout Scheduler in order, each receiving the previous output | Chat log recipients == `[BMI_Agent, Diet_Planner_Agent, Workout_Scheduler_Agent]` | Transcript banners appear in that order |
| R2 | Step 1: User Proxy Agent collects weight (kg), height (cm), age, gender, dietary preference (Veg / Non-Veg / Vegan) | Section 4: `UserProxyAgent.collect()` prompts for all five values (Enter accepts the default) | `profile` is a `UserProfile` with gender and diet in the allowed sets | "Collected: {...}" line shows all five fields |
| R3 | Data collection is reliable (inputs validated, not blindly trusted) | Section 4: `validate_profile` enforces ranges and allowed values | Should-fail self-test: weight 0, age 300, gender "Robot", diet "Keto" all raise `ValueError` | Self-test line prints PASS |
| R4 | Step 2: BMI tool converts height cm → m (`height_cm / 100`) and computes `BMI = kg / m²` | Section 5: `calculate_bmi` | Known values (70 kg / 175 cm → 22.9; 82 / 175 → 26.8; 180 cm → 1.8 m) and should-fail cases (zero / negative inputs raise) | Tool result in transcript matches a hand calculation |
| R5 | "The BMI tool should be registered to the BMI Agent" | Section 6: `Agent(BMI_AGENT, ..., tools=[bmi_tool])`; other agents have no tools | `bmi_tool in bmi_agent.tools` and the other two agents' tool lists are empty | Tools summary printed after agent creation |
| R6 | BMI tool "shares the results with the BMI Agent" (tool is actually used, not bypassed) | Section 7 transcript shows `>>> BMI_Agent called tool calculate_bmi ...` and its result | Tool result's `bmi` equals an independent re-computation from the profile, and that value appears in the BMI Agent's reply | Tool-call lines visible in transcript |
| R7 | Step 3: BMI Agent finds the BMI category and suggests recommendations | Section 6 BMI Agent prompt (WHO categories, recommendations section) | Reply contains a category word and "recommend" | Reply has `**BMI:**`, `**Category:**`, `**Health recommendations:**` |
| R8 | Step 4 inputs: BMI insights from the BMI Agent + dietary preference from the User Proxy Agent | Section 7: Diet Planner message is built from `bmi_insights` and `profile.diet_preference` | Both strings are present in the message sent to the Diet Planner | Transcript message to Diet Planner shows both |
| R9 | Step 4: Diet Planner suggests a tailored meal plan | Section 6 Diet Planner prompt (goal line + Meal / Foods / Why table) | Reply names ≥2 of breakfast / lunch / dinner and mentions the dietary preference | Meals respect the preference (e.g. no meat for Veg) |
| R10 | Step 5 inputs: meal plan from the Diet Planner + age and gender from the User Proxy Agent | Section 7: Workout message is built from `meal_plan`, `profile.age`, `profile.gender` | Meal plan, `Age: N` and `Gender: X` are present in the message sent to the Workout Scheduler | Transcript message to Workout Scheduler shows all three |
| R11 | Step 5: Workout Scheduler creates a weekly workout plan | Section 6 Workout Scheduler prompt (Monday–Sunday table, rest day) | Reply mentions ≥5 day names | Table covers the week and includes a rest / recovery day |
| R12 | Expected output: complete health plan with BMI insights, a tailored diet and a fitness schedule | Section 8 renders `final_plan` with `IPython.display.Markdown` | `final_plan` starts with a Markdown title and contains all three agent outputs verbatim | Rendered plan is readable and complete |

## Non-functional expectations

| Expectation | How it is met |
|---|---|
| Runs end to end in Google Colab | Top-level `await` (supported by Colab), `Runtime → Run all`, defaults accepted with Enter |
| API key via Colab Secrets with an optional manual entry | Section 2: Colab `userdata` → environment variable → hidden `getpass` prompt; key is never printed, and provider errors are reduced to their type name so no key fragment can leak |
| Current framework and pinned dependencies | `ag2[openai]==1.1.2` (AG2 1.x, released 2026-10-03) installed with `uv` |
| Model availability | `MODEL_CANDIDATES` probed in order; a clear error if none is reachable |
| Simple and easy to use | One settings cell (`MODEL_CANDIDATES`, `INTERACTIVE_INPUT`, `DEFAULT_PROFILE`); no extra frameworks |
