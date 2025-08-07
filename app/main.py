# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.db import init_db
from app.routes import hotels, rooms, auth, users

# 建立 FastAPI 實例
app = FastAPI(title="Hotel Booking API")

# 初始化 MongoDB
init_db()

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
app.include_router(auth.router, prefix="/api/v1/auth")  
app.include_router(users.router, prefix="/api/v1/users") 

# 全域錯誤處理
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

# 根路由
@app.get("/")
async def root():
    return {"message": "FastAPI server running"}
