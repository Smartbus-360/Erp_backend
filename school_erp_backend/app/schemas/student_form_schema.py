from pydantic import BaseModel

class StudentFormFieldCreate(BaseModel):
    field_key: str
    field_label: str
    field_type: str
    options: str | None = None
    is_required: bool = False


class StudentFormFieldResponse(StudentFormFieldCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class StudentExtraDataCreate(BaseModel):
    student_id: int
    values: dict[str, str]
