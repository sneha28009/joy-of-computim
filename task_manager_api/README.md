# Task Management API

A beginner-friendly REST API, built with **FastAPI**, to manage a simple to-do list.

You can create tasks, list them, filter them by status, update them and delete them.
Data is stored in a Python dictionary (in memory), so it disappears when the server stops.

> Project One of two. Project Two (`student_management_api`) uses the same structure,
> so you can compare them side by side.

---

## 1. What this project does

| Feature | Endpoint |
|---|---|
| Create a task | `POST /tasks` |
| Get all tasks | `GET /tasks` |
| Get one task by id | `GET /tasks/{task_id}` |
| Filter tasks by completion status | `GET /tasks?completed=true` |
| Update a task (only the fields you send) | `PATCH /tasks/{task_id}` |
| Delete a task | `DELETE /tasks/{task_id}` |

Every task has these fields:

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Given by the server (1, 2, 3, ...). Never reused after a delete. |
| `title` | string | **Required**. 1 to 100 characters. |
| `description` | string | Optional. Up to 500 characters. Default: `""` |
| `completed` | boolean | Optional. Default: `false` |

---

## 2. What is FastAPI?

FastAPI is a Python framework for building web APIs.
You write normal Python functions, and FastAPI turns them into HTTP endpoints:

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    ...
```

From the type hints (`task_id: int`) FastAPI automatically:

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

Open a terminal **inside the `task_manager_api` folder**, then:

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

---

## 4. Start the server

With the virtual environment active, from the `task_manager_api` folder:

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
{"status": "ok", "message": "Task Management API is running"}
```

Stop the server with **CTRL+C**.

To run on a different port: `uvicorn app.main:app --reload --port 8001`

---

## 5. Swagger documentation

FastAPI creates interactive documentation for you. With the server running, open:

- **Swagger UI:** <http://127.0.0.1:8000/docs>
- **ReDoc (read-only docs):** <http://127.0.0.1:8000/redoc>
- **Raw OpenAPI schema (JSON):** <http://127.0.0.1:8000/openapi.json>

To try an endpoint in Swagger UI:

1. Click an endpoint, e.g. **POST /tasks**
2. Click **Try it out**
3. Edit the example JSON
4. Click **Execute**
5. Scroll down to see the status code and response body

---

## 6. API endpoints

| Method | Endpoint | Description | Success code | Error codes |
|---|---|---|---|---|
| GET | `/` | Health check | 200 | – |
| POST | `/tasks` | Create a task | 201 | 422 |
| GET | `/tasks` | Get all tasks | 200 | – |
| GET | `/tasks?completed=true` | Filter by completion status | 200 | 422 |
| GET | `/tasks/{task_id}` | Get task by id | 200 | 404, 422 |
| PATCH | `/tasks/{task_id}` | Update some fields of a task | 200 | 404, 422 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 | 404, 422 |

Status codes used:

| Code | Name | When |
|---|---|---|
| 200 | OK | Request worked, data returned |
| 201 | Created | A new task was created |
| 204 | No Content | Task deleted, nothing to return |
| 404 | Not Found | No task with that id |
| 422 | Unprocessable Entity | Invalid data (wrong type, empty title, missing field, ...) |

---

## 7. Example requests and responses

All examples below are real responses from this API.

### Health check

`GET /` → **200 OK**

```json
{
  "status": "ok",
  "message": "Task Management API is running"
}
```

### Create a task

`POST /tasks`

Request body:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs and bread"
}
```

Response → **201 Created**

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs and bread",
  "completed": false
}
```

### Get all tasks

`GET /tasks` → **200 OK**

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs and bread",
    "completed": false
  },
  {
    "id": 2,
    "title": "Finish FastAPI project",
    "description": "Write tests",
    "completed": true
  }
]
```

### Filter by completion status

`GET /tasks?completed=true` → **200 OK**

```json
[
  {
    "id": 2,
    "title": "Finish FastAPI project",
    "description": "Write tests",
    "completed": true
  }
]
```

Use `?completed=false` to get unfinished tasks.

### Get a task by id

`GET /tasks/1` → **200 OK**

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs and bread",
  "completed": false
}
```

### Update a task (PATCH)

`PATCH /tasks/1`

Send **only the fields you want to change**:

```json
{
  "completed": true
}
```

Response → **200 OK** (title and description are unchanged)

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs and bread",
  "completed": true
}
```

### Delete a task

`DELETE /tasks/1` → **204 No Content** (empty body)

### Error: task not found

`GET /tasks/99` → **404 Not Found**

```json
{
  "detail": "Task with id 99 not found"
}
```

### Error: invalid data

`POST /tasks` with `{"title": ""}` → **422 Unprocessable Entity**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

`loc` tells you **where** the problem is: in the request `body`, field `title`.

### Error: missing required field

`POST /tasks` with `{"description": "no title"}` → **422 Unprocessable Entity**

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {"description": "no title"}
    }
  ]
}
```

### Try it with curl (optional)

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs and bread"}'
```

---

## 8. Run the automated tests

With the virtual environment active, from the `task_manager_api` folder:

```bash
python -m pytest -v
```

You do **not** need to start the server first. `TestClient` calls the app directly in memory.

Expected result (23 tests):

```
tests/test_tasks.py::test_health_check PASSED
tests/test_tasks.py::test_create_task PASSED
...
tests/test_tasks.py::test_delete_nonexistent_task PASSED
======================== 23 passed, 1 warning in 0.63s =========================
```

About the 1 warning: the newest Starlette (the library under FastAPI) prefers a package
called `httpx2` over `httpx`. `httpx2` needs Python 3.11+, and this project supports 3.10+,
so we keep `httpx`. The warning does not affect any test.

What the tests cover:

| Successful scenarios | Failure scenarios |
|---|---|
| Health check | Missing title → 422 |
| Create a task (201) | Empty title → 422 |
| Default values for optional fields | Title too long → 422 |
| Ids go up 1, 2, 3, ... | `completed` not a boolean → 422 |
| Get all tasks (empty and with data) | Get non-existent id → 404 |
| Get task by id | Non-integer id (`/tasks/abc`) → 422 |
| Filter `completed=true` / `false` | Invalid filter value → 422 |
| Update one field / several fields | Update non-existent id → 404 |
| Delete a task (204, then 404) | Update with invalid data → 422 (task unchanged) |
| Deleted ids are not reused | Delete non-existent id → 404 |

**How tests stay independent:** the `reset_storage` fixture in `tests/test_tasks.py`
has `autouse=True`, so pytest runs it before *every* test. It empties the `tasks`
dictionary and resets the id counter, so no test depends on another test's data or order.

Useful pytest options:

```bash
python -m pytest -v -k delete      # run only tests with "delete" in the name
python -m pytest -v -x             # stop at the first failure
```

---

## 9. Project structure

```
task_manager_api/
├── app/
│   ├── __init__.py      # Empty. Marks "app" as a Python package so we can "import app.main"
│   ├── main.py          # The FastAPI app, the in-memory storage and all endpoints
│   └── schemas.py       # Pydantic models: TaskCreate, TaskUpdate, Task
├── tests/
│   ├── __init__.py      # Empty. Lets plain "pytest" (not only "python -m pytest") find the app
│   └── test_tasks.py    # 23 automated tests
├── requirements.txt     # Packages to install
└── README.md            # This file
```

How the pieces connect:

1. A request arrives, e.g. `POST /tasks` with a JSON body.
2. FastAPI finds the matching function in `main.py` (`create_task`).
3. FastAPI validates the body with `TaskCreate` from `schemas.py`.
   Invalid → 422 is returned and the function never runs.
4. The function saves the task in the `tasks` dictionary.
5. FastAPI shapes the return value with `response_model=Task` and sends JSON back.

### The three models in `schemas.py`

| Model | Used for | Why it is separate |
|---|---|---|
| `TaskCreate` | Body of `POST /tasks` | No `id` (the server picks it). `title` is required. |
| `TaskUpdate` | Body of `PATCH /tasks/{id}` | Every field optional, because PATCH changes only what you send. |
| `Task` | Every response | Includes the `id`. |

---

## Limitations (on purpose, for learning)

- Data is lost when the server stops (no database yet).
- No login/authentication.
- Only one server process should run, because each process has its own dictionary.

These will be added in later lessons (SQLAlchemy/PostgreSQL, JWT authentication, ...).
