import os
import uuid
from fastapi import UploadFile, HTTPException
from app.config import MESSAGE_UPLOAD_DIR, ALLOWED_FILE_TYPES


def save_message_file(file: UploadFile):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    os.makedirs(MESSAGE_UPLOAD_DIR, exist_ok=True)

    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(MESSAGE_UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {
        "file_name": file.filename,
        "file_path": file_path,
        "file_type": file.content_type
    }
