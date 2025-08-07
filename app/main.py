# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.error_handler import raise_error 
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.routes import hotels, rooms, auth, users
from app.db import init_db

app = FastAPI(title="Hotel Booking API")

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

# 路由註冊（保留原有路由）
app.include_router(hotels.router, prefix="/api/v1/hotels")
app.include_router(rooms.router, prefix="/api/v1/rooms")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(users.router, prefix="/api/v1/users")


#  HTTPException 統一格式處理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail.get("message", "錯誤"),
                "details": exc.detail.get("details", None)
            },
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": str(exc.detail)
            },
        )
    


#  驗證錯誤格式統一
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "參數錯誤",
            "details": exc.errors()
        },
    )


# 捕捉所有未處理的錯誤（最後保底）
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