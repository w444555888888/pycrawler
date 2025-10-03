import json
from bson import ObjectId
from beanie import PydanticObjectId
from pydantic import BaseModel
from datetime import datetime
from starlette.responses import JSONResponse


class CustomJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            default=self.json_encoder
        ).encode("utf-8")

    @staticmethod
    def json_encoder(obj):
        if isinstance(obj, (ObjectId, PydanticObjectId)):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):  # Pydantic/Beanie 物件
            return obj.model_dump(by_alias=True, exclude_none=True)
        if isinstance(obj, dict):  # dict 類型
            return obj
        # fallback
        if hasattr(obj, "__str__"):
            return str(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def success(
    status: int = 200,
    data: any = None,
    message: str = "",
    cookies: dict = None,
    exclude_fields: list[str] = None
):
    """
    建立統一格式的成功回應 (JSONResponse)

    Args:
        status (int): HTTP 狀態碼，預設 200。
        data (any): 回傳的資料，可以是 dict、list、BaseModel 或 None。
        message (str): 提示訊息，預設空字串。
        cookies (dict): 需要設定的 cookie 鍵值對 (key=value)，會附加到回應。
        exclude_fields (list[str]): 需要在輸出中排除的欄位名稱清單（例如密碼）。

    Returns:
        CustomJSONResponse: 包含格式化後 JSON 的回應物件，格式如下：
        {
            "success": True,
            "data": <處理後的資料>,
            "message": <訊息字串>
        }

    說明:
        - 若 data 是 Pydantic/Beanie 物件，會自動呼叫 `.model_dump()` 並套用 alias。
        - 若 data 是 list，會逐項處理並轉換為 dict。
        - 若 data 是 None，回傳的 data 會是空物件 {}。
        - exclude_fields 可用於移除敏感欄位（如 "password"）。
    """
     
    if data is not None:
        if isinstance(data, list):
            processed = []
            for item in data:
                if isinstance(item, BaseModel):
                    d = item.model_dump(by_alias=True, exclude_none=True)
                elif isinstance(item, dict):
                    d = item.copy()
                else:
                    processed.append(item)
                    continue

                if exclude_fields:
                    for f in exclude_fields:
                        d.pop(f, None)
                processed.append(d)
            data = processed

        elif isinstance(data, BaseModel):
            d = data.model_dump(by_alias=True, exclude_none=True)
            if exclude_fields:
                for f in exclude_fields:
                    d.pop(f, None)
            data = d

        elif isinstance(data, dict):
            d = data.copy()
            if exclude_fields:
                for f in exclude_fields:
                    d.pop(f, None)
            data = d

    resp = CustomJSONResponse(
        status_code=status,
        content={
            "success": True,
            "data": data if data is not None else {},  # 空 list 不會被轉成 {}
            "message": message
        }
    )

    if cookies:
        for k, v in cookies.items():
            resp.set_cookie(
                key=k,
                value=v,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=7 * 24 * 60 * 60,
                path="/"
            )
    return resp
