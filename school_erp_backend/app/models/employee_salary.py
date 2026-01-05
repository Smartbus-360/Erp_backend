from sqlalchemy import Column, Integer
from app.database import Base

class EmployeeSalary(Base):
    __tablename__ = "employee_salary"

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, nullable=False)
    monthly_salary = Column(Integer, nullable=False)

    institute_id = Column(Integer, nullable=False)
