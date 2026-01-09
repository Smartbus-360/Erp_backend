# app/schemas/message.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    receiver_role: str
    # institute / employee / student

    receiver_id: Optional[int] = None
    # null = broadcast

    category: Optional[str] = None
    # teacher / driver / accountant etc.

    title: Optional[str] = None
    message: str

