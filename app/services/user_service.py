from app.models.user import User
from app.models.order import Order
from app.models.flight_order import FlightOrder
from app.utils.response import success
from app.utils.error_handler import raise_error
from passlib.hash import bcrypt
from typing import Dict


# 取得單一使用者與其訂單
async def get_user(user_id: str, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise_error(403, "您沒有權限執行此操作")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

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


# 更新使用者資訊
async def update_user(user_id: str, data: Dict, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise_error(403, "您沒有權限執行此操作")

    required_fields = ["password", "address", "phoneNumber", "realName"]
    if not all(data.get(k) for k in required_fields):
        raise_error(400, "缺少必要欄位：密碼、地址、電話、真實姓名")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

    hashed_password = bcrypt.hash(data["password"])
    user.password = hashed_password
    user.address = data["address"]
    user.phoneNumber = data["phoneNumber"]
    user.realName = data["realName"]

    await user.save()
    return success(user)


# 刪除使用者
async def delete_user(user_id: str, current_user: User):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise_error(403, "您沒有權限執行此操作")

    user = await User.get(user_id)
    if not user:
        raise_error(404, "找不到該使用者")

    await user.delete()
    return success(message="使用者已成功刪除")


# 取得全部使用者（限管理員）
async def get_all_users(current_user: User):
    if not current_user.is_admin:
        raise_error(403, "只有管理員可以查看全部使用者")

    users = await User.find_all().to_list()
    return success(users)
