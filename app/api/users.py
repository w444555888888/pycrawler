# app/api/rooms.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "這是 User API"}
