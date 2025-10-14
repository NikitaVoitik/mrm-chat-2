from datetime import datetime
from typing import List
from fastapi import APIRouter
from app.models.message import Message, MessageCreate

router = APIRouter()


@router.get("/", response_model=List[Message])
async def get_messages():
    """Get all messages."""
    return [
        Message(id=1, text="Hello, World!", timestamp=datetime(2024, 1, 1, 0, 0, 0)),
        Message(id=2, text="Welcome to MRM Chat", timestamp=datetime(2024, 1, 1, 0, 1, 0))
    ]


@router.post("/", response_model=Message)
async def create_message(message: MessageCreate):
    """Create a new message."""
    return Message(
        id=3,
        text=message.text,
        timestamp=datetime.utcnow()
    )
