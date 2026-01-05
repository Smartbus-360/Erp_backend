from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True)

    student_fee_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    payment_mode = Column(String(50))   # cash, online
    payment_date = Column(Date)

    institute_id = Column(Integer, nullable=False)
