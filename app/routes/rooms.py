from fastapi import APIRouter
from app.services.room_service import (
    list_rooms,             
    get_room,               
    list_rooms_by_hotel,  
    create_room,           
    update_room,           
    delete_room,           
    calculate_room_price   
)

router = APIRouter(tags=["rooms"])

# 取得所有房型列表
@router.get("/")
async def route_list_rooms():
    return await list_rooms()

# 取得特定房型的詳細資訊
@router.get("/{room_id}")
async def route_get_room(room_id: str):
    return await get_room(room_id)

# 根據飯店 ID 獲取該飯店下所有房型
@router.get("/findHotel/{hotel_id}")
async def route_list_rooms_by_hotel(hotel_id: str):
    return await list_rooms_by_hotel(hotel_id)

# 新增一筆房型資料
@router.post("/add")
async def route_create_room(data: dict):
    return await create_room(data)

# 編輯特定房型資料（根據 room_id）
@router.put("/edit/{room_id}")
async def route_update_room(room_id: str, data: dict):
    return await update_room(room_id, data)

# 刪除特定房型資料（根據 room_id(node版本沒有)
@router.delete("/delete/{room_id}")
async def route_delete_room(room_id: str):
    return await delete_room(room_id)

# 計算房型在指定日期區間的總價格(node版本沒有)
@router.get("/calculate-price/{room_id}")
async def route_calculate_room_price(room_id: str, start_date: str, end_date: str):
    return await calculate_room_price(room_id, start_date, end_date)
