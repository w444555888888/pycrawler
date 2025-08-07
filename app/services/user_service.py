from fastapi import HTTPException
from app.models.user import User
from app.models.order import Order
from app.models.flight_order import FlightOrder
from app.utils.response import success
from app.utils.error_message import ErrorMessage
from beanie import PydanticObjectId
from passlib.hash import bcrypt
from typing import Dict


async def get_user(user_id: str, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail=ErrorMessage.PERMISSION_DENIED)

    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=ErrorMessage.USER_NOT_FOUND)

    all_order = await Order.find(Order.user_id == user_id).to_list()

    raw_flight_orders = await FlightOrder.find(FlightOrder.user_id == user_id).to_list()
    all_flight_order = []
    for order in raw_flight_orders:
        flight = await order.flight_id.fetch()
        order_data = order.dict()
        order_data["route"] = flight.route if flight else None
        all_flight_order.append(order_data)

    return success({
        **user.dict(),
        "allOrder": all_order,
        "allFightOrder": all_flight_order
    })


async def update_user(user_id: str, data: Dict, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail=ErrorMessage.PERMISSION_DENIED)

    required_fields = ["password", "address", "phoneNumber", "realName"]
    if not all(data.get(k) for k in required_fields):
        raise HTTPException(status_code=400, detail=ErrorMessage.REQUIRED_FIELDS_MISSING)

    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=ErrorMessage.USER_NOT_FOUND)

    hashed_password = bcrypt.hash(data["password"])
    user.password = hashed_password
    user.address = data["address"]
    user.phoneNumber = data["phoneNumber"]
    user.realName = data["realName"]

    await user.save()
    return success(user)


async def delete_user(user_id: str, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail=ErrorMessage.PERMISSION_DENIED)

    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=ErrorMessage.USER_NOT_FOUND)

    await user.delete()
    return success(message="User deleted successfully")


async def get_all_users(current_user: User):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail=ErrorMessage.PERMISSION_DENIED)

    users = await User.find_all().to_list()
    return success(users)
