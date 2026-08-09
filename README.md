# Kanban Task Tracker

A Kanban-style task tracker built with **FastAPI** (backend) and **Vanilla HTML/CSS/JS** (frontend, no frameworks). Tasks move strictly forward through `To Do → In Progress → Done`, with due dates, overdue/due-soon indicators, real-time search, and tags.

Sprint documentation (user stories, verification evidence, ADR, prompt log) lives in [`docs/`](docs/).

## Requirements

- Python 3.10+ (developed on 3.13)
- No database or Node.js needed — storage is in-memory and the frontend is static files.

## Setup (one-time)

From the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run the backend

```bash
.venv/bin/uvicorn main:app --reload --port 8000
```

- `--reload` restarts the server automatically when you edit Python files.
- Interactive API docs (Swagger UI): http://localhost:8000/docs

> **Note:** storage is in-memory, so all tasks reset whenever the server restarts. This is expected.

## Open the frontend

The backend serves the frontend — no separate build or server. With uvicorn running, open:

**http://localhost:8000**

You'll get the Kanban board: create tasks (title, description, due date, tags), drag cards between columns (backward moves are blocked), filter by timeline pills or tag chips, and search with `/` or `Ctrl/Cmd + K`. Frontend files live in [`static/`](static/); after editing them, just refresh the browser — no server restart needed.

## Run the tests

```bash
.venv/bin/python -m pytest test_main.py -v
```

The suite (43 tests) covers the health check, CRUD, illegal state transitions (HTTP 400), due-date validation and timeline filters, and tag normalization and filtering. It uses FastAPI's `TestClient`, so **the server does not need to be running**.

> Tip: activate the venv with `source .venv/bin/activate` to drop the `.venv/bin/` prefix and run `uvicorn main:app --reload` / `pytest` directly.

## Project layout

| Path | Purpose |
|---|---|
| `main.py` | FastAPI app: routes, in-memory store, state-transition and filter logic |
| `schemas.py` | Pydantic v2 models, validation, tag normalization |
| `static/index.html` | Board layout and all CSS |
| `static/app.js` | Drag-and-drop, filters, search, tags — plain ES6+, `fetch` API |
| `test_main.py` | Full pytest suite |
| `docs/` | Sprint documentation and verification evidence |
