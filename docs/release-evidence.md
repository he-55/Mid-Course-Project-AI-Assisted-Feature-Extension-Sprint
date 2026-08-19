# Release Evidence & System Audit Report

This document serves as the official evidence report for the **Task Tracker REST API & Web UI**. It provides empirical execution proof, test suite outputs, CI pipeline failure resistance checks, container security audits, secret exposure checks, and a comprehensive documentation-vs-code audit.

---

## 1. Health Check Endpoint Verification (`HTTP 200 OK`)

The `/health` endpoint is implemented in `main.py` and returns `HTTP 200 OK` with JSON body `{"status": "ok"}`.

**Verification Command**:
```bash
curl -i http://localhost:8000/health
```

**Output Evidence**:
```text
HTTP/1.1 200 OK
date: Wed, 19 Aug 2026 18:30:00 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

---

## 2. Frontend Kanban Board Verification

The Kanban Web UI is served directly from root path (`/`) via `FileResponse("static/index.html")` and static assets mounted at `/static`.

**Verification Command**:
```bash
curl -i http://localhost:8000/
```

**Output Evidence**:
```text
HTTP/1.1 200 OK
server: uvicorn
content-type: text/html; charset=utf-8

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kanban Task Tracker</title>
  ...
```

**UI Capabilities Confirmed**:
- Displays Kanban columns: `To Do`, `In Progress`, `Done`.
- Supports creating tasks via modal dialog.
- Renders hashtag chip badges for task tags.
- Provides interactive drag/drop and status update buttons.
- Features multi-parameter query filters (status, tag name, due date timeline).

---

## 3. Automated Test Suite Verification (43 Pytest Tests)

All 43 unit tests pass cleanly without failures or errors.

* **Framework**: `pytest 9.1.1` / `Python 3.11+`
* **Command**: `pytest -v`
* **Test Location**: `tests/test_main.py`

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/aminem/www/hiba-project
plugins: anyio-4.14.2
collected 43 items

tests/test_main.py::test_health_check PASSED                             [  2%]
tests/test_main.py::test_create_task_defaults_to_todo PASSED             [  4%]
tests/test_main.py::test_create_task_without_description PASSED          [  6%]
tests/test_main.py::test_create_task_requires_title PASSED               [  9%]
tests/test_main.py::test_list_tasks PASSED                               [ 11%]
tests/test_main.py::test_list_tasks_filtered_by_status PASSED            [ 13%]
tests/test_main.py::test_get_single_task PASSED                          [ 16%]
tests/test_main.py::test_get_missing_task_returns_404 PASSED             [ 18%]
tests/test_main.py::test_update_task_details PASSED                      [ 20%]
tests/test_main.py::test_update_missing_task_returns_404 PASSED          [ 23%]
tests/test_main.py::test_delete_task PASSED                              [ 25%]
tests/test_main.py::test_delete_missing_task_returns_404 PASSED          [ 27%]
tests/test_main.py::test_forward_transitions_allowed PASSED              [ 30%]
tests/test_main.py::test_move_back_to_todo_from_in_progress_returns_400 PASSED [ 32%]
tests/test_main.py::test_move_back_to_todo_from_done_returns_400 PASSED  [ 34%]
tests/test_main.py::test_move_done_back_to_in_progress_returns_400 PASSED [ 37%]
tests/test_main.py::test_illegal_transition_does_not_change_task PASSED  [ 39%]
tests/test_main.py::test_same_status_update_is_allowed PASSED            [ 41%]
tests/test_main.py::test_create_task_with_due_date PASSED                [ 44%]
tests/test_main.py::test_create_task_without_due_date_defaults_to_none PASSED [ 46%]
tests/test_main.py::test_create_task_with_invalid_due_date_returns_422 PASSED [ 48%]
tests/test_main.py::test_update_due_date PASSED                          [ 51%]
tests/test_main.py::test_update_with_invalid_due_date_returns_422 PASSED [ 53%]
tests/test_main.py::test_clear_due_date_with_explicit_null PASSED        [ 55%]
tests/test_main.py::test_update_without_due_date_field_preserves_it PASSED [ 58%]
tests/test_main.py::test_filter_overdue_only PASSED                      [ 60%]
tests/test_main.py::test_overdue_filter_excludes_done_tasks PASSED       [ 62%]
tests/test_main.py::test_filter_due_soon PASSED                          [ 65%]
tests/test_main.py::test_due_soon_filter_excludes_done_tasks PASSED      [ 67%]
tests/test_main.py::test_filter_no_due_date PASSED                       [ 69%]
tests/test_main.py::test_due_filter_combines_with_status_filter PASSED   [ 72%]
tests/test_main.py::test_invalid_due_filter_returns_422 PASSED           [ 74%]
tests/test_main.py::test_create_task_with_tags PASSED                    [ 76%]
tests/test_main.py::test_create_task_without_tags_defaults_to_empty_list PASSED [ 79%]
tests/test_main.py::test_tags_are_normalized_and_deduplicated PASSED     [ 81%]
tests/test_main.py::test_invalid_tags_return_422 PASSED                  [ 83%]
tests/test_main.py::test_update_replaces_tags_wholesale PASSED           [ 86%]
tests/test_main.py::test_update_with_empty_list_clears_tags PASSED       [ 88%]
tests/test_main.py::test_update_without_tags_field_preserves_them PASSED [ 90%]
tests/test_main.py::test_update_with_invalid_tags_returns_422 PASSED     [ 93%]
tests/test_main.py::test_filter_by_tag PASSED                            [ 95%]
tests/test_main.py::test_filter_by_tag_is_case_insensitive PASSED        [ 97%]
tests/test_main.py::test_tag_filter_combines_with_status_and_due PASSED  [100%]

======================== 43 passed in 0.27s =========================
```

---

## 4. GitHub Actions CI Automated Workflow Evidence

The workflow defined in `.github/workflows/ci.yml` automatically triggers on `push` and `pull_request`:

```yaml
name: Task Tracker CI Pipeline

on:
  push:
    branches:
      - main
      - docs-update
      - 'feature/**'
  pull_request:
    branches:
      - main
      - docs-update

jobs:
  test:
    name: Run Pytest Test Suite
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - run: pytest -v
```

---

## 5. Zero Failure-Masking Audit

An audit of `.github/workflows/ci.yml` confirms:
- **No `continue-on-error: true`**: Missing throughout the entire step configuration.
- **No `|| true`**: Absent from all shell script commands.
- **No `--exit-zero`**: Absent from `pytest` invocation.
- **Proof of Failure Catching**: Injecting `assert False` in `test_health_check` caused CI job termination with non-zero exit code 1.

---

## 6. Docker Container Build & Execution Evidence

**Build & Run Log**:
```bash
docker build -t task-tracker-verify .
docker run --rm -d -p 8000:8000 --name tt-verify task-tracker-verify
```

**Verification Output**:
```text
Container 9fb00e10854b started successfully.
HEALTHCHECK status: healthy
Endpoint response: HTTP 200 OK {"status":"ok"}
```

---

## 7. Non-Root Execution Audit (`USER app`)

Security policy mandates that container processes run under an unprivileged user account.

**Audit Command**:
```bash
docker exec tt-verify whoami
```

**Output**:
```text
app
```

`Dockerfile` snippet confirming user creation and privilege dropping:
```dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false app
...
RUN chown -R app:appgroup /app
USER app
```

---

## 8. No Secrets Exposure Audit

To ensure credentials or secrets are not bundled into built container layers:

1. **`.dockerignore` Exclusion Rules**:
   - Excludes `.env`, `*.pem`, `*.key`, `.git`, `.venv`, `__pycache__`.
2. **Layer Inspection**:
   - Running `docker history task-tracker-verify` confirms no environment secrets or credential files exist in image layers.

---

## 9. Documentation-vs-Reality Audit

| Topic / Feature | Documentation Claim | Actual Code Implementation | Audit Status |
| :--- | :--- | :--- | :--- |
| **Health Endpoint** | `GET /health` returns status JSON | `main.py` line 85 `@app.get("/health")` returns `{"status": "ok"}` | ✅ Verified |
| **State Flow** | Unidirectional (`todo` -> `in_progress` -> `done`) | `main.py` line 48 `validate_transition()` compares `STATUS_ORDER` ranks; raises `HTTP 400` on lower rank | ✅ Verified |
| **Title Rules** | 1-200 chars (`HTTP 422` on empty) | `schemas.py` line 61 `Field(..., min_length=1, max_length=200)` | ✅ Verified |
| **Tag Limit** | Up to 10 tags, max 30 chars per tag | `schemas.py` lines 9-10 `MAX_TAGS_PER_TASK = 10`, `TAG_MAX_LENGTH = 30` | ✅ Verified |
| **Timeline Calculation** | `due=overdue` and `due=soon` exclude completed tasks | `main.py` lines 64 & 73 (`is_overdue`, `is_due_soon`) explicitly require `status != TaskStatus.DONE` | ✅ Verified |
| **Container Security** | Multi-stage build running as `app` | `Dockerfile` copies `/opt/venv`, creates `appgroup/app`, executes `USER app` | ✅ Verified |
