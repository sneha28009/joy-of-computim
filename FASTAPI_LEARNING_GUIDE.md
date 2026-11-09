# FastAPI Learning Guide

A beginner's guide to the concepts used in the two projects in this folder:

- **Project One:** `task_manager_api/` — a to-do list API
- **Project Two:** `student_management_api/` — a college student API

Every concept below uses real code from these two projects, so you can open the
file and see it in context.

## Contents

1. [What is an API?](#1-what-is-an-api)
2. [What is REST?](#2-what-is-rest)
3. [What are HTTP methods?](#3-what-are-http-methods)
4. [GET, POST, PUT, PATCH and DELETE](#4-get-post-put-patch-and-delete)
5. [What is FastAPI?](#5-what-is-fastapi)
6. [Why FastAPI instead of Flask or Django?](#6-why-fastapi-instead-of-flask-or-django)
7. [What are path parameters?](#7-what-are-path-parameters)
8. [What are query parameters?](#8-what-are-query-parameters)
9. [What are request bodies?](#9-what-are-request-bodies)
10. [What is Pydantic?](#10-what-is-pydantic)
11. [What is BaseModel?](#11-what-is-basemodel)
12. [What is HTTPException?](#12-what-is-httpexception)
13. [What are status codes?](#13-what-are-status-codes)
14. [What is Uvicorn?](#14-what-is-uvicorn)
15. [What is Swagger / OpenAPI?](#15-what-is-swagger--openapi)
16. [What is Pytest?](#16-what-is-pytest)
17. [What is TestClient?](#17-what-is-testclient)
18. [How does FastAPI process an HTTP request?](#18-how-does-fastapi-process-an-http-request)
19. [Quick reference: where each concept lives in the code](#19-quick-reference-where-each-concept-lives-in-the-code)

---

## 1. What is an API?

**API** stands for **Application Programming Interface**.
It is a set of rules that lets one program ask another program for data or actions.

A restaurant comparison:

| Restaurant | Web API |
|---|---|
| You (the customer) | The **client**: a browser, mobile app, another program, or a test |
| The menu | The list of **endpoints** (`POST /tasks`, `GET /students`, ...) |
| The waiter | The **API**: takes your request, brings back a response |
| The kitchen | The **server code** and its data |

You never walk into the kitchen. You only talk to the waiter, using the menu.

**Example from Project One.** A mobile to-do app wants all unfinished tasks. It does not
read our Python dictionary directly. It sends a request:

```
GET http://127.0.0.1:8000/tasks?completed=false
```

and our API answers with JSON:

```json
[
  {"id": 1, "title": "Buy groceries", "description": "Milk, eggs and bread", "completed": false}
]
```

**JSON** (JavaScript Object Notation) is the text format most web APIs use.
It looks almost exactly like a Python dictionary/list.

---

## 2. What is REST?

**REST** (REpresentational State Transfer) is a popular *style* for designing web APIs.
It is a set of conventions, not a library. The main ideas:

1. **Everything is a resource with a URL.**
   A task is a resource. A student is a resource.
   - `/tasks` → the collection of all tasks
   - `/tasks/5` → one specific task (id 5)
   - `/students/3` → one specific student (id 3)

2. **The HTTP method says what to do with the resource.**
   The URL is the *noun*; the method is the *verb*.
   - `GET /tasks/5` → read task 5
   - `DELETE /tasks/5` → delete task 5
   - Notice we do **not** write `/deleteTask?id=5` or `/getAllStudents`.

3. **Stateless.** Every request contains everything the server needs.
   The server does not remember "who you were" between requests.

4. **Standard status codes** tell the client what happened (`200`, `201`, `404`, ...).

5. **Data travels as JSON** (usually).

Both projects follow these rules. Compare their URLs — the same shape for a different resource:

| Action | Project One | Project Two |
|---|---|---|
| Create | `POST /tasks` | `POST /students` |
| Read all | `GET /tasks` | `GET /students` |
| Read one | `GET /tasks/{task_id}` | `GET /students/{student_id}` |
| Update | `PATCH /tasks/{task_id}` | `PUT /students/{student_id}` |
| Delete | `DELETE /tasks/{task_id}` | `DELETE /students/{student_id}` |

These four basic operations are called **CRUD**: **C**reate, **R**ead, **U**pdate, **D**elete.

---

## 3. What are HTTP methods?

**HTTP** (HyperText Transfer Protocol) is the language browsers and servers use to talk.
Every HTTP request has:

| Part | Example |
|---|---|
| **Method** (what to do) | `POST` |
| **URL / path** (which resource) | `/students` |
| **Headers** (extra info) | `Content-Type: application/json` |
| **Body** (data, optional) | `{"name": "Anand Kumar", "age": 20, ...}` |

Every HTTP response has:

| Part | Example |
|---|---|
| **Status code** (what happened) | `201` |
| **Headers** | `content-type: application/json` |
| **Body** (data, optional) | `{"id": 1, "name": "Anand Kumar", ...}` |

The **method** is the verb of the request. The next section explains each one.

---

## 4. GET, POST, PUT, PATCH and DELETE

| Method | Meaning | Has a body? | Our example | Success code |
|---|---|---|---|---|
| **GET** | Read data. Never changes anything. | No | `GET /tasks`, `GET /students/1` | 200 |
| **POST** | Create something new | Yes | `POST /tasks`, `POST /students` | 201 |
| **PUT** | Replace an existing thing **completely** | Yes (all fields) | `PUT /students/1` | 200 |
| **PATCH** | Change **part** of an existing thing | Yes (only changed fields) | `PATCH /tasks/1` | 200 |
| **DELETE** | Remove something | No | `DELETE /tasks/1`, `DELETE /students/1` | 204 |

In FastAPI, each method has its own decorator:

```python
@app.get("/tasks")             # GET
@app.post("/tasks")            # POST
@app.put("/students/{student_id}")     # PUT
@app.patch("/tasks/{task_id}")         # PATCH
@app.delete("/tasks/{task_id}")        # DELETE
```

### PUT vs PATCH — the most confusing pair

This is the main difference between our two projects, chosen on purpose so you can compare.

**PATCH (Project One)** — send only what changes:

```
PATCH /tasks/1
{"completed": true}
```

Only `completed` changes. `title` and `description` stay the same.
That is why `TaskUpdate` (in `task_manager_api/app/schemas.py`) makes every field optional:

```python
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None
```

and the endpoint updates only the fields that were sent:

```python
changes = task_update.model_dump(exclude_none=True)   # e.g. {"completed": True}
tasks[task_id].update(changes)
```

**PUT (Project Two)** — send the whole new version:

```
PUT /students/1
{"name": "Anand Kumar", "age": 21, "course": "Data Science", "email": "anand@example.com"}
```

The old student is replaced completely. If you send only `{"age": 21}`, you get a
`422` error, because `name`, `course` and `email` are required. That is why the PUT
endpoint reuses `StudentCreate`, where every field is required.

**Rule of thumb:** PATCH = "edit a few fields". PUT = "here is the full new version".

---

## 5. What is FastAPI?

**FastAPI** is a modern Python framework for building web APIs.

You write ordinary Python functions with **type hints**, and FastAPI does the boring work:

```python
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    ...
```

From these two lines FastAPI knows:

- this function answers `GET` requests to `/tasks/<something>`,
- `<something>` must be converted to an `int` (else → automatic `422` error),
- the response must look like the `Task` model,
- all of this should appear in the Swagger docs at `/docs`.

FastAPI is built on top of two other libraries:

- **Starlette** — handles the web parts (routing, requests, responses).
- **Pydantic** — handles data validation (see section 10).

The smallest possible FastAPI app:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}
```

Our projects start the same way (see the top of either `app/main.py`).

---

## 6. Why FastAPI instead of Flask or Django?

All three are good, widely used Python web frameworks. They are designed for different jobs.

| | FastAPI | Flask | Django |
|---|---|---|---|
| Main purpose | Building APIs | Small/medium web apps and APIs | Full websites (pages, admin, database) |
| Size | Small | Very small ("micro") | Large ("batteries included") |
| Input validation | **Built in** (from type hints, via Pydantic) | Manual, or add a library | Forms/serializers (Django REST Framework for APIs) |
| Automatic API docs (Swagger) | **Built in** at `/docs` | Add an extension | Add a package |
| Async (`async def`) support | Built in, first-class | Supported (since 2.0) | Supported (since 3.1), partly |
| Database / ORM | Bring your own (e.g. SQLAlchemy) | Bring your own | Built in (Django ORM) |
| Admin panel | No | No | **Built in** |
| Learning curve for an API | Low | Low | Higher |

**Why FastAPI for these projects:**

1. **Less code for validation.** Compare what you would write by hand:

   ```python
   # Without Pydantic you would check every field yourself:
   if "age" not in data:
       return error("age is required")
   if not isinstance(data["age"], int):
       return error("age must be a number")
   if data["age"] < 16:
       return error("age must be at least 16")
   ```

   In our Student API, one line does all of that:

   ```python
   age: int = Field(ge=16, le=100)
   ```

2. **Free interactive documentation.** Open `/docs` and you can test every endpoint
   in the browser — very useful when demonstrating a project.

3. **Clear error messages.** The client is told exactly which field is wrong and why.

4. **Type hints everywhere,** so your editor can autocomplete and catch mistakes.

**When the others are a better fit:** choose **Django** for a full website with HTML
pages, user accounts and an admin panel. Choose **Flask** when you want the smallest
possible framework and prefer to pick every piece yourself.

---

## 7. What are path parameters?

A **path parameter** is a variable part **inside the URL path**.
It usually identifies *which* resource you want.

```
GET /tasks/5
           ^
           task_id = 5
```

In FastAPI you write it in curly braces, and add a parameter with **the same name** to the function:

```python
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return tasks[task_id]
```

Because of `task_id: int`:

| Request | What happens |
|---|---|
| `GET /tasks/5` | `task_id` is the integer `5` |
| `GET /tasks/abc` | Automatic **422** error: "Input should be a valid integer" |

Both projects use path parameters for get, update and delete:
`/tasks/{task_id}` and `/students/{student_id}`.

### Watch out: route order and trailing slashes

FastAPI checks routes in the order they are written. `/students/{student_id}` matches
**any** single word after `/students/`, including `search`. That is why in Project Two:

- `GET /students/search/?name=Anand` → the search endpoint ✅ (the trailing `/` makes it a different path)
- `GET /students/search?name=Anand` → matched as `student_id = "search"` → **422** ❌

Lesson: fixed paths (`/students/search/`) and parameter paths (`/students/{student_id}`)
can collide. Be careful when designing URLs.

---

## 8. What are query parameters?

A **query parameter** comes **after a `?`** in the URL, as `key=value` pairs
(several are joined with `&`). Query parameters usually **filter, search or sort**.

```
GET /tasks?completed=true
           ^^^^^^^^^^^^^^
           query parameter: completed = true
```

In FastAPI, **any function parameter that is not in the path** (and is a simple type
like `int`, `str`, `bool`) is a query parameter.

**Project One — optional filter:**

```python
@app.get("/tasks", response_model=list[Task])
def get_tasks(completed: bool | None = None):
    if completed is None:
        return list(tasks.values())
    return [task for task in tasks.values() if task["completed"] == completed]
```

| Request | `completed` value | Result |
|---|---|---|
| `GET /tasks` | `None` (default) | all tasks |
| `GET /tasks?completed=true` | `True` | finished tasks |
| `GET /tasks?completed=false` | `False` | unfinished tasks |
| `GET /tasks?completed=maybe` | – | **422** error |

Because it has a default value (`= None`), the parameter is **optional**.

**Project Two — required search text:**

```python
@app.get("/students/search/", response_model=list[Student])
def search_students(name: str = Query(min_length=1)):
    ...
```

`Query(min_length=1)` has **no default value**, so `name` is **required**
and cannot be empty. `GET /students/search/` without `?name=` → **422**.

### Path parameter vs query parameter

| | Path parameter | Query parameter |
|---|---|---|
| Where | Inside the path: `/tasks/5` | After `?`: `/tasks?completed=true` |
| Usually means | *Which* item | *How* to filter/search/sort |
| Usually | Required | Optional |
| Our examples | `task_id`, `student_id` | `completed`, `name` |

---

## 9. What are request bodies?

A **request body** is data the client sends **inside** the request (not in the URL),
usually as JSON. It is used with **POST, PUT and PATCH** to send the data to create
or update.

```
POST /students
Content-Type: application/json

{
  "name": "Anand Kumar",
  "age": 20,
  "course": "Computer Science",
  "email": "anand@example.com"
}
```

In FastAPI, a function parameter whose type is a **Pydantic model** is read from the body:

```python
@app.post("/students", response_model=Student, status_code=201)
def register_student(student: StudentCreate):   # <- read from the JSON body
    ...
    new_student = {"id": next_id, **student.model_dump()}
```

Inside the function, `student` is already a validated Python object:
`student.name == "Anand Kumar"`, `student.age == 20`.

One endpoint can use all three kinds of input at once:

```python
@app.put("/students/{student_id}")                         # path parameter
def update_student(student_id: int, student: StudentCreate):  # + request body
```

How FastAPI decides where each parameter comes from:

| Parameter looks like | FastAPI reads it from |
|---|---|
| Its name is in the path, e.g. `{student_id}` | The **path** |
| A simple type (`int`, `str`, `bool`, ...) not in the path | The **query string** |
| A Pydantic model (`StudentCreate`, `TaskUpdate`) | The **request body** |

---

## 10. What is Pydantic?

**Pydantic** is a Python library for **data validation** using type hints.
You describe what valid data looks like, and Pydantic checks real data against it.

FastAPI uses Pydantic for every request body and response.

What Pydantic does for us:

1. **Checks types.** `"age": "twenty"` → error, `age` must be an integer.
2. **Checks rules.** `Field(ge=16)` → age must be 16 or more.
3. **Checks required fields.** No `email` → "Field required".
4. **Fills defaults.** No `completed` in a new task → `False`.
5. **Reports every problem at once**, with the exact location.

Real example from Project Two — sending
`{"name": "A", "age": 10, "course": "Maths", "email": "not-an-email"}`
returns three errors in one response:

```json
{
  "detail": [
    {"loc": ["body", "name"],  "msg": "String should have at least 2 characters", "...": "..."},
    {"loc": ["body", "age"],   "msg": "Input should be greater than or equal to 16", "...": "..."},
    {"loc": ["body", "email"], "msg": "value is not a valid email address: An email address must have an @-sign.", "...": "..."}
  ]
}
```

(Shortened. The full response is in the Project Two README.)

### `Field(...)` — extra rules on a field

| Rule | Meaning | Our example |
|---|---|---|
| `min_length=1` | String has at least 1 character | Task `title` |
| `max_length=100` | String has at most 100 characters | Task `title`, student `name` |
| `ge=16` | Number ≥ 16 ("greater than or equal") | Student `age` |
| `le=100` | Number ≤ 100 ("less than or equal") | Student `age` |
| `default=""` | Value used when the field is missing | Task `description` |
| `examples=[...]` | Example shown in Swagger | Several fields |

### `EmailStr` — a ready-made email type

```python
email: EmailStr
```

Checks the value looks like a real email address. It needs the extra package
`email-validator`, which is why it is in Project Two's `requirements.txt`.

---

## 11. What is BaseModel?

`BaseModel` is the **class you inherit from** to create a Pydantic model.
Each class attribute with a type hint becomes a field.

From `task_manager_api/app/schemas.py`:

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    completed: bool = False
```

How to read it:

| Line | Meaning |
|---|---|
| `class TaskCreate(BaseModel)` | A new model called `TaskCreate` |
| `title: str = Field(min_length=1, ...)` | Required string, 1–100 characters (no default → required) |
| `description: str = Field(default="", ...)` | Optional string, defaults to `""` |
| `completed: bool = False` | Optional boolean, defaults to `False` |

Using a model in plain Python (outside FastAPI):

```python
task = TaskCreate(title="Buy milk")
print(task.title)          # Buy milk
print(task.completed)      # False  (the default)
print(task.model_dump())   # {'title': 'Buy milk', 'description': '', 'completed': False}

TaskCreate(title="")       # raises ValidationError: String should have at least 1 character
```

`model_dump()` turns the model into a normal dictionary. We use it to store data
in our in-memory dictionaries.

### Why several models for one resource?

| Model | Used for | Has `id`? | Fields required? |
|---|---|---|---|
| `TaskCreate` | `POST /tasks` body | No — the server chooses the id | `title` required |
| `TaskUpdate` | `PATCH /tasks/{id}` body | No | All optional |
| `Task` | Every response | **Yes** | All present |
| `StudentCreate` | `POST /students` and `PUT /students/{id}` body | No | All required |
| `Student` | Every response | **Yes** | All present |

The client should never choose the `id`, so input models do not have one.
Responses always include it, so output models do.

### `response_model`

```python
@app.post("/tasks", response_model=Task, status_code=201)
```

`response_model=Task` tells FastAPI: "whatever this function returns, send it in the
shape of `Task`". It also shows the response shape in Swagger.

---

## 12. What is HTTPException?

`HTTPException` is how you **stop an endpoint and return an error** to the client.
You `raise` it (like any Python exception) with a status code and a message.

From both projects:

```python
from fastapi import HTTPException, status

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return tasks[task_id]
```

What the client receives for `GET /tasks/99`:

```
Status: 404 Not Found
{"detail": "Task with id 99 not found"}
```

Our projects raise `HTTPException` for:

| Situation | Status code | Project |
|---|---|---|
| The id does not exist | 404 Not Found | Both |
| The email belongs to another student | 409 Conflict | Two |

### HTTPException vs validation errors

You **do not** raise anything for invalid input data (wrong type, too short, missing field).
Pydantic + FastAPI do that **before** your function runs, and return **422** automatically.

You raise `HTTPException` for problems only **your code** can know about:
"this id is not in my dictionary", "this email is already used".

### `status.HTTP_404_NOT_FOUND` vs `404`

They are the same number. `status.HTTP_404_NOT_FOUND` is just a named constant that
makes the code easier to read. Both styles work.

---

## 13. What are status codes?

A **status code** is a 3-digit number in every response that says what happened.
The first digit tells you the category:

| Range | Category | Meaning |
|---|---|---|
| 2xx | Success | It worked |
| 3xx | Redirection | Look somewhere else |
| 4xx | Client error | **The request** was wrong (bad data, missing item) |
| 5xx | Server error | **The server code** crashed or failed |

Codes used in our projects:

| Code | Name | When we use it | Example |
|---|---|---|---|
| **200** | OK | Successful GET, PUT, PATCH | `GET /tasks` |
| **201** | Created | Successful POST (something new exists) | `POST /students` |
| **204** | No Content | Successful DELETE (nothing to send back) | `DELETE /tasks/1` |
| **404** | Not Found | The id does not exist | `GET /students/99` |
| **409** | Conflict | Request clashes with existing data | Duplicate student email |
| **422** | Unprocessable Entity | Data has the wrong shape or breaks a rule | `{"title": ""}` |

The default for a FastAPI endpoint is **200**. To use another code on success,
set `status_code` in the decorator:

```python
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
```

---

## 14. What is Uvicorn?

Your FastAPI code is the **application**. It defines what to answer.
**Uvicorn** is the **server**. It listens on a network port, receives HTTP requests,
passes them to your app, and sends the answers back.

```bash
uvicorn app.main:app --reload
```

| Part | Meaning |
|---|---|
| `uvicorn` | Start the Uvicorn server |
| `app.main` | Python module: the file `app/main.py` |
| `:app` | The variable inside it: `app = FastAPI(...)` |
| `--reload` | Restart automatically when code changes (for development only) |
| `--port 8001` | (optional) Use another port, default is 8000 |

Uvicorn is an **ASGI server**. ASGI (Asynchronous Server Gateway Interface) is the
standard way async Python servers and web frameworks talk to each other.
(Flask and classic Django use the older **WSGI** standard.)

Restaurant comparison again: Uvicorn is the **front door and the waiter**;
FastAPI is the **kitchen** that knows the recipes.

---

## 15. What is Swagger / OpenAPI?

**OpenAPI** is a standard format (a big JSON document) that describes an API:
every endpoint, every parameter, every request body and every possible response.

FastAPI **generates this document automatically** from your code at:

```
http://127.0.0.1:8000/openapi.json
```

**Swagger UI** is a web page that reads that document and shows interactive docs:

```
http://127.0.0.1:8000/docs
```

**ReDoc** is another, read-only view of the same document:

```
http://127.0.0.1:8000/redoc
```

Everything you see in Swagger comes from your code:

| In Swagger | Comes from |
|---|---|
| Page title "Task Management API" | `FastAPI(title="Task Management API", ...)` |
| Endpoint description | The function's docstring (`"""..."""`) |
| Example request body | `Field(examples=["Buy groceries"])` and the Pydantic model |
| Response shape | `response_model=Task` |
| Required/optional fields, min/max rules | `Field(min_length=..., ge=..., ...)` |

**Try it:**

1. Start a project: `uvicorn app.main:app --reload`
2. Open <http://127.0.0.1:8000/docs>
3. Click **POST /tasks** → **Try it out**
4. Change the JSON, click **Execute**
5. See the real response (status code and body) below

It is the easiest way to demonstrate your API without writing any client code.

---

## 16. What is Pytest?

**Pytest** is the most popular Python testing tool. A test is a function whose name
starts with `test_`, in a file whose name starts with `test_`, that uses `assert`
to check something is true.

```python
def test_create_task():
    response = client.post("/tasks", json={"title": "Buy milk", "description": "2 litres"})

    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"
```

If every `assert` is true → **PASSED**. If any `assert` is false → **FAILED**,
and pytest shows the values that did not match.

Run all tests (from inside a project folder):

```bash
python -m pytest -v
```

`-v` (verbose) prints one line per test:

```
tests/test_tasks.py::test_create_task PASSED
tests/test_tasks.py::test_get_nonexistent_task PASSED
...
======================== 23 passed, 1 warning in 0.63s ========================
```

### Fixtures

A **fixture** is a function that prepares something a test needs. A test asks for a
fixture by putting its name in the test's parameters.

```python
@pytest.fixture
def sample_task():
    """Create one task through the API and return its JSON."""
    response = client.post("/tasks", json={"title": "Buy milk", "description": "2 litres"})
    return response.json()

def test_delete_task(sample_task):          # pytest runs sample_task() first
    response = client.delete(f"/tasks/{sample_task['id']}")
    assert response.status_code == 204
```

### Keeping tests independent: `autouse=True`

Our data lives in a global dictionary. If test A creates a task and test B counts
tasks, test B's result would depend on whether A ran first. That is a fragile test.

The fix (in both test files):

```python
@pytest.fixture(autouse=True)
def reset_storage():
    main.tasks.clear()   # empty the dictionary
    main.next_id = 1     # restart ids at 1
```

`autouse=True` means pytest runs this fixture **before every test automatically**.
Every test starts with empty storage, so the order of tests never matters.

### Arrange – Act – Assert

Every test in these projects has the same three parts:

```python
def test_update_task(sample_task):                          # Arrange (fixture creates a task)
    response = client.patch(                                # Act
        f"/tasks/{sample_task['id']}", json={"completed": True}
    )
    assert response.status_code == 200                      # Assert
    assert response.json()["completed"] is True
```

---

## 17. What is TestClient?

`TestClient` lets your tests **send HTTP requests to your FastAPI app without starting
a server**. It calls the app directly in memory, which makes tests fast and simple.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get("/tasks/1")       # like a browser calling GET /tasks/1
response.status_code                    # 200, 404, ...
response.json()                         # the JSON body as a Python dict/list
```

It has one method per HTTP method:

| Method | Example from our tests |
|---|---|
| `client.get(url)` | `client.get("/students/999")` |
| `client.get(url, params={...})` | `client.get("/tasks", params={"completed": True})` → `/tasks?completed=true` |
| `client.post(url, json={...})` | `client.post("/students", json=VALID_STUDENT)` |
| `client.put(url, json={...})` | `client.put("/students/1", json=updated)` |
| `client.patch(url, json={...})` | `client.patch("/tasks/1", json={"completed": True})` |
| `client.delete(url)` | `client.delete("/tasks/1")` |

`TestClient` is built on the **HTTPX** library — that is why `httpx` is in
`requirements.txt` even though our app code never imports it.

The test goes through **the whole FastAPI pipeline**: routing, validation,
your function, `HTTPException`, `response_model`. So a passing test means the
real endpoint works, not just the Python function.

---

## 18. How does FastAPI process an HTTP request?

Let's follow one real request through Project Two, step by step:

```
POST /students
Content-Type: application/json

{"name": "Anand Kumar", "age": 20, "course": "Computer Science", "email": "anand@example.com"}
```

1. **The client sends the request.**
   A browser, Swagger UI, curl, a mobile app, or `TestClient` in a test.

2. **Uvicorn receives it.**
   Uvicorn listens on port 8000, reads the raw HTTP message and hands it to the
   FastAPI `app` (using the ASGI standard).
   *(In tests, `TestClient` skips Uvicorn and hands the request to `app` directly.)*

3. **FastAPI finds the matching route.**
   It compares the method + path with every decorator, in order, and finds
   `@app.post("/students")` → the function `register_student`.
   No match → **404** `{"detail": "Not Found"}`.
   Path matches but wrong method (e.g. `PATCH /students/1`) → **405 Method Not Allowed**.

4. **FastAPI collects the inputs.**
   It looks at the function's parameters:
   `register_student(student: StudentCreate)` → `StudentCreate` is a Pydantic model →
   read the JSON **body**.

5. **Pydantic validates the inputs.**
   Is `name` 2–100 characters? Is `age` an integer between 16 and 100?
   Is `email` a valid address? Are all fields present?
   Anything wrong → FastAPI returns **422** with the list of problems,
   and **your function never runs.**

6. **FastAPI calls your function** with clean, validated data:
   `student.name == "Anand Kumar"`, `student.age == 20`.

7. **Your code runs the business logic.**
   - `is_email_taken(student.email)` → already used? → `raise HTTPException(409, ...)`.
     FastAPI turns that into a **409** response and stops here.
   - Otherwise build the dict, store it in `students`, increase `next_id`.
   - `return new_student`

8. **FastAPI prepares the response.**
   It checks the return value against `response_model=Student`, converts it to
   JSON, and uses `status_code=201` from the decorator.

9. **Uvicorn sends the response back to the client:**

   ```
   201 Created
   {"id": 1, "name": "Anand Kumar", "age": 20, "course": "Computer Science", "email": "anand@example.com"}
   ```

### The same pipeline in our tests

| Step | Test that proves it works |
|---|---|
| 3. Route matching | `test_get_student_by_id` (correct route found) |
| 5. Validation stops bad data | `test_register_student_invalid_email` → 422 |
| 7. `HTTPException` from our logic | `test_register_duplicate_email` → 409, `test_get_nonexistent_student` → 404 |
| 8. Status code from the decorator | `test_register_student` → 201 |
| Whole pipeline | `test_update_student` (PUT, then GET shows the saved change) |

---

## 19. Quick reference: where each concept lives in the code

| Concept | Project One (`task_manager_api/`) | Project Two (`student_management_api/`) |
|---|---|---|
| Create the app | `app/main.py`: `app = FastAPI(...)` | `app/main.py`: `app = FastAPI(...)` |
| In-memory storage | `tasks: dict[int, dict] = {}` | `students: dict[int, dict] = {}` |
| Health check | `health_check()` → `GET /` | `health_check()` → `GET /` |
| Path parameter | `get_task(task_id: int)` | `get_student(student_id: int)` |
| Query parameter | `get_tasks(completed: bool \| None = None)` | `search_students(name: str = Query(min_length=1))` |
| Request body | `create_task(task: TaskCreate)` | `register_student(student: StudentCreate)` |
| BaseModel + Field | `app/schemas.py`: `TaskCreate`, `TaskUpdate`, `Task` | `app/schemas.py`: `StudentCreate`, `Student` |
| Special type | – | `EmailStr` |
| HTTPException 404 | `get_task`, `update_task`, `delete_task` | `get_student`, `update_student`, `delete_student` |
| HTTPException 409 | – | `register_student`, `update_student` |
| Status 201 / 204 | `create_task` / `delete_task` | `register_student` / `delete_student` |
| PATCH (partial update) | `update_task` | – |
| PUT (full update) | – | `update_student` |
| Tests | `tests/test_tasks.py` (23 tests) | `tests/test_students.py` (29 tests) |
| Fixture reset | `reset_storage` (`autouse=True`) | `reset_storage` (`autouse=True`) |

### Practice ideas (to check your understanding)

1. Add a `GET /tasks/count` endpoint that returns `{"count": <number of tasks>}`.
   Where must it go relative to `/tasks/{task_id}`, and why? Write a test for it.
2. Add a `PATCH /students/{student_id}` that changes only the fields sent
   (hint: copy the idea of `TaskUpdate`).
3. Add an optional `?course=` query parameter to `GET /students` to filter by course.
4. Make task titles unique (hint: copy the idea of `is_email_taken`) and return `409`.
