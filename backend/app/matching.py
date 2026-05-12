# app/matching.py
import uuid
from typing import Optional

# This lives in memory (a Python dict) — fast but resets on server restart
# In production you'd use Redis instead
waiting_queue: list[dict] = []

def add_to_queue(socket_id: str, interests: list[str], is_video: bool) -> None:
    """Add a user to the waiting queue."""
    waiting_queue.append({
        "socket_id": socket_id,
        "interests": interests,
        "is_video": is_video,
    })

def remove_from_queue(socket_id: str) -> None:
    """Remove a user from the queue (when they disconnect or skip)."""
    global waiting_queue
    waiting_queue[:] = [u for u in waiting_queue if u["socket_id"] != socket_id]

def find_match(socket_id: str, interests: list[str], is_video: bool) -> Optional[dict]:
    """
    Try to find a match. Strategy:
    1. First try users with overlapping interests
    2. Fall back to anyone available
    """
    candidates = [u for u in waiting_queue if u["socket_id"] != socket_id]

    # Try interest match first
    for candidate in candidates:
        shared = set(interests) & set(candidate["interests"])
        if shared:
            remove_from_queue(candidate["socket_id"])
            return candidate

    # Fall back to any available user
    if candidates:
        match = candidates[0]
        remove_from_queue(match["socket_id"])
        return match

    return None  # Nobody available, stay in queue

def generate_room_id() -> str:
    return str(uuid.uuid4())