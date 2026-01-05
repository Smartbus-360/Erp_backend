from pydantic import BaseModel

class EmployeeLoginCreate(BaseModel):
    # employee_id: int
    email: str
    password: str
