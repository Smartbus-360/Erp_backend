from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class StudentFormField(Base):
    __tablename__ = "student_form_fields"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)

    field_key = Column(String(50), nullable=False)
    field_label = Column(String(100), nullable=False)
    field_type = Column(String(20), nullable=False)  
    # text, date, dropdown, number
    options = Column(String(500), nullable=True)


    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
