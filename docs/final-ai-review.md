# Final AI Review and Ownership Evidence

This review is grounded in the final `app/` and `frontend/` layout and the structure refactor in commit `31acf50`.

## AGENTS.md guardrails

- **Repo-specific stack and commands included**: yes
- **Docs-first/read-first guardrail included**: yes
- **Unexpected `app/`/`frontend/` edits rule included**: yes; minimal fixes must be explicitly requested and documented here.

## AI code review mini-log

Reviewed diff: commit `31acf50`, which moved the backend into `app/` and the UI into `frontend/`.

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| Use package-qualified imports and keep a compatibility fallback in `app/main.py`. | **Useful** | The package import works from the repository and the fallback preserves direct-module compatibility. | Accepted; the 47-test suite and Docker image both pass. |
| Resolve frontend paths relative to the module instead of the process working directory. | **Useful** | Absolute repository-relative resolution makes `/` reliable when Uvicorn starts from another directory. | Accepted; `/` and `/frontend/app.js` returned 200. |
| Remove explanatory comments from the frontend during the move. | **Noise** | It changes readability without improving runtime behavior. | Accepted only where harmless; no product behavior depends on comment removal. |

## AI security mini-review

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| Runtime process should not run as root. | [Dockerfile](../Dockerfile#L28) and `USER app` at [line 45](../Dockerfile#L45) | **Valid** | Least privilege limits the impact of a container compromise. | Kept the non-root runtime and verified `docker exec tt-app whoami` → `app`. |
| Environment files were not excluded from the build context. | [.dockerignore](../.dockerignore#L1) | **Valid** | `.env` files can contain credentials even when the Dockerfile does not explicitly copy them. | Added `.env` and `.env.*` exclusions; the Dockerfile copies only `app/`, `frontend/`, and `run.py`. |
| The in-memory task dictionary stores plaintext authentication credentials. | [app/main.py](../app/main.py#L38) | **False Positive** | This application has no authentication or credential fields; the store contains public task entities only. | Kept in-memory storage because authentication and a production database are out of scope. |

## Manual security check

I inspected tracked files for common private-key and API-token patterns, confirmed no `.env` files are tracked, built the image, checked `/health`, and verified the container identity as `app`. I also confirmed that the frontend renders user values with DOM text APIs rather than injecting task content as HTML.

## One AI output I rejected or corrected

An AI review suggested treating `description: null` as “no update.” That would make the Edit flow unable to clear a description. I corrected the route to distinguish an absent field from an explicit null using `model_fields_set`, added `test_update_can_clear_description_with_explicit_null`, and preserved the existing partial-update behavior for omitted fields.

## Three AI usage rules

1. **Never paste**: API keys, `.env` secrets, database credentials, production logs, or personal/customer data.
2. **Always verify**: Run the full test suite, inspect diffs, and verify Docker health and runtime identity before accepting a change.
3. **Record AI contributions by**: Naming the changed file or diff, grading suggestions as Useful/Noise/Wrong, and documenting the human decision.

## Ownership statement

I understand the final application structure, API contracts, validation rules, state transitions, and container runtime configuration. I reviewed the refactor, corrected the description-clear behavior, and verified the result with tests, route smoke checks, and Docker checks. AI assisted with drafts and review prompts, but I made and can explain the final engineering and documentation decisions.
