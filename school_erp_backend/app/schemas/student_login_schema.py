from pydantic import BaseModel

class StudentLoginCreate(BaseModel):
    # student_id: int
    email: str
    password: str

class StudentLoginUpdate(BaseModel):
    email: str

class StudentPasswordUpdate(BaseModel):
    password: str
