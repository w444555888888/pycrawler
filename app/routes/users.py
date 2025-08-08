from fastapi import APIRouter, Depends
from app.services.user_service import (
    get_all_users,
    get_user,
    update_user,
    delete_user
)
from app.services.auth_service import verify_token
from app.models.user import User

router = APIRouter(tags=["users"])

#全部用戶資料
@router.get("/")
async def route_get_all_users(current_user: User = Depends(verify_token)):
    return await get_all_users(current_user)

#單一用戶資料
@router.get("/{user_id}")
async def route_get_user(user_id: str, current_user: User = Depends(verify_token)):
    return await get_user(user_id, current_user)

#更新用戶資料
@router.put("/{user_id}")
async def route_update_user(user_id: str, data: dict, current_user: User = Depends(verify_token)):
    return await update_user(user_id, data, current_user)

#刪除用戶資料
@router.delete("/{user_id}")
async def route_delete_user(user_id: str, current_user: User = Depends(verify_token)):
    return await delete_user(user_id, current_user)
