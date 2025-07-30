from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_hotels():
    return {"message": "這是 Hotel API"}
