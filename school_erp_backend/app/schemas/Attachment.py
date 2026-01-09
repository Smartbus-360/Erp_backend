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
