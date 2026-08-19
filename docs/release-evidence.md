# System Release Verification & Audit Artifacts

This document serves as the official audit log and verification record for the Task Tracker REST API application. It details empirical execution proof, test suite output, CI pipeline resilience checks, container security audits, and adversarial break tests.

---

## 1. Local Test Suite Verification Log

All 43 unit tests pass cleanly without errors or regressions.

* **Test Framework**: `pytest 9.1.1` / `Python 3.11+`
* **Test Runner Command**: `pytest -v`
* **Coverage Scope**: Health checks, Task CRUD operations, state transition constraints, tag sanitization, and timeline filters (`due=overdue`, `due=soon`, `due=none`).

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/aminem/www/hiba-project
plugins: anyio-4.14.2
collected 43 items

test_main.py::test_health_check PASSED                                   [  2%]
test_main.py::test_create_task_defaults_to_todo PASSED                   [  4%]
test_main.py::test_create_task_without_description PASSED                [  6%]
test_main.py::test_create_task_requires_title PASSED                     [  9%]
test_main.py::test_list_tasks PASSED                                     [ 11%]
test_main.py::test_list_tasks_filtered_by_status PASSED                  [ 13%]
test_main.py::test_get_single_task PASSED                                [ 16%]
test_main.py::test_get_missing_task_returns_404 PASSED                   [ 18%]
test_main.py::test_update_task_details PASSED                            [ 20%]
test_main.py::test_update_missing_task_returns_404 PASSED                [ 23%]
test_main.py::test_delete_task PASSED                                    [ 25%]
test_main.py::test_delete_missing_task_returns_404 PASSED                [ 27%]
test_main.py::test_forward_transitions_allowed PASSED                    [ 30%]
test_main.py::test_move_back_to_todo_from_in_progress_returns_400 PASSED [ 32%]
test_main.py::test_move_back_to_todo_from_done_returns_400 PASSED        [ 34%]
test_main.py::test_move_done_back_to_in_progress_returns_400 PASSED      [ 37%]
test_main.py::test_illegal_transition_does_not_change_task PASSED        [ 39%]
test_main.py::test_same_status_update_is_allowed PASSED                  [ 41%]
test_main.py::test_create_task_with_due_date PASSED                      [ 44%]
test_main.py::test_create_task_without_due_date_defaults_to_none PASSED  [ 46%]
test_main.py::test_create_task_with_invalid_due_date_returns_422 PASSED  [ 48%]
test_main.py::test_update_due_date PASSED                                [ 51%]
test_main.py::test_update_with_invalid_due_date_returns_422 PASSED       [ 53%]
test_main.py::test_clear_due_date_with_explicit_null PASSED              [ 55%]
test_main.py::test_update_without_due_date_field_preserves_it PASSED     [ 58%]
test_main.py::test_filter_overdue_only PASSED                            [ 60%]
test_main.py::test_overdue_filter_excludes_done_tasks PASSED             [ 62%]
test_main.py::test_filter_due_soon PASSED                                [ 65%]
test_main.py::test_due_soon_filter_excludes_done_tasks PASSED            [ 67%]
test_main.py::test_filter_no_due_date PASSED                             [ 69%]
test_main.py::test_due_filter_combines_with_status_filter PASSED         [ 72%]
test_main.py::test_invalid_due_filter_returns_422 PASSED                 [ 74%]
test_main.py::test_create_task_with_tags PASSED                          [ 76%]
test_main.py::test_create_task_without_tags_defaults_to_empty_list PASSED [ 79%]
test_main.py::test_tags_are_normalized_and_deduplicated PASSED           [ 81%]
test_main.py::test_invalid_tags_return_422 PASSED                        [ 83%]
test_main.py::test_update_replaces_tags_wholesale PASSED                 [ 86%]
test_main.py::test_update_with_empty_list_clears_tags PASSED             [ 88%]
test_main.py::test_update_without_tags_field_preserves_them PASSED       [ 90%]
test_main.py::test_update_with_invalid_tags_returns_422 PASSED           [ 93%]
test_main.py::test_filter_by_tag PASSED                                  [ 95%]
test_main.py::test_filter_by_tag_is_case_insensitive PASSED              [ 97%]
test_main.py::test_tag_filter_combines_with_status_and_due PASSED        [100%]

======================== 43 passed in 0.27s =========================
```

---

## 2. CI Pipeline Integrity & Regressive Fault Injection

To verify that the GitHub Actions pipeline (`.github/workflows/ci.yml`) actively enforces test passing without silent masking:

1. **Baseline Passing Build**: Clean push triggered workflow execution; all 43 tests passed.
2. **Intentional Fault Injection**: Modified `test_health_check` to expect `{"status": "failure"}`. The CI workflow failed immediately with exit code 1.
3. **Restoration**: Correct assertion restored; CI pipeline returned to green state.

---

## 3. Container Security & Environment Isolation

Containerized deployment security was validated using the following steps:

```bash
# Build multi-stage image
docker build -t task-tracker-prod .

# Launch background container instance
docker run --rm -d -p 8000:8000 --name tt-sec-test task-tracker-prod

# Confirm process user is non-root
docker exec tt-sec-test whoami
# Output: app

# Confirm health endpoint status
curl -s http://localhost:8000/health
# Output: {"status":"ok"}

# Cleanup instance
docker stop tt-sec-test
```

---

## 4. Adversarial Break Test Summary

| Test Objective | Payload / Action | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| **Reverse State Transition** | Move task from `done` back to `todo` | `HTTP 400 Bad Request` | Verified |
| **Whitespace Title** | Create task with title `"   "` | `HTTP 422 Unprocessable Entity` | Verified |
| **Excessive Tag Length** | Create tag exceeding 30 characters | `HTTP 422 Unprocessable Entity` | Verified |
| **Tag Count Boundary** | Provide 11 unique tags in payload | `HTTP 422 Unprocessable Entity` | Verified |

---

## 5. Specification & Implementation Alignment Matrix

* **Unidirectional State Flow**: Enforced in `main.py` via `STATUS_ORDER` rank comparisons.
* **Non-Root Execution**: Enforced in `Dockerfile` via system user `app:appgroup`.
* **Zero Silent Failures**: Pipeline runs `pytest -v` without `continue-on-error` or error swallowing flags.
