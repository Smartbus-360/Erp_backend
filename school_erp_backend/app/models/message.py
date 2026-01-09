from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # sender
    sender_id = Column(Integer, nullable=False)
    sender_role = Column(String(20), nullable=False)
    # admin / employee / student

    # receiver
    receiver_role = Column(String(20), nullable=False)
    # institute / employee / student

    receiver_id = Column(Integer, nullable=True)
    # NULL = broadcast

    category = Column(String(50), nullable=True)
    # teacher / driver / accountant

    institute_id = Column(Integer, nullable=False)

    title = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ RELATIONSHIP
    attachments = relationship(
        "MessageAttachment",
        back_populates="message",
        cascade="all, delete-orphan"
    )


class MessageAttachment(Base):
    __tablename__ = "message_attachments"

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

    # ✅ BACK RELATION
    message = relationship("Message", back_populates="attachments")
