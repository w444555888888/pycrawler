# app/routes/captcha.py
from fastapi import APIRouter, Body
from app.services import captcha_service

router = APIRouter(tags=["captcha"])

@router.get("/initCaptcha")
async def route_init():
    return captcha_service.init()

@router.post("/verifyCaptcha")
async def route_check(data: dict = Body(...)):
    return captcha_service.check(data)