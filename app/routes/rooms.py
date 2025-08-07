# app/routes/rooms.py
from fastapi import APIRouter
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/by-hotel/{hotel_id}")
async def list_by_hotel(hotel_id: str):
    return await room_service.list_by_hotel(hotel_id)

@router.post("/add")
async def add_room(data: dict):
    return await room_service.add_room(data)

@router.put("/edit/{id}")
async def edit_room(id: str, data: dict):
    return await room_service.edit_room(id, data)

@router.delete("/delete/{id}")
async def delete_room(id: str):
    return await room_service.delete_room(id)