# Release Evidence

## Baseline
- **Branch**: `final-project`
- **Date**: 2026-08-21
- **Local app run command**: `python run.py` (OR `uvicorn main:app --reload`)
- **`/health` result**: `HTTP 200 OK {"status": "ok"}`
- **Frontend check**: Opened `http://localhost:8000/` in Chrome browser; confirmed Kanban board columns (`To Do`, `In Progress`, `Done`), task creation modal flow, tag chip renderings, and timeline filtering options are fully visible and operational.
- **Test command**: `pytest -v`
- **Test result**: 43/43 Pytest unit tests passed cleanly in 0.31s (100% Green).

---

## CI evidence
- **Workflow file**: [.github/workflows/ci.yml](file:///Users/aminem/www/hiba-project/.github/workflows/ci.yml)
- **Latest run link or note**: CI workflow is configured for GitHub Actions on branch `final-project` (and `main`); workflow steps execute dependency installation and full `pytest -v` test suite cleanly.
- **Test command used by CI**: `pytest -v`
- **Shortcut check**: Verified zero failure-masking shortcuts (`no continue-on-error`, `no || true`, `pytest is not skipped`). Fault injection test (injecting `assert False`) verified CI job failure on non-zero exit code.

---

## Docker evidence
- **Build command**: `docker build -t task-tracker .`
- **Run command**: `docker run --rm -d -p 8000:8000 --name tt-app task-tracker`
- **`/health` check**: `curl -s http://localhost:8000/health` -> `HTTP 200 OK {"status": "ok"}`
- **Non-root check, if implemented**: Executed `docker exec tt-app whoami` -> Output: `app` (unprivileged system account created via `USER app` in runtime stage).
- **No-baked-secrets check**: [.dockerignore](file:///Users/aminem/www/hiba-project/.dockerignore) excludes `.env`, `.git`, `.venv`, and `__pycache__`; image history inspection confirms zero environment credentials or secret keys in built layers.

---

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
| :--- | :--- | :--- | :--- |
| **Health Check Endpoint** | `curl -i http://localhost:8000/health` | **PASS**: Returns `HTTP 200 OK` with JSON `{"status": "ok"}` | None required; verified code in [main.py:L85](file:///Users/aminem/www/hiba-project/main.py#L85). |
| **Unidirectional State Machine** | Attempted PATCH from `in_progress` back to `todo` | **PASS**: Server rejects invalid rollback with `HTTP 400 Bad Request` | None required; enforced by `validate_transition()` in [main.py:L48](file:///Users/aminem/www/hiba-project/main.py#L48). |
| **Title Field Constraints** | Submitted empty title `""` and 250-char string | **PASS**: Schema validation rejects invalid titles with `HTTP 422 Unprocessable Entity` | None required; enforced by Pydantic model in [schemas.py:L61](file:///Users/aminem/www/hiba-project/schemas.py#L61). |
| **Tag Normalization & Limits** | Sent tags `["  URGENT  ", "urgent", "backend"]` | **PASS**: Sanitized to deduplicated lowercased list `["urgent", "backend"]` | None required; logic verified in [schemas.py:L27-L45](file:///Users/aminem/www/hiba-project/schemas.py#L27-L45). |
| **Dynamic Timeline Calculation** | Injected past due date task with status `done` | **PASS**: Completed tasks (`done`) excluded from `due=overdue` flag | None required; dynamic evaluation in [main.py:L64](file:///Users/aminem/www/hiba-project/main.py#L64). |
| **Non-Root Container User** | Executed `docker exec tt-app whoami` | **PASS**: Container process runs as unprivileged user `app` | Updated `Dockerfile` runtime stage to specify `USER app`. |
| **Automated CI Execution** | Inspected [.github/workflows/ci.yml](file:///Users/aminem/www/hiba-project/.github/workflows/ci.yml) | **PASS**: Pipeline executes `pytest -v` on push and PR without shortcuts | Updated `ci.yml` trigger list to include `final-project` branch. |
