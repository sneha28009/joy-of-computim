"""
Pydantic models (also called "schemas").

A schema describes the SHAPE of the data:
- which fields exist,
- what type each field has,
- which rules each field must follow (for example "title cannot be empty").

FastAPI uses these classes to:
1. Validate the JSON the client sends (bad data -> automatic 422 error).
2. Decide what the JSON response looks like.
3. Draw the request/response examples in Swagger (/docs).
"""

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """The data a client sends to CREATE a task (POST /tasks)."""

    # Field(...) adds validation rules on top of the type.
    title: str = Field(min_length=1, max_length=100, examples=["Buy groceries"])
    # Has a default value, so the client may leave it out.
    description: str = Field(default="", max_length=500, examples=["Milk, eggs and bread"])
    completed: bool = False


class TaskUpdate(BaseModel):
    """
    The data a client sends to UPDATE a task (PATCH /tasks/{task_id}).

    PATCH means "change only some fields", so every field is optional.
    None means "the client did not send this field, leave it unchanged".
    """

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


class Task(BaseModel):
    """A task exactly as the API sends it back to the client."""

    id: int
    title: str
    description: str
    completed: bool
