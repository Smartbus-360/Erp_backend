from pydantic import BaseModel
from datetime import date
from typing import Literal
from typing import List, Optional

class FeeStructureCreate(BaseModel):
    class_id: int | None = None
    section_id: int | None = None
    student_id: int | None = None
    fee_name: str
    amount: int
    scope: Literal["ALL", "CLASS", "STUDENT"]



class GenerateFee(BaseModel):
    student_id: int
    class_id: int


class CollectFee(BaseModel):
    student_fee_id: int
    amount: int
    payment_mode: str
    payment_date: date

class FeeItem(BaseModel):
    fee_name: str
    amount: float

class SaveFeeStructureRequest(BaseModel):
    scope: str                     # ALL | CLASS | STUDENT
    class_id: Optional[int] = None
    section_id: Optional[int] = None
    student_id: Optional[int] = None
    fees: List[FeeItem]
