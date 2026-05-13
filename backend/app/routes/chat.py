# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
import uuid

from app.database import get_db
from app.models import Chat, Message, User
from app.schemas import ChatCreate, ChatOut, ChatEnd, MessageOut

router = APIRouter()


@router.post("/", response_model=ChatOut)
async def create_chat(data: ChatCreate, db: AsyncSession = Depends(get_db)):
    """
    Called when two users are matched — saves the chat room to the DB.
    The frontend (or socket server) calls this right after 'matched' event.
    """
    # Make sure we're not creating a duplicate room
    existing = await db.execute(select(Chat).where(Chat.room_id == data.room_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Room already exists")

    chat = Chat(
        id=str(uuid.uuid4()),
        room_id=data.room_id,
        user1_id=data.user1_id,
        user2_id=data.user2_id,
        is_video=data.is_video,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


@router.get("/{room_id}", response_model=ChatOut)
async def get_chat(room_id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch a chat and all its messages by room ID.
    Useful for replaying a conversation or showing history.
    """
    result = await db.execute(
        select(Chat).where(Chat.room_id == room_id)
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat


@router.post("/{room_id}/end", response_model=ChatOut)
async def end_chat(room_id: str, db: AsyncSession = Depends(get_db)):
    """
    Mark a chat as ended when a user disconnects or skips.
    Sets status = 'ended' and records the end time.
    """
    result = await db.execute(select(Chat).where(Chat.room_id == room_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.status = "ended"
    chat.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(chat)
    return chat


@router.post("/{room_id}/messages", response_model=MessageOut)
async def save_message(
    room_id: str,
    sender_id: str,
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Save a text message to the database.
    Note: messages are sent via Socket.io in real time —
    this endpoint is for persistence (storing the history).
    """
    result = await db.execute(select(Chat).where(Chat.room_id == room_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    message = Message(
        id=str(uuid.uuid4()),
        chat_id=chat.id,
        sender_id=sender_id,
        content=content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/{room_id}/messages", response_model=list[MessageOut])
async def get_messages(room_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages in a chat room."""
    result = await db.execute(select(Chat).where(Chat.room_id == room_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    msgs = await db.execute(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.created_at)
    )
    return msgs.scalars().all()