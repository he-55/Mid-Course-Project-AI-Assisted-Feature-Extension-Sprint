"""Pytest suite for the Kanban task tracker API."""

import pytest
from fastapi.testclient import TestClient

from main import app, reset_store

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
