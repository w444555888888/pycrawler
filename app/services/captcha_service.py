import random
import os
import jwt
from fastapi import HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.utils.response import success
from app.utils.error_handler import raise_error

JWT_SECRET = os.getenv("JWT", "w444")
JWT_EXPIRE_MINUTES = 5

# 滑塊初始化：產生亂數 x 值並回傳加密的 token
def init():
    x = random.randint(100, 180)  # 和原本 Node 相近的範圍
    payload = {
        "x": x,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return success(200, {
        "token": token,
        "targetX": x
    })

# 滑塊驗證
def check(data: dict):
    token = data.get("token")
    user_x = data.get("userX")

    if not token or user_x is None:
        raise_error(400, "請提供 token 與 x")

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        correct_x = decoded.get("x")
        if correct_x is None:
            raise_error(400, "Token 格式錯誤")

        tolerance = 6
        if abs(int(correct_x) - user_x) < tolerance:
            return success(200, {"passed": True}, "滑塊驗證成功")
        else:
            raise_error(400, "滑塊驗證未通過")

    except ExpiredSignatureError:
        raise_error(401, "驗證失敗：Token 已過期")
    except InvalidTokenError:
        raise_error(401, "驗證失敗：無效的 Token")
    except Exception as e:
        raise_error(403, "Token 驗證失敗", str(e))