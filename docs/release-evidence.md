# Release Evidence

## Baseline

- **Branch**: `final-project` (clean and tracking `origin/final-project`)
- **Date**: 2026-08-21
- **Local app run command**: `.venv/bin/python -m uvicorn app.main:app --reload --port 8000` or `.venv/bin/python run.py`
- **`/health` result**: `HTTP 200 OK` with `{"status":"ok"}`
- **Frontend check**: The baseline browser check opened `http://localhost:8000/` and confirmed the Kanban columns, inline create form, edit/delete actions, tag chips, search, and timeline filters. The current route smoke check returned 200 for `/` and `/frontend/app.js`.
- **Test command**: `.venv/bin/python -m pytest -v`
- **Test result**: 47/47 tests passed; one Starlette deprecation warning was emitted by the installed TestClient dependency.

## CI evidence

- **Workflow file**: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- **Latest green run**: [final-project CI run 32417098848](https://github.com/he-55/Mid-Course-Project-AI-Assisted-Feature-Extension-Sprint/actions/runs/32417098848), completed successfully after the `app/` and `frontend/` refactor.
- **Test command used by CI**: `pytest -v`
- **Workflow checks**: Python 3.11 is explicit, dependencies are installed from `requirements.txt`, and pytest runs on both push and pull request. No `continue-on-error`, `|| true`, skipped pytest command, or vague Python version is present.

## Docker evidence

- **Build command**: `docker build -t task-tracker .`
- **Build result**: Completed successfully for the current Dockerfile.
- **Run command**: `docker run --rm -d -p 8000:8000 --name tt-app task-tracker`
- **`/health` check**: `curl -i http://127.0.0.1:8000/health` returned `HTTP/1.1 200 OK` and `{"status":"ok"}`.
- **Non-root check**: `docker exec tt-app whoami` returned `app`; the inspected container configuration also used `app`.
- **No-baked-secrets check**: `.dockerignore` excludes `.env` and `.env.*`; the Dockerfile copies only `app/`, `frontend/`, and `run.py` into the runtime image.
- **Runtime command**: The image starts `uvicorn app.main:app --host 0.0.0.0 --port 8000` as defined in [Dockerfile](../Dockerfile#L54).

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made |
|---|---|---|---|
| The documented application entrypoint works | `run.py`, `app/main.py`, and the route smoke check | **PASS**: `/health`, `/`, and `/frontend/app.js` are available from the current package layout. | Updated repository instructions from `main:app`/`static` to `app.main:app`/`frontend`. |
| The API enforces workflow and validation rules | [app/main.py](../app/main.py#L59), [app/schemas.py](../app/schemas.py#L58), and 47 pytest tests | **PASS**: backward status moves return 400; invalid payloads return 422. | Added boundary and edit-clear regression tests. |
| The Docker image is safe to run | [Dockerfile](../Dockerfile#L28), [.dockerignore](../.dockerignore#L1), and the current build/run checks above | **PASS**: image builds, serves health 200, runs as `app`, and excludes environment files from context. | Added `.env` and `.env.*` exclusions. |
| The CI workflow runs the full suite | [.github/workflows/ci.yml](../.github/workflows/ci.yml#L3) and the linked GitHub Actions run | **PASS**: final-project run completed successfully. | Added the current run link here. |
| Editing can clear a description | [frontend/app.js](../frontend/app.js#L439) and [app/main.py](../app/main.py#L159) | **PASS** after correction: explicit `description: null` now clears the stored value, while an absent field preserves it. | Updated the route and added a regression test. |
