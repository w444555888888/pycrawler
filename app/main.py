# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.routes import hotels, rooms, users, auth, order, flight, captcha
from app.db import init_db
from app.utils.error_handler import http_error_handler, validation_exception_handler

app = FastAPI(title="Hotel Booking API")

# 啟動時初始化 DB
@app.on_event("startup")
async def on_startup():
    await init_db()

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由註冊
app.include_router(hotels.router, prefix="/api/v1/hotels")
app.include_router(rooms.router, prefix="/api/v1/rooms")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(order.router, prefix="/api/v1/order")
app.include_router(flight.router, prefix="/api/v1/flight")
app.include_router(captcha.router, prefix="/api/v1/captcha")

# 統一錯誤格式處理器
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 捕捉所有未處理的錯誤（兜底）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "伺服器錯誤",
            "details": str(exc)
        }
    )

# 根路由
@app.get("/")
async def root():
    return {"message": "FastAPI server running"}
