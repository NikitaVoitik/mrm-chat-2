from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message model."""
    text: str = Field(..., min_length=1, max_length=1000, description="Message text")


class MessageCreate(MessageBase):
    """Model for creating a message."""
    pass


class Message(MessageBase):
    """Message model with all fields."""
    id: int = Field(..., description="Message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")

    class Config:
        from_attributes = True
