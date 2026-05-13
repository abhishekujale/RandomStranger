# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ─── Message schemas ──────────────────────────────────────────────

class MessageOut(BaseModel):
    """Shape of a message we send back to the frontend."""
    id: str
    chat_id: str
    sender_id: str
    content: str
    is_image: bool
    original_lang: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}  # lets Pydantic read SQLAlchemy objects


# ─── Chat schemas ─────────────────────────────────────────────────

class ChatCreate(BaseModel):
    """Data the frontend sends when saving a new chat to the DB."""
    room_id: str
    user1_id: str
    user2_id: str
    is_video: bool = False

class ChatOut(BaseModel):
    """Shape of a chat we send back."""
    id: str
    room_id: str
    user1_id: str
    user2_id: str
    is_video: bool
    translations_enabled: bool
    status: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}

class ChatEnd(BaseModel):
    """Body for ending a chat."""
    room_id: str


# ─── Report schemas ───────────────────────────────────────────────

class ReportCreate(BaseModel):
    """Data sent when a user reports someone."""
    chat_id: str
    reporter_id: str
    reason: str   # e.g. "spam", "harassment", "inappropriate content"

class ReportOut(BaseModel):
    id: str
    chat_id: str
    reporter_id: str
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── User schemas ─────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Creating/registering an anonymous user with interests."""
    interests: list[str] = []

class UserOut(BaseModel):
    id: str
    socket_id: Optional[str] = None
    interests: list[str]
    is_online: bool
    created_at: datetime

    model_config = {"from_attributes": True}