# app/schemas/message.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    receiver_role: str
    # institute / employee / student

    send_scope: str
# "class" | "class_section"

class_id: Optional[int] = None
section: Optional[str] = None


    title: Optional[str] = None
    message: str

