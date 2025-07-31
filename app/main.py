# app/main.py

# 載入 FastAPI 套件與相關模組(自動處理cookie, JSON)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 匯入自定義設定與路由模組
from app.core.config import settings
from app.api import hotels, rooms, users, auth, order, flight, captcha

# 匯入 motor 用於非同步連接 MongoDB
import motor.motor_asyncio

# 匯入 logging 模組記錄錯誤
import logging

# 建立 FastAPI 應用實例
app = FastAPI()

# 1. 設定 MongoDB 連線（非同步 motor）
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=5000,  # 連線逾時設定（毫秒）
    maxPoolSize=10                  # 最大連線池數量
)
db = client.get_default_database()  # 取得預設資料庫（從 URI 抓）

# 2. 設定 CORS（跨來源資源共用）
allowed_origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,   # 允許的前端來源
    allow_credentials=True,          # 是否允許攜帶 cookie
    allow_methods=["*"],             # 允許所有 HTTP 方法
    allow_headers=["*"]              # 允許所有自訂 header
)

# 3. 註冊各模組路由（類似 Express 的 app.use(...)）
app.include_router(hotels.router, prefix="/api/v1/hotels")
app.include_router(rooms.router, prefix="/api/v1/rooms")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(order.router, prefix="/api/v1/order")
app.include_router(flight.router, prefix="/api/v1/flight")
app.include_router(captcha.router, prefix="/api/v1/captcha")

# 4. 全域錯誤處理（類似 Express 的錯誤 middleware）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception: %s", str(exc))  # 紀錄錯誤訊息到 log
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "伺服器錯誤",
            "success": False,
            "data": None
        }
    )

# 5. 預設首頁（用來確認伺服器是否有啟動）
@app.get("/")
async def root():
    return {"message": "FastAPI server running"}
