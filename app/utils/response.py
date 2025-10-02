import json
from bson import ObjectId
from beanie import PydanticObjectId
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
        # fallback
        if hasattr(obj, "__str__"):
            return str(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def success(status: int = 200, data: any = None, message: str = "", cookies: dict = None):
    resp = CustomJSONResponse(
        status_code=status,
        content={
            "success": True,
            "data": data or {},
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
