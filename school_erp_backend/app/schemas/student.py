from pydantic import BaseModel
from datetime import date
from typing import Optional,Dict

class StudentCreate(BaseModel):
    name: str
    admission_no: str
    roll_no: str | None = None
    class_name: str
    class_id: int
    section: str | None = None
    dob: date | None = None
    gender: str | None = None
    admission_date: date | None = None
    discount_percent: int | None = None
    mobile: str | None = None

    birth_form_id: str | None = None
    orphan: str | None = None
    caste: str | None = None
    osc: str | None = None

    identification_mark: str | None = None
    previous_school: str | None = None
    religion: str | None = None
    blood_group: str | None = None

    previous_board_roll: str | None = None
    family: str | None = None
    disease: str | None = None
    total_siblings: int | None = None
    address: str | None = None

    father_name: str | None = None
    father_mobile: str | None = None
    father_occupation: str | None = None

    mother_name: str | None = None
    mother_mobile: str | None = None
    mother_occupation: str | None = None

    guardian_name: str | None = None
    guardian_relation: str | None = None
    guardian_mobile: str | None = None
    extra_fields: Optional[Dict[str, str]] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    admission_no: str
    roll_no: Optional[str] = None
    class_name: str
    section: str | None
    gender: Optional[str] = None
    

class StudentDetailResponse(BaseModel):
    id: int
    name: str
    admission_no: str
    roll_no: str | None
    class_name: str
    section: str | None
    gender: str | None

    dob: date | None = None
    admission_date: date | None = None
    mobile: str | None = None
    address: str | None = None

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True
