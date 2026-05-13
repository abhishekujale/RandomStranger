# app/models.py
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from app.database import Base
import uuid

def gen_id():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    socket_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chats_as_user1: Mapped[list["Chat"]] = relationship("Chat", foreign_keys="Chat.user1_id", back_populates="user1")
    chats_as_user2: Mapped[list["Chat"]] = relationship("Chat", foreign_keys="Chat.user2_id", back_populates="user2")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    room_id: Mapped[str] = mapped_column(String, unique=True)
    user1_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user2_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    is_video: Mapped[bool] = mapped_column(Boolean, default=False)
    translations_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id], back_populates="chats_as_user1")
    user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id], back_populates="chats_as_user2")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    chat_id: Mapped[str] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    is_image: Mapped[bool] = mapped_column(Boolean, default=False)
    original_lang: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    chat_id: Mapped[str] = mapped_column(ForeignKey("chats.id"))
    reporter_id: Mapped[str]
    reason: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)