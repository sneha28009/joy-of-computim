"""
Automated tests for the Student Management API.

Run them from the student_management_api folder:
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

# A valid student we can reuse in many tests.
VALID_STUDENT = {
    "name": "Anand Kumar",
    "age": 20,
    "course": "Computer Science",
    "email": "anand@example.com",
}


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
    main.students.clear()
    main.next_id = 1


@pytest.fixture
def sample_student():
    """Register one student through the API and return its JSON (id will be 1)."""
    response = client.post("/students", json=VALID_STUDENT)
    return response.json()


@pytest.fixture
def many_students():
    """Register three students with different names."""
    client.post("/students", json=VALID_STUDENT)
    client.post(
        "/students",
        json={"name": "Priya Sharma", "age": 21, "course": "Physics", "email": "priya@example.com"},
    )
    client.post(
        "/students",
        json={"name": "Anandi Rao", "age": 19, "course": "Maths", "email": "anandi@example.com"},
    )


# ---------------------------------------------------------------------------
# Successful scenarios
# ---------------------------------------------------------------------------


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_student():
    response = client.post("/students", json=VALID_STUDENT)

    assert response.status_code == 201
    assert response.json() == {"id": 1, **VALID_STUDENT}


def test_get_all_students_when_empty():
    response = client.get("/students")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_students(many_students):
    response = client.get("/students")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_student_by_id(sample_student):
    response = client.get(f"/students/{sample_student['id']}")

    assert response.status_code == 200
    assert response.json() == sample_student


def test_search_students_by_name(many_students):
    response = client.get("/students/search", params={"name": "Anand"})

    assert response.status_code == 200
    names = [student["name"] for student in response.json()]
    # "Anand" is part of both "Anand Kumar" and "Anandi Rao".
    assert names == ["Anand Kumar", "Anandi Rao"]


def test_search_is_case_insensitive(many_students):
    response = client.get("/students/search/?name=PRIYA")

    assert response.status_code == 200
    assert [student["name"] for student in response.json()] == ["Priya Sharma"]


def test_search_with_no_match_returns_empty_list(many_students):
    response = client.get("/students/search/?name=Zara")

    assert response.status_code == 200
    assert response.json() == []


def test_update_student(sample_student):
    updated = {
        "name": "Anand K.",
        "age": 21,
        "course": "Data Science",
        "email": "anand.k@example.com",
    }

    response = client.put(f"/students/{sample_student['id']}", json=updated)

    assert response.status_code == 200
    assert response.json() == {"id": sample_student["id"], **updated}
    # The change is saved: fetching the student again shows the new data.
    assert client.get(f"/students/{sample_student['id']}").json()["course"] == "Data Science"


def test_update_student_can_keep_own_email(sample_student):
    # Keeping your own email is NOT a duplicate.
    response = client.put(f"/students/{sample_student['id']}", json={**VALID_STUDENT, "age": 22})

    assert response.status_code == 200
    assert response.json()["age"] == 22


def test_delete_student(sample_student):
    response = client.delete(f"/students/{sample_student['id']}")

    assert response.status_code == 204
    # The student is really gone.
    assert client.get(f"/students/{sample_student['id']}").status_code == 404


# ---------------------------------------------------------------------------
# Failure scenarios
# ---------------------------------------------------------------------------


def test_register_student_missing_required_field():
    # No "email" field.
    student = {"name": "Anand Kumar", "age": 20, "course": "Computer Science"}

    response = client.post("/students", json=student)

    assert response.status_code == 422


def test_register_student_empty_body():
    response = client.post("/students", json={})

    assert response.status_code == 422


def test_register_student_invalid_email():
    response = client.post("/students", json={**VALID_STUDENT, "email": "not-an-email"})

    assert response.status_code == 422


def test_register_student_too_young():
    # Field(ge=16) means age must be 16 or more.
    response = client.post("/students", json={**VALID_STUDENT, "age": 10})

    assert response.status_code == 422


def test_register_student_negative_age():
    response = client.post("/students", json={**VALID_STUDENT, "age": -5})

    assert response.status_code == 422


def test_register_student_age_not_a_number():
    response = client.post("/students", json={**VALID_STUDENT, "age": "twenty"})

    assert response.status_code == 422


def test_register_student_name_too_short():
    # Field(min_length=2) rejects a 1-letter name.
    response = client.post("/students", json={**VALID_STUDENT, "name": "A"})

    assert response.status_code == 422


def test_register_student_empty_course():
    response = client.post("/students", json={**VALID_STUDENT, "course": ""})

    assert response.status_code == 422


def test_register_duplicate_email(sample_student):
    other_student = {**VALID_STUDENT, "name": "Someone Else"}

    response = client.post("/students", json=other_student)

    assert response.status_code == 409
    assert response.json() == {"detail": "A student with email anand@example.com already exists"}


def test_register_duplicate_email_different_case(sample_student):
    response = client.post("/students", json={**VALID_STUDENT, "email": "ANAND@example.com"})

    assert response.status_code == 409


def test_get_nonexistent_student():
    response = client.get("/students/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Student with id 999 not found"}


def test_get_student_with_invalid_id():
    # The path parameter must be an integer.
    response = client.get("/students/abc")

    assert response.status_code == 422


def test_search_without_name():
    # "name" is a required query parameter.
    response = client.get("/students/search/")

    assert response.status_code == 422


def test_update_nonexistent_student():
    response = client.put("/students/999", json=VALID_STUDENT)

    assert response.status_code == 404


def test_update_student_with_invalid_data(sample_student):
    response = client.put(
        f"/students/{sample_student['id']}", json={**VALID_STUDENT, "email": "bad-email"}
    )

    assert response.status_code == 422
    # The student was not changed.
    assert client.get(f"/students/{sample_student['id']}").json() == sample_student


def test_update_student_missing_field(sample_student):
    # PUT needs ALL fields; sending only "age" is not enough.
    response = client.put(f"/students/{sample_student['id']}", json={"age": 22})

    assert response.status_code == 422


def test_update_student_to_duplicate_email(many_students):
    # Student 2 (Priya) tries to take Anand's email.
    priya = {"name": "Priya Sharma", "age": 21, "course": "Physics", "email": "anand@example.com"}

    response = client.put("/students/2", json=priya)

    assert response.status_code == 409


def test_delete_nonexistent_student():
    response = client.delete("/students/999")

    assert response.status_code == 404
