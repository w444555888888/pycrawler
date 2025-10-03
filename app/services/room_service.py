from typing import Optional
from beanie import PydanticObjectId
from app.models.room import Room
from app.models.hotel import Hotel
from app.utils.response import success
from app.utils.error_handler import raise_error


# 建立房型
async def create_room(data):
    hotel = await Hotel.get(data.get("hotel_id"))
    if not hotel:
        raise_error(400, "找不到對應的飯店")

    room = Room(**data)
    await room.insert()
    return success(room)


# 更新房型
async def update_room(room_id: str, data):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")

    for k, v in data.items():
        setattr(room, k, v)
    room.update_timestamp()
    await room.save()
    return success(room)


# 刪除房型
async def delete_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")

    await room.delete()
    return success()


# 取得全部房型
async def list_rooms():
    rooms = await Room.find_all().to_list()
    return success(rooms)


# 根據 ID 取得房型
async def get_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")
    return success(room)


# 根據飯店 ID 取得房型列表
async def list_rooms_by_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")

    rooms = await Room.find(Room.hotel_id == PydanticObjectId(hotel_id)).to_list()
    return success(data=rooms)


# 計算房價
async def calculate_room_price(room_id: str, start_date: str, end_date: str):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")

    total_price = room.calculate_total_price(start_date, end_date)
    return success({"totalPrice": total_price})
