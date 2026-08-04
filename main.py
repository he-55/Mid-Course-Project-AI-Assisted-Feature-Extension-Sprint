"""FastAPI Kanban task tracker with strict unidirectional state transitions."""

import itertools
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from schemas import (
    STATUS_ORDER,
    DueFilter,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

app = FastAPI(title="Kanban Task Tracker", version="1.1.0")

# Tasks due within this many days (inclusive, starting today) count as "due soon".
DUE_SOON_WINDOW_DAYS = 2

# --- In-memory store -------------------------------------------------------

_tasks: dict[int, dict] = {}
_id_counter = itertools.count(1)


def reset_store() -> None:
    """Clear all tasks and restart IDs. Used by the test suite."""
    global _id_counter
    _tasks.clear()
    _id_counter = itertools.count(1)


def _get_task_or_404(task_id: int) -> dict:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


def validate_transition(current: TaskStatus, target: TaskStatus) -> None:
    """Enforce the unidirectional flow TODO -> IN_PROGRESS -> DONE.

    Any move to a column with a lower rank (e.g. back to TODO) is illegal
    and raises HTTP 400.
    """
    if STATUS_ORDER[target] < STATUS_ORDER[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Illegal state transition: '{current.value}' -> '{target.value}'. "
                "Tasks can only move forward (todo -> in_progress -> done)."
            ),
        )


def is_overdue(task: dict, today: date) -> bool:
    """Past due and not completed. DONE tasks are never overdue."""
    return (
        task["due_date"] is not None
        and task["due_date"] < today
        and task["status"] != TaskStatus.DONE
    )


def is_due_soon(task: dict, today: date) -> bool:
    """Due between today and the due-soon window (inclusive), not completed."""
    return (
        task["due_date"] is not None
        and task["status"] != TaskStatus.DONE
        and today <= task["due_date"] <= today + timedelta(days=DUE_SOON_WINDOW_DAYS)
    )


# --- API routes ------------------------------------------------------------


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post(
    "/api/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: TaskCreate) -> dict:
    task_id = next(_id_counter)
    task = {
        "id": task_id,
        "title": payload.title,
        "description": payload.description,
        "status": TaskStatus.TODO,
        "due_date": payload.due_date,
        "tags": payload.tags,
    }
    _tasks[task_id] = task
    return task


@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(
    task_status: Optional[TaskStatus] = Query(default=None, alias="status"),
    due: Optional[DueFilter] = Query(default=None),
    tag: Optional[str] = Query(default=None, min_length=1),
) -> list[dict]:
    tasks = list(_tasks.values())
    if task_status is not None:
        tasks = [t for t in tasks if t["status"] == task_status]
    if tag is not None:
        # Stored tags are normalized lowercase, so lowering the query
        # gives case-insensitive matching.
        wanted = tag.strip().lower()
        tasks = [t for t in tasks if wanted in t["tags"]]
    if due is not None:
        today = date.today()
        if due == DueFilter.OVERDUE:
            tasks = [t for t in tasks if is_overdue(t, today)]
        elif due == DueFilter.SOON:
            tasks = [t for t in tasks if is_due_soon(t, today)]
        elif due == DueFilter.NONE:
            tasks = [t for t in tasks if t["due_date"] is None]
    return tasks


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> dict:
    return _get_task_or_404(task_id)


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    task = _get_task_or_404(task_id)

    if payload.status is not None:
        validate_transition(task["status"], payload.status)
        task["status"] = payload.status
    if payload.title is not None:
        task["title"] = payload.title
    if payload.description is not None:
        task["description"] = payload.description
    # An explicit "due_date": null clears the date; an absent field leaves it alone.
    if "due_date" in payload.model_fields_set:
        task["due_date"] = payload.due_date
    # A tags list (including []) replaces wholesale; None/absent leaves them alone.
    if payload.tags is not None:
        task["tags"] = payload.tags
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    _get_task_or_404(task_id)
    del _tasks[task_id]


# --- Frontend --------------------------------------------------------------


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
