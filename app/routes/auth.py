from fastapi import APIRouter, Request, Response
from app.services.auth_service import (
    register,
    login,
    forgot_password,
    reset_password,
    me,
    logout,
    verify_token
)

router = APIRouter(tags=["auth"])


@router.post("/register")
async def route_register(request: Request):
    data = await request.json()
    return await register(data)


@router.post("/login")
async def route_login(request: Request, response: Response):
    data = await request.json()
    return await login(data, response)


@router.post("/forgot-password")
async def route_forgot_password(request: Request):
    data = await request.json()
    return await forgot_password(data)


@router.post("/reset-password/{token}")
async def route_reset_password(token: str, request: Request):
    data = await request.json()
    new_password = data.get("password") 
    return await reset_password(token, new_password)


@router.get("/me")
async def route_me(request: Request):
    verify_token(request)  # 驗證 JWT，失敗會自動 raise HTTPException
    return me(request)


@router.post("/logout")
async def route_logout(request: Request, response: Response):
    verify_token(request)  # 先驗證，再執行 logout
    return logout(response)
