from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_auths():
    return {"message": "這是 Auth API"}
