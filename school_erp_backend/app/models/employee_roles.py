from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)

    name = Column(String(100), nullable=False)   # Teacher, Driver, Librarian

    is_active = Column(Boolean, default=True)
