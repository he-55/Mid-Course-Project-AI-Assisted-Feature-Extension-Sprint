# CLAUDE.md - Terminal Agent Guidelines & Environment Context

This file provides workspace context and operational rules for AI coding assistants working in terminal environments.

---

## 1. Key Commands

- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Application**: `python run.py` OR `uvicorn main:app --reload`
- **Run Unit Tests**: `pytest -v`
- **Build Container**: `docker build -t task-tracker .`
- **Run Container**: `docker run --rm -d -p 8000:8000 --name tt-app task-tracker`

---

## 2. Core Architecture & Files

- `main.py`: Application entrypoint, FastAPI instance, REST routes, static files mounting (`/static`), `/health` endpoint.
- `schemas.py`: Pydantic v2 schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`), enums (`TaskStatus`, `DueFilter`), tag normalization.
- `test_main.py`: Pytest suite containing 43 unit tests covering health, CRUD, status transitions, tag validation, and timeline filters.
- `static/`: HTML/CSS/JS frontend files (`index.html`).
- `docs/`: System documentation, release evidence, AI review, and midcourse deliverables.

---

## 3. Mandatory Development Rules

- **Unidirectional Transitions**: `todo` -> `in_progress` -> `done`. Rollbacks raise `HTTP 400 Bad Request`.
- **Validation**: Title (1-200 chars), Tags (max 10, max 30 chars each, lowercased & deduplicated).
- **Verification**: Always execute `pytest -v` before declaring work complete.
