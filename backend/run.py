# run.py
import uvicorn
from app.main import socket_app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-restarts when you change code
    )