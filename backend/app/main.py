# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.socket_manager import sio
from app.routes import chat, report
import socketio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all DB tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up on shutdown
    await engine.dispose()

app = FastAPI(title="RandomStranger API", lifespan=lifespan)

# Mount Socket.io alongside FastAPI
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Include REST route groups
app.include_router(chat.router, prefix="/api/chats", tags=["chats"])
app.include_router(report.router, prefix="/api/reports", tags=["reports"])

@app.get("/health")
async def health():
    return {"status": "ok"}