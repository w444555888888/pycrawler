# app/routes/order.py
from fastapi import APIRouter
from app.services import order_service

router = APIRouter(prefix="/order", tags=["order"])

@router.post("/create")
async def create_order(data: dict):
    return await order_service.create_order(data)

@router.get("/list")
async def list_orders():
    return await order_service.list_orders()

@router.get("/detail/{id}")
async def order_detail(id: str):
    return await order_service.order_detail(id)