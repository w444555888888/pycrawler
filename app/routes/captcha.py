# app/routes/captcha.py
from fastapi import APIRouter
from app.services import captcha_service

router = APIRouter(prefix="/captcha", tags=["captcha"])

@router.get("/init")
async def init():
    return await captcha_service.init()

@router.post("/check")
async def check(data: dict):
    return await captcha_service.check(data)