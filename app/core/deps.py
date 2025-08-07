from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

def get_current_user(request: Request):
    token = request.cookies.get("JWT_token")
    if not token:
        raise HTTPException(status_code=401, detail="請先登入")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="登入已過期，請重新登入")