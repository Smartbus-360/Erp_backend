from sqlalchemy import Column, Integer, String
from app.database import Base

class FeeFineRule(Base):
    __tablename__ = "fee_fine_rules"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)

    fine_type = Column(String(20))  
    # daily / monthly / custom

    fine_amount = Column(Integer, nullable=False)
    grace_days = Column(Integer, default=0)
    grace_months = Column(Integer, default=0)
