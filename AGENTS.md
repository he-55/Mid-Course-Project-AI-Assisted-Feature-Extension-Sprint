# AGENTS.md - Repo-Level Instructions for AI Agents

This document defines repository context, tech stack commands, business rules, security rules, and Module 5 guardrails for AI coding assistants working on the Task Tracker REST API project.

---

## 1. Project Summary

The **Task Tracker REST API** is a lightweight task management system built with Python, FastAPI, Pydantic v2, and an in-memory repository (`_tasks` dictionary). It includes a responsive Kanban Web UI served directly from the root path (`/`) and static assets mounted at `/static`.

---

## 2. Tech Stack & Commands

| Component | Technology / Specification |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Framework** | FastAPI 0.110+ |
| **Data Validation** | Pydantic v2 (`BaseModel`, `ConfigDict`, `@field_validator`) |
| **Server** | Uvicorn |
| **Testing** | pytest, httpx (Starlette TestClient) |
| **Frontend** | Vanilla HTML5 / CSS3 / JavaScript (`static/index.html`) |

### Execution Commands (Run from Repository Root)
- **Install Dependencies**: `pip install -r requirements.txt`
- **Run API & Web UI Locally**: `python -m uvicorn main:app --reload --port 8000` OR `uvicorn main:app --reload`
- **Run Unit Test Suite**: `pytest -v` OR `.venv/bin/pytest -v`
- **Run Docker Container**: `docker build -t task-tracker .` && `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker`

---

## 3. Core Business & Validation Rules

1. **Task Statuses**: `todo`, `in_progress`, `done` (lowercase string enums in `TaskStatus`).
   - **Unidirectional State Transitions**: Tasks move strictly forward (`todo` -> `in_progress` -> `done`). Moving to a status with a lower rank (e.g. `in_progress` -> `todo`) is illegal and raises `HTTP 400 Bad Request`.
2. **Title Rules**: 1-200 characters (`min_length=1`, `max_length=200`). Invalid or empty titles raise `HTTP 422 Unprocessable Entity`.
3. **Description Rules**: Optional, up to 2000 characters (`max_length=2000`).
4. **Tags Rules**:
   - Up to 10 tags per task (`MAX_TAGS_PER_TASK = 10`).
   - Each tag must be 1-30 characters long (`TAG_MAX_LENGTH = 30`).
   - Blank or whitespace-only tags raise `HTTP 422 Unprocessable Entity`.
   - Tags are stored as a cleaned (trimmed, lowercased), deduplicated list preserving original input order.
5. **Due Date & Timeline Calculation**:
   - `due_date` is optional ISO format (`YYYY-MM-DD`).
   - **Overdue (`due=overdue`)**: `due_date < date.today()` and `status != done`. Completed tasks (`done`) are never marked overdue.
   - **Due Soon (`due=soon`)**: `due_date` within today to today + 2 days (`DUE_SOON_WINDOW_DAYS = 2`) and `status != done`.
   - **No Due Date (`due=none`)**: Tasks without a due date set.
6. **In-Memory Storage**: Tasks are stored in `_tasks: dict[int, dict]` in `main.py` using `itertools.count(1)` for sequential integer IDs starting at 1. `reset_store()` clears tasks for test isolation.

---

## 4. Module 5 Guardrails & Operational Constraints

1. **Docs-First & Read-Only Default**:
   - Primary deliverables live in `docs/`.
   - AI assistants must prefer read-only analysis and inspection over modifying source code.
   - Do NOT modify core files (`main.py`, `schemas.py`, `test_main.py`, `static/`) unless explicitly instructed for a specific minimal fix.
2. **One Task Per Thread**: Keep agent conversations focused on a single bounded objective. Do not mix setup, security audits, feature planning, and playbook drafting in one conversation thread.
3. **Repo-Grounded Evidence**:
   - Always cite actual file paths (`main.py`, `schemas.py`, `test_main.py`, `static/index.html`, `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml`, `README.md`) and line numbers.
   - If a behavior, command, or file is not visible, mark it as `[NOT VISIBLE]` or `[UNCONFIRMED]` rather than guessing or inferring from external conventions.

---

## 5. Security & Governance Rules

1. **Never Paste Secrets**: Never output, commit, or prompt with API keys, tokens, `.env` file secrets, database credentials, production logs, or personal customer data.
2. **Read Before Approving Diffs**: Inspect every file diff carefully before committing or approving changes.
3. **Verification Obligation**: Never declare a task complete without executing and reporting concrete verification commands (`pytest -v`, `/health` check, `whoami` check, or break tests).
4. **AI Proposes, Developer Grades**: AI model outputs represent drafts to inspect, classify, grade, and refine. Human judgment owns all final deliverables.
