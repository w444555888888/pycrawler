from fastapi import HTTPException
from datetime import datetime
from app.models.order import Order
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.user import User
from app.utils.response import success
from app.utils.error_handler import raise_error
from typing import Dict, Optional


# 取得全部訂單
async def list_orders():
    orders = await Order.find_all().to_list()
    return success(orders)


# 根據 ID 取得單一訂單（含 hotel、room）
async def get_order(order_id: str):
    order = await Order.get(order_id, fetch_links=True)
    if not order:
        raise_error(404, '訂單找不到')
    return success(order)


# 建立訂單（含檢查飯店、房型、是否重複）
async def create_order(data: Dict, user: User):
    hotel_id = data.get("hotelId")
    room_id = data.get("roomId")
    total_price = data.get("totalPrice")

    if not hotel_id or not room_id or not total_price:
        raise_error(400, '缺少必填字段')

    # 檢查是否已有相同尚未完成的訂單
    existing = await Order.find({
        "hotelId": hotel_id,
        "roomId": room_id,
        "userId": str(user.id),
        "status": {"$ne": "completed"}
    }).to_list()

    if existing:
        raise_error(400, "此房型尚有未完成訂單")

    hotel = await Hotel.get(hotel_id)
    if not hotel:
        raise_error(404, "飯店找不到")

    room = await Room.get(room_id)
    if not room:
        raise_error(404, "房型找不到")

    service_fee = total_price * 0.10
    total_price_with_fee = total_price + service_fee

    order = Order(
        **data,
        userId=str(user.id),
        totalPrice=total_price_with_fee,
        createdAt=datetime.utcnow()
    )
    await order.insert()
    return success(order, code=201)


# 更新訂單（by id）
async def update_order(order_id: str, data: Dict):
    order = await Order.get(order_id)
    if not order:
        raise_error(404, '訂單找不到')

    for k, v in data.items():
        setattr(order, k, v)
    await order.save()
    return success(order)


# 刪除訂單（by id）
async def delete_order(order_id: str):
    order = await Order.get(order_id)
    if not order:
        raise_error(404, '訂單找不到')

    await order.delete()
    return success(message="訂單刪除成功")
