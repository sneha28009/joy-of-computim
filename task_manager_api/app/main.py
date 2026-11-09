"""
Task Management API
-------------------
A small REST API to Create, Read, Update and Delete (CRUD) tasks.

Start the server (from the task_manager_api folder):
    uvicorn app.main:app --reload

Then open the interactive docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, status

from app.schemas import Task, TaskCreate, TaskUpdate

# Create the FastAPI application.
# The title, description and version are shown at the top of Swagger (/docs).
app = FastAPI(
    title="Task Management API",
    description="A beginner-friendly API to manage a simple to-do list.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------
# Tasks live in a normal Python dictionary:  {task_id: task_data}
# Example:
#   {1: {"id": 1, "title": "Buy milk", "description": "", "completed": False}}
#
# Everything is lost when the server stops. We will use a real database later.
tasks: dict[int, dict] = {}

# The id that the NEXT new task will get. It only ever goes up,
# so the id of a deleted task is never reused for a new task.
next_id = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def health_check():
    """Health check: a quick way to confirm that the server is running."""
    return {"status": "ok", "message": "Task Management API is running"}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """
    Create a new task.

    `task: TaskCreate` tells FastAPI to read the JSON request body and
    validate it with the TaskCreate model. If the data is invalid, FastAPI
    returns 422 automatically and this function never runs.
    """
    # We change the module-level counter, so Python needs the word "global".
    global next_id

    # model_dump() turns the Pydantic object into a dict.
    # The ** copies its keys (title, description, completed) into the new dict.
    new_task = {"id": next_id, **task.model_dump()}
    tasks[next_id] = new_task
    next_id += 1
    return new_task


@app.get("/tasks", response_model=list[Task])
def get_tasks(completed: bool | None = None):
    """
    Get all tasks, optionally filtered by completion status.

    `completed` is not part of the URL path, so FastAPI treats it as a
    QUERY parameter:
        GET /tasks                  -> all tasks
        GET /tasks?completed=true   -> only finished tasks
        GET /tasks?completed=false  -> only unfinished tasks
    """
    # The client did not send ?completed=... so return everything.
    if completed is None:
        return list(tasks.values())

    # Otherwise keep only the tasks whose "completed" value matches.
    return [task for task in tasks.values() if task["completed"] == completed]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    """
    Get one task by its id.

    `{task_id}` in the path is a PATH parameter. FastAPI converts it to int,
    so /tasks/abc returns 422 automatically.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return tasks[task_id]


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    """Update some (or all) fields of an existing task."""
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Keep only the fields the client actually sent.
    # exclude_none=True drops every field that is still None.
    # Example: {"completed": true} -> only "completed" changes.
    changes = task_update.model_dump(exclude_none=True)
    tasks[task_id].update(changes)
    return tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """
    Delete a task.

    204 No Content means "it worked, and there is nothing to send back".
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    del tasks[task_id]
