from pydantic import BaseModel

class StudentFormConfigResponse(BaseModel):
    show_admission_no: bool
    show_section: bool
    show_dob: bool
    show_gender: bool
    show_caste: bool
    show_religion: bool
    show_blood_group: bool
    show_orphan: bool
    show_osc: bool
    show_parents: bool

    class Config:
        from_attributes = True
