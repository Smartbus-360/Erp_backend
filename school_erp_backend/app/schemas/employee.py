from pydantic import BaseModel
from typing import Optional, Dict

class EmployeeCreate(BaseModel):
    name: str
    designation: str | None = None
    phone: str | None = None
    gender: str | None = None
    religion: str | None = None
    education: str | None = None
    address: str | None = None

    extra_fields: Optional[Dict[str, str]] = {}


class EmployeeResponse(BaseModel):
    id: int
    name: str
    designation: str | None
    phone: str | None

    class Config:
        from_attributes = True


class EmployeeCreateResponse(BaseModel):
    id: int
    name: str
    designation: str | None
    phone: str | None

    class Config:
        from_attributes = True

class PermissionUpdate(BaseModel):
    can_students: bool = False
    can_attendance: bool = False
    can_exams: bool = False
    can_fees: bool = False
    can_salary: bool = False
    can_homework: bool = False

class EmployeeListResponse(BaseModel):
    id: int
    name: str
    designation: str | None
    phone: str | None
    has_login: bool
    login_email: str | None
    is_active: bool

    class Config:
        from_attributes = True
