# CLAUDE.md - Terminal Agent Guidelines & Environment Context

This file provides workspace context and operational rules for AI coding assistants working in terminal environments.

---

## 1. Key Commands

- **Install Dependencies**: `python3 -m venv .venv` then `.venv/bin/python -m pip install -r requirements.txt`
- **Run Application**: `.venv/bin/python run.py` OR `.venv/bin/python -m uvicorn app.main:app --reload`
- **Run Unit Tests**: `.venv/bin/python -m pytest -v`
- **Build Container**: `docker build -t task-tracker .`
- **Run Container**: `docker run --rm -d -p 8000:8000 --name tt-app task-tracker`

---

## 2. Core Architecture & Files

- `app/main.py`: Application entrypoint, FastAPI instance, REST routes, frontend mounting, `/health` endpoint.
- `app/schemas.py`: Pydantic v2 schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`), enums (`TaskStatus`, `DueFilter`), tag normalization.
- `tests/test_main.py`: Pytest suite containing 47 unit tests covering health, CRUD, status transitions, validation boundaries, tag validation, and timeline filters.
- `frontend/`: HTML/CSS/JS frontend files (`index.html`, `app.js`).
- `docs/`: System documentation, release evidence, AI review, and midcourse deliverables.

---

## 3. Mandatory Development Rules

- **Unidirectional Transitions**: `todo` -> `in_progress` -> `done`. Rollbacks raise `HTTP 400 Bad Request`.
- **Validation**: Title (1-200 chars), Tags (max 10, max 30 chars each, lowercased & deduplicated).
- **Verification**: Always execute `pytest -v` before declaring work complete.
