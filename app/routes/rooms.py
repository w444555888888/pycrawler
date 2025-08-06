# rooms.py
from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from app.models.room import RoomBase
from app.db import db

router = APIRouter()

@router.post("/")
async def create_room(room: RoomBase):
    room_dict = room.dict()
    result = await db.rooms.insert_one(room_dict)
    room_dict["_id"] = str(result.inserted_id)
    return room_dict

@router.put("/{room_id}")
async def update_room(room_id: str, body: dict = Body(...)):
    result = await db.rooms.find_one_and_update(
        {"_id": ObjectId(room_id)},
        {"$set": body},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="找不到此房型或更新失敗")
    result["_id"] = str(result["_id"])
    return result

@router.delete("/{room_id}")
async def delete_room(room_id: str):
    result = await db.rooms.delete_one({"_id": ObjectId(room_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="找不到此房型")
    return {"message": "刪除成功"}

@router.get("/")
async def get_all_rooms():
    rooms = await db.rooms.find({}).to_list(length=1000)
    for room in rooms:
        room["_id"] = str(room["_id"])
    return rooms

@router.get("/findHotel/{hotel_id}")
async def get_hotel_rooms(hotel_id: str):
    try:
        hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
        if not hotel:
            raise HTTPException(status_code=404, detail="找不到該飯店")
        rooms = await db.rooms.find({"hotelId": ObjectId(hotel_id)}).to_list(length=100)
        for room in rooms:
            room["_id"] = str(room["_id"])
        return rooms
    except:
        raise HTTPException(status_code=500, detail="找尋房型時發生錯誤")