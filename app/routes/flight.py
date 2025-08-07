from fastapi import APIRouter, Depends
from app.services.flight_service import (
    list_flights,
    create_flight,
    get_flight,
    update_flight,
    delete_flight
)
from app.services.auth_service import verify_token

router = APIRouter()


@router.get("/flight")
async def get_all_flights():
    return await list_flights()


@router.post("/flight")
async def create_new_flight(payload: dict, current_user=Depends(verify_token)):
    # 僅限管理員可建立航班
    if not current_user.get("isAdmin", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="只有管理員可以新增航班")
    return await create_flight(payload)


@router.get("/flight/{flight_id}")
async def get_flight_by_id(flight_id: str):
    return await get_flight(flight_id)


@router.put("/flight/{flight_id}")
async def update_flight_by_id(flight_id: str, payload: dict, current_user=Depends(verify_token)):
    if not current_user.get("isAdmin", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="只有管理員可以更新航班")
    return await update_flight(flight_id, payload)


@router.delete("/flight/{flight_id}")
async def delete_flight_by_id(flight_id: str, current_user=Depends(verify_token)):
    if not current_user.get("isAdmin", False):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="只有管理員可以刪除航班")
    return await delete_flight(flight_id)
