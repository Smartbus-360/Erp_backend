from pydantic import BaseModel

class ClassCreate(BaseModel):
    name: str
    class_coordinator_id: int | None = None


class SectionCreate(BaseModel):
    name: str
    class_id: int
    teacher_id: int | None = None



class ClassResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SectionResponse(BaseModel):
    id: int
    name: str
    class_id: int

    class Config:
        from_attributes = True
