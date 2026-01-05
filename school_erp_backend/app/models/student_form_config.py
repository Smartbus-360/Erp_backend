from sqlalchemy import Column, Integer, Boolean
from app.database import Base

class StudentFormConfig(Base):
    __tablename__ = "student_form_config"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, unique=True)

    show_admission_no = Column(Boolean, default=True)
    show_section = Column(Boolean, default=True)

    show_dob = Column(Boolean, default=True)
    show_gender = Column(Boolean, default=True)
    show_caste = Column(Boolean, default=True)
    show_religion = Column(Boolean, default=True)
    show_blood_group = Column(Boolean, default=True)
    show_orphan = Column(Boolean, default=False)
    show_osc = Column(Boolean, default=False)

    show_parents = Column(Boolean, default=True)
