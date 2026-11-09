"""
Automated tests for the Task Management API.

Run them from the task_manager_api folder:
    python -m pytest -v

TestClient lets us call the API like a real client would (GET, POST, ...)
without starting a server. Every test follows the same 3 steps:
    1. Arrange - prepare data
    2. Act     - call the endpoint
    3. Assert  - check the status code and the JSON response
"""

import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_storage():
    """
    Runs automatically before EVERY test (autouse=True).

    Empties the in-memory storage and resets the id counter, so every test
    starts from a clean state and tests never depend on each other's order.
    """
    main.tasks.clear()
    main.next_id = 1


@pytest.fixture
def sample_task():
    """Create one task through the API and return its JSON (id will be 1)."""
    response = client.post(
        "/tasks", json={"title": "Buy milk", "description": "2 litres"}
    )
    return response.json()


@pytest.fixture
def mixed_tasks():
    """Create two finished tasks and one unfinished task."""
    client.post("/tasks", json={"title": "Read a book", "completed": True})
    client.post("/tasks", json={"title": "Go for a run", "completed": False})
    client.post("/tasks", json={"title": "Pay bills", "completed": True})


# ---------------------------------------------------------------------------
# Successful scenarios
# ---------------------------------------------------------------------------


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "2 litres", "completed": False},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Buy milk",
        "description": "2 litres",
        "completed": False,
    }


def test_create_task_uses_default_values():
    # Only the title is required; description and completed have defaults.
    response = client.post("/tasks", json={"title": "Call mom"})

    assert response.status_code == 201
    assert response.json()["description"] == ""
    assert response.json()["completed"] is False


def test_create_tasks_get_increasing_ids():
    first = client.post("/tasks", json={"title": "First"}).json()
    second = client.post("/tasks", json={"title": "Second"}).json()

    assert first["id"] == 1
    assert second["id"] == 2


def test_get_all_tasks_when_empty():
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_tasks(mixed_tasks):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_task_by_id(sample_task):
    response = client.get(f"/tasks/{sample_task['id']}")

    assert response.status_code == 200
    assert response.json() == sample_task


def test_filter_completed_tasks(mixed_tasks):
    response = client.get("/tasks", params={"completed": True})

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Read a book", "Pay bills"]


def test_filter_not_completed_tasks(mixed_tasks):
    response = client.get("/tasks?completed=false")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Go for a run"]


def test_update_task(sample_task):
    response = client.patch(f"/tasks/{sample_task['id']}", json={"completed": True})

    assert response.status_code == 200
    assert response.json()["completed"] is True
    # PATCH changes only what we sent; the other fields stay the same.
    assert response.json()["title"] == "Buy milk"
    assert response.json()["description"] == "2 litres"


def test_update_task_title_and_description(sample_task):
    response = client.patch(
        f"/tasks/{sample_task['id']}",
        json={"title": "Buy oat milk", "description": "1 litre"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Buy oat milk"
    assert response.json()["description"] == "1 litre"
    # The change is saved: fetching the task again shows the new title.
    assert client.get(f"/tasks/{sample_task['id']}").json()["title"] == "Buy oat milk"


def test_delete_task(sample_task):
    response = client.delete(f"/tasks/{sample_task['id']}")

    assert response.status_code == 204
    # The task is really gone.
    assert client.get(f"/tasks/{sample_task['id']}").status_code == 404


def test_deleted_task_id_is_not_reused(sample_task):
    client.delete(f"/tasks/{sample_task['id']}")

    response = client.post("/tasks", json={"title": "New task"})

    assert response.json()["id"] == 2


# ---------------------------------------------------------------------------
# Failure scenarios
# ---------------------------------------------------------------------------


def test_create_task_missing_title():
    # "title" is a required field.
    response = client.post("/tasks", json={"description": "No title here"})

    assert response.status_code == 422


def test_create_task_empty_title():
    # Field(min_length=1) rejects an empty title.
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_create_task_invalid_completed_value():
    # "completed" must be a boolean.
    response = client.post("/tasks", json={"title": "Test", "completed": "maybe"})

    assert response.status_code == 422


def test_create_task_title_too_long():
    response = client.post("/tasks", json={"title": "x" * 101})

    assert response.status_code == 422


def test_get_nonexistent_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 999 not found"}


def test_get_task_with_invalid_id():
    # The path parameter must be an integer.
    response = client.get("/tasks/abc")

    assert response.status_code == 422


def test_filter_with_invalid_completed_value():
    response = client.get("/tasks?completed=maybe")

    assert response.status_code == 422


def test_update_nonexistent_task():
    response = client.patch("/tasks/999", json={"completed": True})

    assert response.status_code == 404


def test_update_task_with_invalid_data(sample_task):
    response = client.patch(f"/tasks/{sample_task['id']}", json={"title": ""})

    assert response.status_code == 422
    # The task was not changed.
    assert client.get(f"/tasks/{sample_task['id']}").json()["title"] == "Buy milk"


def test_delete_nonexistent_task():
    response = client.delete("/tasks/999")

    assert response.status_code == 404
