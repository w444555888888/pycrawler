from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_captcha():
    return {"message": "這是 Captcha API"}
