from sqlalchemy import Column, Integer, String, Boolean,Date
from app.database import Base
from datetime import date

class StudentFee(Base):
    __tablename__ = "student_fees"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, nullable=False)
    class_id = Column(Integer, nullable=False)

    total_amount = Column(Integer, nullable=False)
    fine_amount = Column(Integer, default=0)

    paid_amount = Column(Integer, default=0)
    is_paid = Column(Boolean, default=False)
    due_date = Column(Date, nullable=False)

    created_date = Column(Date, default=date.today)



    institute_id = Column(Integer, nullable=False)
