# Security: Python Code Analysis and Correction with CrewAI

A single-user notebook in which an LLM agent **executes Python on the host** through a
`CodeInterpreterTool`, and the notebook then executes the LLM's corrected code to verify it. That
makes this the highest-risk project in the repository alongside Project 11, and the one to read
most carefully before adapting. It is not a deployed service.

## Trust boundaries

| Boundary | Data crossing it | Trust level |
|---|---|---|
| Notebook constant -> validation | `BUGGY_CODE`, a fixed string in the notebook | Operator-controlled today; validated for type, emptiness and size anyway |
| Notebook -> OpenAI | The code, the specification, task descriptions, planning prompts, API key | Third-party processing |
| OpenAI -> notebook | Error analysis, corrected code, tool-call requests | Untrusted model output |
| Code Analyzer -> `CodeInterpreterTool` -> host | **Python source written by the model**, run in a subprocess | **Untrusted code execution on the host** |
| Corrector output -> verification harness -> host | The fenced ```python block, run in the same tool | Same |
| Notebook -> reader | Rendered Markdown | Untrusted until a human reads it |

The input code is a constant, so there is no external attacker in the delivered build. The model
is still an untrusted author of code that runs on your machine, twice: once when the Analyzer tests
the buggy code, and once when the notebook verifies the fix.

## Controls present in the code

| Threat | Control |
|---|---|
| Hardcoded or leaked keys | Colab Secrets, then environment variable, then hidden `getpass`; only "API key loaded." is printed. Model probe errors are reduced to their type name |
| Telemetry, trace upload, version check | `CREWAI_TRACING_ENABLED=false`, `OTEL_SDK_DISABLED=true`, `CREWAI_DISABLE_VERSION_CHECK=true`, so the only network traffic is to OpenAI |
| Oversized or malformed input | `validate_code`: must be a non-empty `str` of at most `MAX_CODE_CHARS` (20,000). Four should-fail cases asserted |
| Runaway or hung execution | `subprocess.run(..., timeout=TOOL_TIMEOUT_SECONDS)` (10 s); the self-test proves an infinite loop is killed |
| Interpreter picking up planted modules | `python -I` (isolated mode: ignores `PYTHON*` environment variables and the user site, and does not put the script directory on `sys.path`), `cwd` set to a fresh temporary directory |
| Output flooding the context | stdout and stderr truncated to the last 4,000 characters each |
| Model declaring success | Section 10 extracts the fenced block with a strict regex and runs it against fixed expected values for six inputs; the final check is that result, not the agent's claim |
| Tool reachable from the wrong agent | Only `code_analyzer` has the tool; the check cell asserts `code_corrector.tools` is empty |
| Runaway reasoning and cost | `max_iter` 8 / 5 on the worker agents |
| Dependency drift | `crewai==1.15.33` pinned |

## Known gaps

- **The subprocess inherits the API key.** Section 2 exports `OPENAI_API_KEY` into `os.environ`, and
  the tool calls `subprocess.run` without an `env=` argument, so model-written code runs with the
  key in its environment (`python -I` only drops `PYTHON*` variables). Nothing in the saved run
  read it, but a prompt-injected snippet could. Pass a minimal environment (for example
  `env={"PATH": os.environ["PATH"]}`) before reusing this tool on untrusted code.
- **The tool is not a sandbox.** `python -I` with a timeout stops accidental hangs and import
  hijacks. It does **not** stop the code from reading or deleting files, opening network
  connections, or consuming memory. Any code the model writes runs with your user's permissions.
  In the delivered build the model is only ever asked to run a fixed Fibonacci function, which
  bounds the realistic risk, but a different prompt or a different input changes that completely.
- **If `BUGGY_CODE` is ever made user-supplied**, this becomes remote code execution by way of the
  model: an attacker's code goes to the Analyzer, which is instructed to run it. Treat the input
  as hostile and run the tool in a real sandbox (container, seccomp, no network) before doing that.
- **The verification harness trusts the fenced block to be the whole answer.** A corrected
  function that passes the six inputs could still contain unrelated code; the harness only checks
  return values.
- **The Manager does not manage.** With `Process.sequential`, CrewAI runs the tasks itself and
  `manager_agent` is attached but does not delegate; coordination comes from `planning=True`. The
  author documents this. Switching to `Process.hierarchical` would give the manager
  `allow_delegation=True` authority over the two workers and should be reviewed as a change to the
  threat model.
- **The saved tool output contains a temporary path** from the author's Colab session
  (`/tmp/...`). It is harmless but shows that run outputs leak environment details.
- **No audit logging** beyond the printed outputs; **no spend cap** beyond `max_iter`.

## Do not

- Commit a real API key, or paste one into a notebook cell.
- Point this notebook at code you did not write, or let anyone else supply `BUGGY_CODE`, without
  moving execution into a sandbox first.
- Remove the timeout, the `-I` flag or the size cap to "make it work" on a bigger input.

## Reporting a vulnerability

Open a GitHub issue on this repository. For anything sensitive, contact the maintainer through the
GitHub profile at https://github.com/mwill20.
