from typing import Optional
from fastapi import HTTPException
from app.models.room import Room
from app.models.hotel import Hotel
from app.utils.response import success


async def create_room(data):
    hotel = await Hotel.get(data.get("hotel_id"))
    if not hotel:
        raise HTTPException(status_code=400, detail="Hotel not found")

    room = Room(**data)
    await room.insert()
    return success(room)


async def update_room(room_id: str, data):
    room = await Room.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    for k, v in data.items():
        setattr(room, k, v)
    room.update_timestamp()
    await room.save()
    return success(room)


async def delete_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    await room.delete()
    return success()


async def list_rooms():
    rooms = await Room.find_all().to_list()
    return success(rooms)


async def get_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return success(room)


async def list_rooms_by_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    rooms = await Room.find(Room.hotel_id == hotel_id).to_list()
    return success(rooms)


async def calculate_room_price(room_id: str, start_date: str, end_date: str):
    room = await Room.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    total_price = room.calculate_total_price(start_date, end_date)
    return success({"totalPrice": total_price})
