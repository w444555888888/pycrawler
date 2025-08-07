# app/routes/auth.py
from fastapi import APIRouter
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(data: dict):
    return await auth_service.register(data)

@router.post("/login")
async def login(data: dict):
    return await auth_service.login(data)

@router.get("/verify-token")
async def verify_token(token: str):
    return await auth_service.verify_token(token)

@router.post("/forgot-password")
async def forgot_password(data: dict):
    return await auth_service.forgot_password(data)

@router.post("/reset-password")
async def reset_password(data: dict):
    return await auth_service.reset_password(data)