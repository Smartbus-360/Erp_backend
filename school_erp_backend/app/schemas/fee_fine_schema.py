from pydantic import BaseModel

class FeeFineCreate(BaseModel):
    fine_type: str
    fine_amount: int
    grace_days: int | None = 0
    grace_months: int | None = 0
