"""
Student Management API
----------------------
A small REST API to register, read, search, update and delete college students.

Start the server (from the student_management_api folder):
    uvicorn app.main:app --reload

Then open the interactive docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query, status

from app.schemas import Student, StudentCreate

# Create the FastAPI application.
# The title, description and version are shown at the top of Swagger (/docs).
app = FastAPI(
    title="Student Management API",
    description="A beginner-friendly API to manage college students.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------
# Students live in a normal Python dictionary:  {student_id: student_data}
# Example:
#   {1: {"id": 1, "name": "Anand", "age": 20,
#        "course": "Computer Science", "email": "anand@example.com"}}
#
# Everything is lost when the server stops. We will use a real database later.
students: dict[int, dict] = {}

# The id that the NEXT new student will get. It only ever goes up,
# so the id of a deleted student is never reused for a new student.
next_id = 1


# ---------------------------------------------------------------------------
# Helper function
# ---------------------------------------------------------------------------


def is_email_taken(email: str, ignore_student_id: int | None = None) -> bool:
    """
    Return True if another student already uses this email.

    The check ignores upper/lower case, so "Anand@Example.com" and
    "anand@example.com" count as the same email.

    ignore_student_id lets a student keep their own email when updating.
    """
    for student in students.values():
        same_email = student["email"].lower() == email.lower()
        if same_email and student["id"] != ignore_student_id:
            return True
    return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def health_check():
    """Health check: a quick way to confirm that the server is running."""
    return {"status": "ok", "message": "Student Management API is running"}


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def register_student(student: StudentCreate):
    """
    Register a new student.

    `student: StudentCreate` tells FastAPI to read the JSON request body and
    validate it with the StudentCreate model. If the data is invalid, FastAPI
    returns 422 automatically and this function never runs.
    """
    # We change the module-level counter, so Python needs the word "global".
    global next_id

    # Two students cannot share one email -> 409 Conflict.
    if is_email_taken(student.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with email {student.email} already exists",
        )

    # model_dump() turns the Pydantic object into a dict.
    # The ** copies its keys (name, age, course, email) into the new dict.
    new_student = {"id": next_id, **student.model_dump()}
    students[next_id] = new_student
    next_id += 1
    return new_student


@app.get("/students", response_model=list[Student])
def get_students():
    """Get all students."""
    return list(students.values())


@app.get("/students/search", response_model=list[Student])
def search_students(name: str = Query(min_length=1)):
    """
    Search students by name:  GET /students/search/?name=Anand

    `name` is a QUERY parameter. Query(min_length=1) makes it required and
    non-empty. The search is case-insensitive and matches part of a name,
    so "an" finds "Anand" and "Hannah". No match returns an empty list.
    """
    search_text = name.lower()
    return [
        student
        for student in students.values()
        if search_text in student["name"].lower()
    ]


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """
    Get one student by id.

    `{student_id}` in the path is a PATH parameter. FastAPI converts it to int,
    so /students/abc returns 422 automatically.
    """
    if student_id not in students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    return students[student_id]


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate):
    """Replace ALL information of an existing student (PUT = full update)."""
    if student_id not in students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    # The new email must not belong to a DIFFERENT student.
    if is_email_taken(student.email, ignore_student_id=student_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with email {student.email} already exists",
        )

    # Replace the old data completely, but keep the same id.
    students[student_id] = {"id": student_id, **student.model_dump()}
    return students[student_id]


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    """
    Delete a student.

    204 No Content means "it worked, and there is nothing to send back".
    """
    if student_id not in students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    del students[student_id]
