# Student Management API

A beginner-friendly REST API, built with **FastAPI**, to manage college students.

You can register students, list them, search them by name, update them and delete them.
Two students can never share the same email.
Data is stored in a Python dictionary (in memory), so it disappears when the server stops.

> Project Two of two. It uses the same structure as Project One (`task_manager_api`),
> so you can compare them side by side. The main differences are listed in
> [Comparison with the Task Management API](#comparison-with-the-task-management-api).

---

## 1. What this project does

| Feature | Endpoint |
|---|---|
| Register a student | `POST /students` |
| Get all students | `GET /students` |
| Get one student by id | `GET /students/{student_id}` |
| Search students by name | `GET /students/search/?name=Anand` |
| Update a student (replace all fields) | `PUT /students/{student_id}` |
| Delete a student | `DELETE /students/{student_id}` |

Every student has these fields:

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Given by the server (1, 2, 3, ...). Never reused after a delete. |
| `name` | string | **Required**. 2 to 100 characters. |
| `age` | integer | **Required**. 16 to 100. |
| `course` | string | **Required**. 2 to 100 characters. |
| `email` | string | **Required**. Must be a valid email. Must be unique (case-insensitive). |

---

## 2. What is FastAPI?

FastAPI is a Python framework for building web APIs.
You write normal Python functions, and FastAPI turns them into HTTP endpoints:

```python
@app.get("/students/{student_id}")
def get_student(student_id: int):
    ...
```

From the type hints (`student_id: int`) FastAPI automatically:

- reads the value from the URL,
- converts it to the right type,
- returns a clear `422` error if the value is invalid,
- documents the endpoint in Swagger (`/docs`).

See `../FASTAPI_LEARNING_GUIDE.md` for a full beginner explanation.

---

## 3. Install the dependencies

You need **Python 3.10 or newer**. Check with:

```bash
python3 --version
```

Open a terminal **inside the `student_management_api` folder**, then:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

A *virtual environment* (`.venv`) is a private folder of packages for this project only,
so it does not clash with other Python projects on your computer.

What gets installed (`requirements.txt`):

| Package | Why we need it |
|---|---|
| `fastapi` | The web framework |
| `pydantic` | Data validation (comes with FastAPI, listed so you can see it) |
| `uvicorn` | The server that runs the app |
| `pytest` | Runs the automated tests |
| `httpx` | Used by FastAPI's `TestClient` to send test requests |
| `email-validator` | Needed by Pydantic's `EmailStr` to check email addresses |

`email-validator` is the only extra package compared to Project One.

---

## 4. Start the server

With the virtual environment active, from the `student_management_api` folder:

```bash
uvicorn app.main:app --reload
```

- `app.main` → the file `app/main.py`
- `:app` → the variable named `app` inside that file (`app = FastAPI(...)`)
- `--reload` → restart automatically when you save a code change (development only)

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open <http://127.0.0.1:8000/> in your browser. You should see:

```json
{"status": "ok", "message": "Student Management API is running"}
```

Stop the server with **CTRL+C**.

To run both projects at the same time, give this one another port:

```bash
uvicorn app.main:app --reload --port 8001
```

---

## 5. Swagger documentation

FastAPI creates interactive documentation for you. With the server running, open:

- **Swagger UI:** <http://127.0.0.1:8000/docs>
- **ReDoc (read-only docs):** <http://127.0.0.1:8000/redoc>
- **Raw OpenAPI schema (JSON):** <http://127.0.0.1:8000/openapi.json>

To try an endpoint in Swagger UI:

1. Click an endpoint, e.g. **POST /students**
2. Click **Try it out**
3. Edit the example JSON
4. Click **Execute**
5. Scroll down to see the status code and response body

---

## 6. API endpoints

| Method | Endpoint | Description | Success code | Error codes |
|---|---|---|---|---|
| GET | `/` | Health check | 200 | – |
| POST | `/students` | Register a student | 201 | 409, 422 |
| GET | `/students` | Get all students | 200 | – |
| GET | `/students/search/?name=Anand` | Search by name | 200 | 422 |
| GET | `/students/{student_id}` | Get student by id | 200 | 404, 422 |
| PUT | `/students/{student_id}` | Update (replace) a student | 200 | 404, 409, 422 |
| DELETE | `/students/{student_id}` | Delete a student | 204 | 404, 422 |

Status codes used:

| Code | Name | When |
|---|---|---|
| 200 | OK | Request worked, data returned |
| 201 | Created | A new student was registered |
| 204 | No Content | Student deleted, nothing to return |
| 404 | Not Found | No student with that id |
| 409 | Conflict | The email already belongs to another student |
| 422 | Unprocessable Entity | Invalid data (bad email, age too low, missing field, ...) |

> ⚠ **Keep the trailing slash on search:** `/students/search/?name=Anand`.
> Without it (`/students/search?name=Anand`), FastAPI matches the URL to
> `/students/{student_id}` with `student_id = "search"` and returns a 422
> ("Input should be a valid integer"). Swagger always uses the correct URL.

---

## 7. Example requests and responses

All examples below are real responses from this API.

### Health check

`GET /` → **200 OK**

```json
{
  "status": "ok",
  "message": "Student Management API is running"
}
```

### Register a student

`POST /students`

Request body:

```json
{
  "name": "Anand Kumar",
  "age": 20,
  "course": "Computer Science",
  "email": "anand@example.com"
}
```

Response → **201 Created**

```json
{
  "id": 1,
  "name": "Anand Kumar",
  "age": 20,
  "course": "Computer Science",
  "email": "anand@example.com"
}
```

### Get all students

`GET /students` → **200 OK**

```json
[
  {
    "id": 1,
    "name": "Anand Kumar",
    "age": 20,
    "course": "Computer Science",
    "email": "anand@example.com"
  },
  {
    "id": 2,
    "name": "Priya Sharma",
    "age": 21,
    "course": "Physics",
    "email": "priya@example.com"
  }
]
```

### Get a student by id

`GET /students/1` → **200 OK**

```json
{
  "id": 1,
  "name": "Anand Kumar",
  "age": 20,
  "course": "Computer Science",
  "email": "anand@example.com"
}
```

### Search by name

`GET /students/search/?name=anand` → **200 OK**

The search ignores upper/lower case and matches part of a name.

```json
[
  {
    "id": 1,
    "name": "Anand Kumar",
    "age": 20,
    "course": "Computer Science",
    "email": "anand@example.com"
  }
]
```

No match returns an empty list `[]` (not an error).

### Update a student (PUT)

`PUT /students/1`

PUT replaces the **whole** student, so send **every** field:

```json
{
  "name": "Anand Kumar",
  "age": 21,
  "course": "Data Science",
  "email": "anand@example.com"
}
```

Response → **200 OK**

```json
{
  "id": 1,
  "name": "Anand Kumar",
  "age": 21,
  "course": "Data Science",
  "email": "anand@example.com"
}
```

### Delete a student

`DELETE /students/2` → **204 No Content** (empty body)

### Error: duplicate email

`POST /students` with an email that is already registered → **409 Conflict**

```json
{
  "detail": "A student with email anand@example.com already exists"
}
```

### Error: student not found

`GET /students/99` → **404 Not Found**

```json
{
  "detail": "Student with id 99 not found"
}
```

### Error: invalid data

`POST /students` with:

```json
{"name": "A", "age": 10, "course": "Maths", "email": "not-an-email"}
```

Response → **422 Unprocessable Entity** — Pydantic reports **every** problem at once:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 2 characters",
      "input": "A",
      "ctx": {"min_length": 2}
    },
    {
      "type": "greater_than_equal",
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 16",
      "input": 10,
      "ctx": {"ge": 16}
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address: An email address must have an @-sign.",
      "input": "not-an-email",
      "ctx": {"reason": "An email address must have an @-sign."}
    }
  ]
}
```

### Try it with curl (optional)

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Anand Kumar", "age": 20, "course": "Computer Science", "email": "anand@example.com"}'
```

---

## 8. Run the automated tests

With the virtual environment active, from the `student_management_api` folder:

```bash
python -m pytest -v
```

You do **not** need to start the server first. `TestClient` calls the app directly in memory.

Expected result (29 tests):

```
tests/test_students.py::test_health_check PASSED
tests/test_students.py::test_register_student PASSED
...
tests/test_students.py::test_delete_nonexistent_student PASSED
======================== 29 passed, 1 warning in 0.46s =========================
```

About the 1 warning: the newest Starlette (the library under FastAPI) prefers a package
called `httpx2` over `httpx`. `httpx2` needs Python 3.11+, and this project supports 3.10+,
so we keep `httpx`. The warning does not affect any test.

What the tests cover:

| Successful scenarios | Failure scenarios |
|---|---|
| Health check | Missing required field / empty body → 422 |
| Register a student (201) | Invalid email → 422 |
| Get all students (empty and with data) | Age too low / negative / not a number → 422 |
| Get student by id | Name too short, empty course → 422 |
| Search by name (partial match) | Duplicate email → 409 (also with different upper/lower case) |
| Search ignores upper/lower case | Get non-existent id → 404 |
| Search with no match → `[]` | Non-integer id (`/students/abc`) → 422 |
| Update a student (PUT) | Search without `name` → 422 |
| Update while keeping own email | Update non-existent id → 404 |
| Delete a student (204, then 404) | Update with invalid data / missing field → 422 |
| | Update to another student's email → 409 |
| | Delete non-existent id → 404 |

**How tests stay independent:** the `reset_storage` fixture in `tests/test_students.py`
has `autouse=True`, so pytest runs it before *every* test. It empties the `students`
dictionary and resets the id counter, so no test depends on another test's data or order.

Useful pytest options:

```bash
python -m pytest -v -k email       # run only tests with "email" in the name
python -m pytest -v -x             # stop at the first failure
```

---

## 9. Project structure

```
student_management_api/
├── app/
│   ├── __init__.py      # Empty. Marks "app" as a Python package so we can "import app.main"
│   ├── main.py          # The FastAPI app, the in-memory storage and all endpoints
│   └── schemas.py       # Pydantic models: StudentCreate, Student
├── tests/
│   ├── __init__.py      # Empty. Lets plain "pytest" (not only "python -m pytest") find the app
│   └── test_students.py # 29 automated tests
├── requirements.txt     # Packages to install
└── README.md            # This file
```

How the pieces connect:

1. A request arrives, e.g. `POST /students` with a JSON body.
2. FastAPI finds the matching function in `main.py` (`register_student`).
3. FastAPI validates the body with `StudentCreate` from `schemas.py`.
   Invalid → 422 is returned and the function never runs.
4. The function checks the email is not taken (`is_email_taken`). Taken → 409.
5. The function saves the student in the `students` dictionary.
6. FastAPI shapes the return value with `response_model=Student` and sends JSON back.

---

## Comparison with the Task Management API

| | Task Management API | Student Management API |
|---|---|---|
| Update method | `PATCH` (change some fields) | `PUT` (replace all fields) |
| Update model | `TaskUpdate` (all fields optional) | `StudentCreate` (all fields required) |
| Filter / search | `GET /tasks?completed=true` (exact match on a boolean) | `GET /students/search/?name=...` (partial, case-insensitive text match) |
| Extra business rule | – | Unique email → `409 Conflict` |
| Extra validation | Title length | Name/course length, age range, email format |
| Helper function | – | `is_email_taken()` (used by register and update) |
| Extra package | – | `email-validator` |

Everything else (storage, id counter, health check, 404 handling, 204 on delete,
test fixtures) is the same on purpose.

---

## Limitations (on purpose, for learning)

- Data is lost when the server stops (no database yet).
- No login/authentication.
- Only one server process should run, because each process has its own dictionary.

These will be added in later lessons (SQLAlchemy/PostgreSQL, JWT authentication, ...).
