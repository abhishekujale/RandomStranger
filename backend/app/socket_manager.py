# app/socket_manager.py
import socketio
from app.matching import add_to_queue, remove_from_queue, find_match, generate_room_id
from app.database import AsyncSessionLocal
from app.models import Chat, Message
from sqlalchemy import select
import uuid


# Create the Socket.io server
# cors_allowed_origins should be your Next.js URL in production
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

@sio.event
async def connect(sid, environ):
    """Called when a user connects."""
    print(f"User connected: {sid}")

@sio.event
async def disconnect(sid):
    """Called when a user disconnects."""
    print(f"User disconnected: {sid}")
    remove_from_queue(sid)
    # Notify their partner if they were in a chat
    await sio.emit("partner-disconnected", room=sid)

@sio.event
async def join_queue(sid, data):
    """
    User wants to find a match.
    data = { "interests": ["gaming", "music"], "isVideo": true }
    """
    interests = data.get("interests", [])
    is_video = data.get("isVideo", False)

    match = find_match(sid, interests, is_video)

    if match:
        # Found a match! Create a room and notify both users
        room_id = generate_room_id()
        await sio.enter_room(sid, room_id)
        await sio.enter_room(match["socket_id"], room_id)

        await sio.emit("matched", {"roomId": room_id, "partnerId": match["socket_id"]}, to=sid)
        await sio.emit("matched", {"roomId": room_id, "partnerId": sid}, to=match["socket_id"])
    else:
        # No match yet, add to queue
        add_to_queue(sid, interests, is_video)
        await sio.emit("waiting", {"message": "Looking for someone..."}, to=sid)

@sio.event
async def typing(sid, data):
    """Broadcast typing indicator to partner."""
    room_id = data.get("roomId")
    await sio.emit("partner-typing", {}, room=room_id, skip_sid=sid)

@sio.event
async def skip(sid, data):
    """User clicked Next — disconnect from current room, re-queue."""
    room_id = data.get("roomId")
    if room_id:
        await sio.emit("partner-disconnected", {}, room=room_id, skip_sid=sid)
        await sio.leave_room(sid, room_id)

# WebRTC signaling — just relay these between the two peers
@sio.event
async def webrtc_offer(sid, data):
    room_id = data.get("roomId")
    await sio.emit("webrtc-offer", data, room=room_id, skip_sid=sid)

@sio.event
async def webrtc_answer(sid, data):
    room_id = data.get("roomId")
    await sio.emit("webrtc-answer", data, room=room_id, skip_sid=sid)

@sio.event
async def ice_candidate(sid, data):
    room_id = data.get("roomId")
    await sio.emit("ice-candidate", data, room=room_id, skip_sid=sid)


@sio.event
async def send_message(sid, data):
    """
    1. Emit to partner in real time (fast)
    2. Save to database (for history)
    """
    room_id = data.get("roomId")
    content = data.get("content", "")

    # Step 1 — real-time delivery (instant)
    await sio.emit("receive-message", {
        "senderId": sid,
        "content": content,
    }, room=room_id, skip_sid=sid)

    # Step 2 — persist to DB (slightly slower, but that's OK)
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Chat).where(Chat.room_id == room_id))
        chat = result.scalar_one_or_none()
        if chat:
            message = Message(
                id=str(uuid.uuid4()),
                chat_id=chat.id,
                sender_id=sid,
                content=content,
            )
            db.add(message)
            await db.commit()