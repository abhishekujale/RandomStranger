# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URI")

# The "engine" is the actual connection to your DB
engine = create_async_engine(DATABASE_URL, echo=True)

# A "session" is like a conversation with the DB — you open one per request
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# All your models will inherit from this Base
class Base(DeclarativeBase):
    pass

# This is a "dependency" — FastAPI will call it automatically per request
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session