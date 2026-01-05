from pydantic import BaseModel

class EmployeeFormFieldCreate(BaseModel):
    field_key: str
    field_label: str
    field_type: str
    options: str | None = None
    is_required: bool = False


class EmployeeFormFieldResponse(EmployeeFormFieldCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class EmployeeExtraDataCreate(BaseModel):
    employee_id: int
    values: dict[str, str]
