from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_flights():
    return {"message": "這是 Flight API"}
