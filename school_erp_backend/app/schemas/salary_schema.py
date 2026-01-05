from pydantic import BaseModel
from datetime import date

class SetSalary(BaseModel):
    employee_id: int
    monthly_salary: int


class PaySalary(BaseModel):
    employee_id: int
    month: str
    amount: int
    payment_date: date
    payment_mode: str
