from app.models.user import User
from app.models.order import Order
from app.models.flight_order import FlightOrder
from app.utils.response import success
from app.utils.error_handler import raise_error
from passlib.hash import bcrypt
from beanie import PydanticObjectId
from typing import Dict
from app.models.flight import Flight


# 取得單一使用者與其訂單
async def get_user(user_id: str, current_user: User):
    if str(current_user["id"]) != user_id and not current_user.get("isAdmin"):
        raise_error(403, "您沒有權限執行此操作")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

    user_oid = PydanticObjectId(user_id)

    #  一般訂單
    all_order = await Order.find(Order.user_id == user_oid).to_list()

    #  航班訂單
    raw_flight_orders = await FlightOrder.find(FlightOrder.user_id == user_oid).to_list()
    all_flight_order = []
    for order in raw_flight_orders:
        flight = await Flight.get(order.flight_id)
        order_data = order.model_dump(by_alias=True, exclude_none=True)
        order_data["route"] = flight.route if flight else None
        all_flight_order.append(order_data)

    return success(
        data={
            "user": user,  
            "allOrder": all_order,  
            "allFlightOrder": all_flight_order,
        },
        message="取得使用者資料成功",
        exclude_fields=["password"]
    )


# 更新使用者資訊
async def update_user(user_id: str, data: dict, current_user: User):
    
    if str(current_user["id"]) != user_id and not current_user.get("isAdmin"):
        raise_error(403, "您沒有權限執行此操作")

    required_fields = ["password", "address", "phoneNumber", "realName"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        raise_error(400, f"缺少必要欄位：{', '.join(missing)}")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

    user.password = bcrypt.hash(data["password"])
    user.address = data["address"]
    user.phoneNumber = data["phoneNumber"]
    user.realName = data["realName"]

    await user.save()
    return success(data=user, message="使用者資料更新成功")



# 刪除使用者
async def delete_user(user_id: str, current_user: User):
    if str(current_user["id"]) != user_id and not current_user.get("isAdmin"):
        raise_error(403, "您沒有權限執行此操作")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

    await user.delete()
    return success(message="使用者已成功刪除")



# 取得全部使用者（限管理員）
async def get_all_users(current_user: dict):
    if not current_user.get("isAdmin"):
        raise_error(403, "只有管理員可以查看全部使用者")

    users = await User.find_all().to_list()
    return success(data=users, exclude_fields=["password"], message="取得所有使用者成功")


