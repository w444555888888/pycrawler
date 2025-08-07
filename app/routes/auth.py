from fastapi import APIRouter, HTTPException, Request, Response
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from bson import ObjectId
import os

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    if await User.find_one({"$or": [{"username": user.username}, {"email": user.email}]}):
        raise HTTPException(status_code=400, detail="此帳號或信箱已被註冊")

    hashed = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed
    result = await User.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    del user_dict["password"]
    return user_dict

@router.post("/login")
async def login(user: UserLogin, response: Response):
    user_data = await User.find_one({"$or": [{"username": user.account}, {"email": user.account}]})
    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=404, detail="帳號或密碼錯誤")

    token = create_access_token({"id": str(user_data["_id"]), "isAdmin": user_data.get("isAdmin", False)})
    response.set_cookie(key="JWT_token", value=token, httponly=False, path="/", max_age=7*86400)
    user_data["_id"] = str(user_data["_id"])
    del user_data["password"]
    return {"userDetails": user_data}

@router.get("/me")
async def get_me(request: Request):
    return request.state.user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("JWT_token")
    return {"message": "已登出"}