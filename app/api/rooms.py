# app/api/rooms.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_rooms():
    return {"message": "這是 Room API"}
