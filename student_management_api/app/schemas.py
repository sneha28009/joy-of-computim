"""
Pydantic models (also called "schemas").

A schema describes the SHAPE of the data:
- which fields exist,
- what type each field has,
- which rules each field must follow (for example "age must be at least 16").

FastAPI uses these classes to:
1. Validate the JSON the client sends (bad data -> automatic 422 error).
2. Decide what the JSON response looks like.
3. Draw the request/response examples in Swagger (/docs).
"""

from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    """
    The data a client sends to REGISTER a student (POST /students)
    and to UPDATE a student (PUT /students/{student_id}).

    PUT replaces the WHOLE student, so it needs every field, exactly like
    registering. That is why both endpoints share this one model.
    (Compare with the Task API, where PATCH uses a separate model
    with optional fields.)
    """

    name: str = Field(min_length=2, max_length=100, examples=["Anand Kumar"])
    # ge = "greater than or equal", le = "less than or equal"
    age: int = Field(ge=16, le=100, examples=[20])
    course: str = Field(min_length=2, max_length=100, examples=["Computer Science"])
    # EmailStr checks the value looks like a real email address (name@domain.com).
    email: EmailStr = Field(examples=["anand@example.com"])


class Student(BaseModel):
    """A student exactly as the API sends it back to the client."""

    id: int
    name: str
    age: int
    course: str
    email: str
