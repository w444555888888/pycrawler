from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_orders():
    return {"message": "這是 Order API"}