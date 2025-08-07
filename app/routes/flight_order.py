from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.db import get_db
from app.services.flight_service import (
    create_flight_order,
    get_user_orders,
    get_order_detail,
    cancel_order
)
from app.services.auth_service import verify_token

router = APIRouter()


@router.post("/flight/order")
async def create_order(payload: dict, db: AsyncIOMotorDatabase = Depends(get_db), current_user=Depends(verify_token)):
    return await create_flight_order(payload, current_user["_id"])


@router.get("/flight/orders/user")
async def get_user_order_list(db: AsyncIOMotorDatabase = Depends(get_db), current_user=Depends(verify_token)):
    return await get_user_orders(current_user["_id"])


@router.get("/flight/orders/{order_id}")
async def get_flight_order_detail(order_id: str):
    return await get_order_detail(order_id)


@router.post("/flight/orders/{order_id}/cancel")
async def cancel_flight_order(order_id: str, current_user=Depends(verify_token)):
    return await cancel_order(order_id, current_user["_id"])
