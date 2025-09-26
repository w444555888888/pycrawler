from fastapi import HTTPException
from app.models.hotel import Hotel
from app.utils.response import success
from app.utils.error_handler import raise_error
from typing import Optional
from datetime import datetime, timezone


def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

# 模糊搜尋飯店名稱(搜索框)    
async def get_hotel_name_suggestions(name: str):
    if not name.strip():
        raise_error(400, "請輸入搜尋名稱")

    hotels = await Hotel.find({
        "name": {"$regex": name, "$options": "i"}
    }, projection={"_id": 1, "name": 1}).limit(10).to_list()

    return success(hotels)

# 查詢熱門飯店
async def get_popular_hotels():
    hotels = await Hotel.find({"popularHotel": True}).to_list()
    return success(hotels)    

# 搜尋飯店資料(根據篩選條件)
async def list_hotels(
    name: Optional[str] = None,
    hotel_id: Optional[str] = None,
    popular: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    query = {}

    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if hotel_id:
        query["_id"] = hotel_id
    if popular:
        query["popularHotel"] = True

    # 等同於 Node.js 的 populate('rooms')
    hotels = await Hotel.find(query).fetch_links().to_list()
    if not hotels:
        raise_error(404, "找不到符合條件的飯店")

    parsed_start = parse_date(start_date) if start_date else None
    parsed_end = parse_date(end_date) if end_date else None

    updated_hotels = []
    for hotel in hotels:
        rooms = hotel.rooms or []
        cheapest_price = None
        total_price = 0
        available_rooms = []

        for room in rooms:
            price = room.calculate_total_price(start_date, end_date)
            total_price += price
            if cheapest_price is None or price < cheapest_price:
                cheapest_price = price

            room_data = room.model_dump(by_alias=True, exclude_none=True)
            room_data["roomTotalPrice"] = price
            available_rooms.append(room_data)

        hotel_data = hotel.model_dump(by_alias=True, exclude_none=True)
        hotel_data["availableRooms"] = available_rooms
        hotel_data["cheapestPrice"] = cheapest_price
        hotel_data["totalPrice"] = total_price
        updated_hotels.append(hotel_data)

    if min_price is not None or max_price is not None:
        filtered_hotels = []
        for hotel in updated_hotels:
            price = hotel.get("cheapestPrice")
            if price is None:
                continue
            if (min_price is not None and price < min_price) or (max_price is not None and price > max_price):
                continue
            filtered_hotels.append(hotel)
        updated_hotels = filtered_hotels

    return success(updated_hotels)


# 獲取所有飯店資料（不帶任何過濾條件）
async def get_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")
    return success(hotel)


# 新增飯店
async def create_hotel(data):
    hotel = Hotel(**data)
    await hotel.insert()
    return success(hotel)

# 更新飯店
async def update_hotel(hotel_id: str, data):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")
    for k, v in data.items():
        setattr(hotel, k, v)
    await hotel.save()
    return success(hotel)

# 刪除飯店
async def delete_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")
    await hotel.delete()
    return success()
