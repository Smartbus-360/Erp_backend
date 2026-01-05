from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, nullable=False)
    month = Column(String(20))     # Jan-2025
    amount = Column(Integer, nullable=False)
    payment_date = Column(Date)
    payment_mode = Column(String(50))

    institute_id = Column(Integer, nullable=False)
