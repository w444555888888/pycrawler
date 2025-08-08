from fastapi import APIRouter, Depends
from app.services.flight_service import (
    list_flights,
    create_flight,
    get_flight,
    update_flight,
    delete_flight,
    create_flight_order,
    get_user_orders,
    get_order_detail,
    cancel_order,
)
from app.services.auth_service import verify_token

router = APIRouter(tags=["flights"])

# ----------- Flight 相關 -----------
@router.get("/")
async def route_get_flight_list():
    return await list_flights()

@router.post("/")
async def route_create_new_flight(payload: dict):
    return await create_flight(payload)

@router.get("/{flight_id}")
async def route_get_flight_by_id(flight_id: str):
    return await get_flight(flight_id)

@router.put("/{flight_id}")
async def route_update_flight_by_id(flight_id: str, payload: dict):
    return await update_flight(flight_id, payload)

@router.delete("/{flight_id}")
async def route_delete_flight_by_id(flight_id: str):
    return await delete_flight(flight_id)

# ----------- Flight Order 訂單相關 -----------
@router.post("/order")
async def route_create_order(payload: dict, current_user=Depends(verify_token)):
    return await create_flight_order(payload, current_user.id)

@router.get("/orders/user")
async def route_get_orders_by_user(current_user=Depends(verify_token)):
    return await get_user_orders(current_user.id)

@router.get("/orders/{order_id}")
async def route_get_order_detail_by_id(order_id: str):
    return await get_order_detail(order_id)

@router.post("/orders/{order_id}/cancel")
async def route_cancel_order_by_id(order_id: str, current_user=Depends(verify_token)):
    return await cancel_order(order_id, current_user.id)
