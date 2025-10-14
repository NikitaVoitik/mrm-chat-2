from fastapi import APIRouter
from app.api.v1 import messages

api_router = APIRouter()

api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
