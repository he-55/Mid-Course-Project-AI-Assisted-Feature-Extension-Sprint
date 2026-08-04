"""Pytest suite for the Kanban task tracker API."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from main import DUE_SOON_WINDOW_DAYS, app, reset_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    """Start every test with an empty task store."""
    reset_store()
    yield
    reset_store()


def make_task(title: str = "Sample task", description: str | None = "A description") -> dict:
    response = client.post("/api/tasks", json={"title": title, "description": description})
    assert response.status_code == 201
    return response.json()


# --- Health check ----------------------------------------------------------


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Create ----------------------------------------------------------------


def test_create_task_defaults_to_todo():
    task = make_task("Write report", "Quarterly numbers")
    assert task["title"] == "Write report"
    assert task["description"] == "Quarterly numbers"
    assert task["status"] == "todo"
    assert isinstance(task["id"], int)


def test_create_task_without_description():
    task = make_task("No description", None)
    assert task["description"] is None
    assert task["status"] == "todo"


def test_create_task_requires_title():
    response = client.post("/api/tasks", json={"description": "missing title"})
    assert response.status_code == 422

    response = client.post("/api/tasks", json={"title": ""})
    assert response.status_code == 422


# --- Read ------------------------------------------------------------------


def test_list_tasks():
    make_task("Task A")
    make_task("Task B")

    response = client.get("/api/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task A", "Task B"]


def test_list_tasks_filtered_by_status():
    task_a = make_task("Task A")
    make_task("Task B")
    client.patch(f"/api/tasks/{task_a['id']}", json={"status": "in_progress"})

    response = client.get("/api/tasks", params={"status": "in_progress"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task A"

    response = client.get("/api/tasks", params={"status": "todo"})
    assert [t["title"] for t in response.json()] == ["Task B"]


def test_get_single_task():
    task = make_task("Findable")
    response = client.get(f"/api/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Findable"


def test_get_missing_task_returns_404():
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


# --- Update ----------------------------------------------------------------


def test_update_task_details():
    task = make_task("Old title", "Old description")
    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"title": "New title", "description": "New description"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New title"
    assert body["description"] == "New description"
    assert body["status"] == "todo"


def test_update_missing_task_returns_404():
    response = client.patch("/api/tasks/999", json={"title": "Ghost"})
    assert response.status_code == 404


# --- Delete ----------------------------------------------------------------


def test_delete_task():
    task = make_task("Doomed")
    response = client.delete(f"/api/tasks/{task['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404


def test_delete_missing_task_returns_404():
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404


# --- State transition rules ------------------------------------------------


def test_forward_transitions_allowed():
    task = make_task("Moving forward")

    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_move_back_to_todo_from_in_progress_returns_400():
    task = make_task("No going back")
    client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})

    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "todo"})
    assert response.status_code == 400
    assert "Illegal state transition" in response.json()["detail"]


def test_move_back_to_todo_from_done_returns_400():
    task = make_task("Definitely done")
    client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})

    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "todo"})
    assert response.status_code == 400


def test_move_done_back_to_in_progress_returns_400():
    task = make_task("Locked in Done")
    client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})

    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    assert response.status_code == 400


def test_illegal_transition_does_not_change_task():
    task = make_task("Unchanged")
    client.patch(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    client.patch(f"/api/tasks/{task['id']}", json={"status": "todo"})

    response = client.get(f"/api/tasks/{task['id']}")
    assert response.json()["status"] == "in_progress"


def test_same_status_update_is_allowed():
    task = make_task("Idempotent")
    response = client.patch(f"/api/tasks/{task['id']}", json={"status": "todo"})
    assert response.status_code == 200
    assert response.json()["status"] == "todo"


# --- Due dates --------------------------------------------------------------


def iso(offset_days: int) -> str:
    """ISO date string relative to today."""
    return (date.today() + timedelta(days=offset_days)).isoformat()


def make_task_due(title: str, due: str | None) -> dict:
    response = client.post("/api/tasks", json={"title": title, "due_date": due})
    assert response.status_code == 201
    return response.json()


def test_create_task_with_due_date():
    response = client.post(
        "/api/tasks", json={"title": "Dated", "due_date": "2026-12-31"}
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-12-31"


def test_create_task_without_due_date_defaults_to_none():
    task = make_task("Undated")
    assert task["due_date"] is None


def test_create_task_with_invalid_due_date_returns_422():
    for bad_value in ["not-a-date", "31/12/2026", "2026-13-01", 12345]:
        response = client.post(
            "/api/tasks", json={"title": "Bad date", "due_date": bad_value}
        )
        assert response.status_code == 422, f"expected 422 for {bad_value!r}"


def test_update_due_date():
    task = make_task("Reschedulable")
    response = client.patch(
        f"/api/tasks/{task['id']}", json={"due_date": "2027-01-15"}
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == "2027-01-15"


def test_update_with_invalid_due_date_returns_422():
    task = make_task("Still valid")
    response = client.patch(
        f"/api/tasks/{task['id']}", json={"due_date": "soonish"}
    )
    assert response.status_code == 422


def test_clear_due_date_with_explicit_null():
    task = make_task_due("Clearable", "2026-12-31")
    response = client.patch(f"/api/tasks/{task['id']}", json={"due_date": None})
    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_update_without_due_date_field_preserves_it():
    task = make_task_due("Sticky date", "2026-12-31")
    response = client.patch(f"/api/tasks/{task['id']}", json={"title": "Renamed"})
    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-12-31"


# --- Due filters ------------------------------------------------------------


def test_filter_overdue_only():
    make_task_due("Past due", iso(-1))
    make_task_due("Future", iso(30))
    make_task("Undated")

    response = client.get("/api/tasks", params={"due": "overdue"})
    assert response.status_code == 200
    assert [t["title"] for t in response.json()] == ["Past due"]


def test_overdue_filter_excludes_done_tasks():
    finished = make_task_due("Finished late", iso(-5))
    make_task_due("Still late", iso(-5))
    client.patch(f"/api/tasks/{finished['id']}", json={"status": "in_progress"})
    client.patch(f"/api/tasks/{finished['id']}", json={"status": "done"})

    response = client.get("/api/tasks", params={"due": "overdue"})
    assert [t["title"] for t in response.json()] == ["Still late"]


def test_filter_due_soon():
    make_task_due("Due today", iso(0))
    make_task_due("Inside window", iso(DUE_SOON_WINDOW_DAYS))
    make_task_due("Past due", iso(-1))
    make_task_due("Far future", iso(DUE_SOON_WINDOW_DAYS + 5))
    make_task("Undated")

    response = client.get("/api/tasks", params={"due": "soon"})
    assert response.status_code == 200
    titles = {t["title"] for t in response.json()}
    assert titles == {"Due today", "Inside window"}


def test_due_soon_filter_excludes_done_tasks():
    finished = make_task_due("Done today", iso(0))
    client.patch(f"/api/tasks/{finished['id']}", json={"status": "in_progress"})
    client.patch(f"/api/tasks/{finished['id']}", json={"status": "done"})

    response = client.get("/api/tasks", params={"due": "soon"})
    assert response.json() == []


def test_filter_no_due_date():
    make_task_due("Dated", iso(3))
    make_task("Undated")

    response = client.get("/api/tasks", params={"due": "none"})
    assert [t["title"] for t in response.json()] == ["Undated"]


def test_due_filter_combines_with_status_filter():
    started = make_task_due("Overdue in progress", iso(-2))
    make_task_due("Overdue in todo", iso(-2))
    client.patch(f"/api/tasks/{started['id']}", json={"status": "in_progress"})

    response = client.get(
        "/api/tasks", params={"due": "overdue", "status": "in_progress"}
    )
    assert [t["title"] for t in response.json()] == ["Overdue in progress"]


def test_invalid_due_filter_returns_422():
    response = client.get("/api/tasks", params={"due": "yesterday"})
    assert response.status_code == 422
