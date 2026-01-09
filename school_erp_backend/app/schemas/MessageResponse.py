from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_role: str
    receiver_role: str
    receiver_id: Optional[int]
    category: Optional[str]
    title: Optional[str]
    message: str
    is_read: bool
    created_at: datetime
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True
