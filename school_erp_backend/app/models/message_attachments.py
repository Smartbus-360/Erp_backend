from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class MessageAttachment(Base):
    __tablename__ = "message_attachments"
    __table_args__ = {"extend_existing": True}  # ✅ REQUIRED

    id = Column(Integer, primary_key=True, index=True)

    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
