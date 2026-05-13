# run.py
import uvicorn
from app.main import socket_app
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("DATABASE_URI"))
if __name__ == "__main__":
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-restarts when you change code
    )