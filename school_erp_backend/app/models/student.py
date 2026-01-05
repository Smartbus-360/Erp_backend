from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    admission_no = Column(String(50), nullable=False)
    roll_no = Column(String(50), nullable=True)


    class_name = Column(String(50), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    section = Column(String(10), nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    dob = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)

    admission_date = Column(Date, nullable=True)
    discount_percent = Column(Integer, nullable=True)
    mobile = Column(String(20), nullable=True)

    birth_form_id = Column(String(50), nullable=True)
    orphan = Column(String(10), nullable=True)
    caste = Column(String(50), nullable=True)
    osc = Column(String(10), nullable=True)

    identification_mark = Column(String(255), nullable=True)
    previous_school = Column(String(255), nullable=True)
    religion = Column(String(50), nullable=True)
    blood_group = Column(String(10), nullable=True)

    previous_board_roll = Column(String(50), nullable=True)
    family = Column(String(100), nullable=True)
    disease = Column(String(255), nullable=True)
    total_siblings = Column(Integer, nullable=True)
    address = Column(String(500), nullable=True)

    # Parents
    father_name = Column(String(150), nullable=True)
    father_mobile = Column(String(20), nullable=True)
    father_occupation = Column(String(100), nullable=True)

    mother_name = Column(String(150), nullable=True)
    mother_mobile = Column(String(20), nullable=True)
    mother_occupation = Column(String(100), nullable=True)

    guardian_name = Column(String(150), nullable=True)
    guardian_relation = Column(String(50), nullable=True)
    guardian_mobile = Column(String(20), nullable=True)

    institute_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", backref="student", uselist=False)
    school_class = relationship("SchoolClass")
    section_rel = relationship("Section")
