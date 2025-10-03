from typing import Optional
from beanie import PydanticObjectId
from app.models.room import Room
from app.models.hotel import Hotel
from app.utils.response import success
from app.utils.error_handler import raise_error


# 建立房型
async def create_room(data):
    hotel = await Hotel.get(data.get("hotelId"))
    if not hotel:
        raise_error(400, "找不到對應的飯店")

    room = Room(**data)
    await room.insert()
    return success(data=room)


# 更新房型
async def update_room(room_id: str, data: dict):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")
    # model_validate: 驗證並轉換前端傳入的 dict 成為 Room 模型
    #   - 自動處理 alias -> 欄位名 (例如 roomType -> room_type)
    #   - 自動做型別轉換 (例如 "5" -> int 5)
    #   - 如果資料不合法，會丟出 ValidationError
    #
    # model_dump: 把模型轉回 dict
    #   - exclude_unset=True: 只保留有提供的欄位 (適合做部分更新)
    #   - by_alias=True 時會用 alias 名稱輸出 (例如 roomType 而不是 room_type)
    update_data = Room.model_validate(data).model_dump(exclude_unset=True)
    for k, v in update_data.items():
        # setattr(room, "room_type", "Twin Room")  等於 room.room_type = "Twin Room"
        # setattr(room, "max_people", 5)           等於 room.max_people = 5
        setattr(room, k, v)

    room.update_timestamp()
    await room.save()

    return success(data=room)


# 刪除房型
async def delete_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")

    await room.delete()
    return success(message="刪除成功")


# 取得全部房型
async def list_rooms():
    rooms = await Room.find_all().to_list()
    success(data=rooms)


# 根據 ID 取得房型
async def get_room(room_id: str):
    room = await Room.get(room_id)
    if not room:
        raise_error(404, "找不到該房型")
    return success(data=room)


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
    return success(data={"totalPrice": total_price})
