from fastapi import HTTPException, Request, Response
from app.models.user import User
from app.utils.email_service import send_reset_email
from app.utils.response import success
from app.utils.error_handler import raise_error
from passlib.hash import bcrypt
from datetime import datetime, timezone, timedelta
import jwt
import os
import secrets

JWT_SECRET = os.getenv("JWT", "w444")
JWT_EXPIRE_HOURS = 168  # 對應 Node 7d = 168hr

# 發 token 並設 cookie
def set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="JWT_token",
        value=token,
        httponly=False,
        secure=os.getenv("NODE_ENV") == "production",
        samesite="strict" if os.getenv("NODE_ENV") == "production" else "lax",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )

def generate_token(user):
    payload = {
        "id": str(user.id),
        "isAdmin": getattr(user, "isAdmin", False),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def register(data: dict):
    username_exists = await User.find_one(User.username == data["username"])
    email_exists = await User.find_one(User.email == data["email"])
    if username_exists or email_exists:
        raise_error(400, "此帳號或信箱已被註冊")
    
    hashed_pwd = bcrypt.hash(data["password"])
    user = User(username=data["username"], email=data["email"], password=hashed_pwd)
    await user.insert()
    return success(user.model_dump(by_alias=True, exclude_none=True))


async def login(data: dict, response: Response):
    user = await User.find_one({
        "$or": [
            {"username": data["account"]},
            {"email": data["account"]}
        ]
    })

    if not user:
        raise_error(404, "沒有此使用者")
    
    if not bcrypt.verify(data["password"], user.password):
        raise_error(404, "輸入密碼錯誤")
    
    token = generate_token(user)
    set_token_cookie(response, token)

    user_data = user.model_dump(by_alias=True, exclude_none=True)
    user_data.pop("password", None)
    return success({"userDetails": user_data})


async def forgot_password(data: dict):
    user = await User.find_one(User.email == data["email"])
    if not user:
        raise_error(404, "沒有此信箱的使用者")
    
    token = secrets.token_hex(16)
    user.resetPasswordToken = token
    user.resetPasswordExpires = datetime.now(timezone.utc) + timedelta(hours=1)
    await user.save()

    await send_reset_email(user.email, token)
    return success(message="重置密碼郵件已發送")


async def reset_password(token: str, new_password: str):
    user = await User.find_one({
        "resetPasswordToken": token,
        "resetPasswordExpires": {"$gt": datetime.now(timezone.utc)}
    })

    if not user:
        raise_error(404, "重置令牌無效或已過期")

    user.password = bcrypt.hash(new_password)
    user.resetPasswordToken = None
    user.resetPasswordExpires = None
    await user.save()
    return success(message="密碼重置成功")


def me(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise_error(401, "尚未登入")
    return success(user)


def logout(response: Response):
    response.delete_cookie("JWT_token", path="/")
    return success(message="已登出")


def verify_token(request: Request):
    token = request.cookies.get("JWT_token")
    if not token:
        raise_error(401, "請先登入")
    
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        request.state.user = decoded
    except jwt.ExpiredSignatureError:
        raise_error(403, "登入已過期，請重新登入")
    except jwt.PyJWTError:
        raise_error(403, "無效的 Token")