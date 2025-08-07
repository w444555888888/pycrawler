from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.schemas.user import UserOut
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, current_user = Depends(get_current_user)):
    if user_id != current_user["id"] and not current_user["isAdmin"]:
        raise HTTPException(status_code=403, detail="只能查自己的資料")
    user = await User.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="找不到用戶")
    user["_id"] = str(user["_id"])
    del user["password"]
    return user

@router.get("/", response_model=list[UserOut])
async def get_all_users(current_user = Depends(get_current_user)):
    if not current_user["isAdmin"]:
        raise HTTPException(status_code=403, detail="只有管理員可以查看所有用戶")
    users = await User.find().to_list(length=1000)
    for u in users:
        u["_id"] = str(u["_id"])
        del u["password"]
    return users