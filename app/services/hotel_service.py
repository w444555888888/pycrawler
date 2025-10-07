from app.utils.response import success
from app.models.hotel import Hotel
from app.models.room import Room
from app.utils.error_handler import raise_error
from typing import Optional
from beanie import PydanticObjectId, Link
from pydantic import BaseModel
from bson import DBRef, ObjectId
from datetime import datetime, timezone



# 獲取所有飯店資料（不帶任何過濾條件）
async def get_all_hotels():
    hotels = await Hotel.find_all().to_list()
    return success(data=hotels)


# 模糊搜尋飯店名稱(搜索框)    
async def get_hotel_name_suggestions(name: str):
    if not name.strip():
        raise_error(400, "請輸入搜尋名稱")

    hotels = await Hotel.find({
        "name": {"$regex": name, "$options": "i"}
    }, projection={"_id": 1, "name": 1}).limit(10).to_list()

    return success(data=hotels)

# 查詢熱門飯店
async def get_popular_hotels():
    hotels = await Hotel.find({"popularHotel": True}).to_list()
    return success(data=hotels)   


# 遞迴清理函式 — 取代 jsonable_encoder，防止 DBRef 錯誤
def clean_for_json(obj):
    """安全遞迴轉換所有資料，避免 DBRef / ObjectId / BaseModel 造成 JSON 錯誤"""
    if isinstance(obj, DBRef):
        # Node.js virtual populate 結構
        return str(obj.id)
    if isinstance(obj, (ObjectId, PydanticObjectId)):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return clean_for_json(obj.model_dump(by_alias=True, exclude_none=True))
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    return obj




# 搜尋飯店資料 (依篩選條件)
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
    safe_data = []

    # 條件設定
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if hotel_id:
        query["_id"] = ObjectId(hotel_id)
    if popular:
        query["popularHotel"] = True

    print("🟡 hotel_id 傳入參數 =", hotel_id)
    print("🟡 query =", query)
    try:
        # 單查 hotel，不用房型與價格
        is_single_query = (
            hotel_id and not name and not min_price and not max_price and not start_date and not end_date
        )
        if is_single_query:
            hotel = await Hotel.get(ObjectId(hotel_id))
            if not hotel:
                raise_error(404, "找不到此飯店")
            return success(data=hotel)
        
        # 多查 hotel，需帶房型與價格
        hotels = await Hotel.find(query).to_list()
        if not hotels:
            raise_error(404, "找不到符合條件的飯店")

        updated_hotels = []
        for hotel in hotels:
            current_hotel_id = ObjectId(str(hotel.id))

            # 若 query 中有 hotel_id，這裡自然只查該飯店的房型
            rooms = await Room.find(Room.hotel_id == current_hotel_id).to_list()

            if not rooms:
                print(f"此飯店無房型: {hotel.name}")
                continue

            cheapest_price = None
            available_rooms = []

            for idx, room in enumerate(rooms):
                print(f"➡️ 房型[{idx}]：{room.title}")
                print(f"   🧩 start_date={start_date}, end_date={end_date}")

                price = room.calculate_total_price(start_date, end_date)
                print(f"   🧮 計算結果：{price}")

                if not price or price <= 0:
                    continue

                if cheapest_price is None or price < cheapest_price:
                    cheapest_price = price

                room_data = room.model_dump(by_alias=True, exclude_none=True)
                room_data["hotelId"] = str(
                    getattr(room, "hotelId", getattr(room, "hotel_id", current_hotel_id))
                )
                room_data["roomTotalPrice"] = price
                available_rooms.append(room_data)

            # --- 更新最低價 ---
            if cheapest_price is not None and (hotel.cheapest_price != cheapest_price):
                try:
                    hotel.cheapest_price = cheapest_price
                    await hotel.save()
                except Exception as e:
                    print(f"⚠️ 更新 hotel.cheapest_price 失敗: {e}")

            hotel_data = hotel.model_dump(by_alias=True, exclude_none=True, exclude={"rooms"})
            hotel_data["availableRooms"] = available_rooms
            hotel_data["cheapestPrice"] = cheapest_price or hotel.cheapest_price or 0
            updated_hotels.append(hotel_data)

        if min_price is not None or max_price is not None:
            updated_hotels = [
                h for h in updated_hotels
                if h.get("cheapestPrice") is not None
                and (min_price is None or h["cheapestPrice"] >= min_price)
                and (max_price is None or h["cheapestPrice"] <= max_price)
            ]

        safe_data = clean_for_json(updated_hotels)

    except Exception as e:
        import traceback
        print(f"例外型別: {type(e)}")
        print(f"例外內容: {e}")
        print(traceback.format_exc())
        safe_data = []

    return success(data=safe_data, exclude_fields=["rooms"])





# 取得單一飯店
async def get_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")
    return success(data=hotel)


# 新增飯店
async def create_hotel(data):
    hotel = Hotel(**data)
    await hotel.insert()
    return success(data=hotel)

# 更新飯店
async def update_hotel(hotel_id: str, data: dict):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")

    update_data = Hotel.model_validate(data).model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(hotel, k, v)

    await hotel.save()
    return success(data=hotel)


# 刪除飯店
async def delete_hotel(hotel_id: str):
    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "找不到該飯店")
    await hotel.delete()
    return success(message="刪除成功")
