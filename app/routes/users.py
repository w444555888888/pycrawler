# app/routes/users.py
from fastapi import APIRouter
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/info/{id}")
async def user_info(id: str):
    return await user_service.user_info(id)

@router.put("/update/{id}")
async def update_user(id: str, data: dict):
    return await user_service.update_user(id, data)

@router.get("/orders/{id}")
async def user_orders(id: str):
    return await user_service.user_orders(id)