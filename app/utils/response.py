from fastapi.responses import JSONResponse
from typing import Any


def send_response(status: int = 200, data: Any = None, message: str = ""):
    """
    回傳統一格式的成功訊息
    :param status: HTTP 狀態碼
    :param data: 要回傳的資料
    :param message: 額外訊息文字
    """
    return JSONResponse(
        status_code=status,
        content={
            "success": True,
            "data": data or {},
            "message": message
        }
    )


def success(data: Any = None):
    """
    成功格式（FastAPI 回傳用）
    """
    return JSONResponse(
        status_code=200,
        content={"code": 0, "message": "success", "data": data or {}}
    )