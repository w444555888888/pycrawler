from fastapi import APIRouter, Depends, Query
from app.services.flight_service import (
    list_flights,
    create_flight,
    get_flight,
    update_flight,
    delete_flight,
    get_all_flight_orders,
    create_flight_order,
    get_user_orders,
    get_order_detail,
    cancel_order,
)
from app.services.auth_service import verify_token

router = APIRouter(tags=["flights"])




# ----------- Flight Order 訂單相關 -----------

@router.get("/allOrder")
async def route_get_all_orders():
    return await get_all_flight_orders()

@router.post("/order")
async def route_create_order(payload: dict, current_user=Depends(verify_token)):
    return await create_flight_order(payload, current_user["id"])

@router.get("/orders/user")
async def route_get_orders_by_user(current_user=Depends(verify_token)):
    return await get_user_orders(current_user["id"])

@router.get("/orders/{order_id}")
async def route_get_order_detail_by_id(order_id: str):
    return await get_order_detail(order_id)

@router.post("/orders/{order_id}/cancel")
async def route_cancel_order_by_id(order_id: str, current_user=Depends(verify_token)):
    return await cancel_order(order_id, current_user["id"])




# ----------- Flight 相關 -----------

@router.post("")
async def route_create_new_flight(payload: dict):
    return await create_flight(payload)


@router.put("/{flight_id}")
async def route_update_flight_by_id(flight_id: str, payload: dict):
    return await update_flight(flight_id, payload)


@router.get("")
async def route_get_flight_list(
    departureCity: str | None = Query(None),
    arrivalCity: str | None = Query(None),
    startDate: str | None = Query(None),   # 'YYYY-MM-DD'
    endDate: str | None = Query(None),     # 'YYYY-MM-DD'
):
    # 對齊 Node：把 query 直接傳給 list_flights（snake 參數名對應）
    return await list_flights(
        departure_city=departureCity,
        arrival_city=arrivalCity,
        start_date=startDate,
        end_date=endDate,
    )


@router.get("/{flight_id}")
async def route_get_flight_by_id(flight_id: str):
    return await get_flight(flight_id)

@router.delete("/{flight_id}")
async def route_delete_flight_by_id(flight_id: str):
    return await delete_flight(flight_id)



