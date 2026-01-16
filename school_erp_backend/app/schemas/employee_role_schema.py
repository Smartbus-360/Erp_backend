from pydantic import BaseModel

class EmployeeRoleCreate(BaseModel):
    name: str

class EmployeeRoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
