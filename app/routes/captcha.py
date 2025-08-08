# app/routes/captcha.py
from fastapi import APIRouter
from app.services import captcha_service

router = APIRouter(tags=["captcha"])

@router.get("/initCaptcha")
async def route_init():
    return await captcha_service.init()

@router.post("/verifyCaptcha")
async def route_check(data: dict):
    return await captcha_service.check(data)