from fastapi.responses import JSONResponse
from typing import Any


def success(status: int = 200, data: Any = None, message: str = ""):
    """
    回傳統一格式的訊息
    :param status: HTTP 狀態碼
    :param data: 回傳資料內容
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