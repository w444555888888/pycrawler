# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import hotels, rooms, users, auth, order, flight, captcha
import motor.motor_asyncio
import logging

app = FastAPI()

# 1. 設定 MongoDB 連線（非同步）
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=5000,
    maxPoolSize=10
)
db = client.get_default_database()

#  2. 跨域設定 CORS
allowed_origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#  3. 路由掛載
app.include_router(hotels.router, prefix="/api/v1/hotels")
app.include_router(rooms.router, prefix="/api/v1/rooms")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(order.router, prefix="/api/v1/order")
app.include_router(flight.router, prefix="/api/v1/flight")
app.include_router(captcha.router, prefix="/api/v1/captcha")

#  4. 全域錯誤處理（取代 Express 的 middleware error handler）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "伺服器錯誤",
            "success": False,
            "data": None
        }
    )

#  5. 預設首頁（測試是否正常啟動）
@app.get("/")
async def root():
    return {"message": "FastAPI server running"}
