from fastapi import APIRouter, Depends
from app.services.auth_service import verify_token
from app.services.order_service import (
    list_orders,
    get_order,
    create_order,
    update_order,
    delete_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])

#全部訂單
@router.get("/")
async def route_list_orders():
    return await list_orders()

#id查找
@router.get("/{order_id}")
async def route_get_order(order_id: str):
    return await get_order(order_id)

#新訂單
@router.post("/")
async def route_create_order(data: dict, current_user=Depends(verify_token)):
    return await create_order(data, current_user)

#id更新訂單
@router.put("/{order_id}")
async def route_update_order(order_id: str, data: dict):
    return await update_order(order_id, data)

#id刪除訂單
@router.delete("/{order_id}")
async def route_delete_order(order_id: str):
    return await delete_order(order_id)
