from fastapi import HTTPException
from typing import Optional, List
from beanie import PydanticObjectId
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, time
from app.models.flight import Flight, CabinClass, Schedule, Route
from app.models.flight_order import FlightOrder
from app.utils.response import success
from app.utils.error_handler import raise_error
from app.utils.flight_time_util import calculate_arrival_date
from app.utils.flight_duration import calculate_flight_duration
from app.utils.timezone import get_time_zone_by_city


# 創建新航班
async def create_flight(data: dict):
    flight_number = data.get("flightNumber")
    existing = await Flight.find_one(Flight.flight_number == flight_number)
    if existing:
        raise_error(400, "flightNumber已存在")

    route = data.get("route")
    schedules = data.get("schedules", [])
    cabin_classes = data.get("cabinClasses")
    if not cabin_classes:
        raise_error(400, "缺少 cabinClasses")

    departure_city = route.get("departureCity")
    arrival_city = route.get("arrivalCity")

    tz_name = get_time_zone_by_city(departure_city)
    if not tz_name:
        raise_error(404, f"找不到城市時區資訊：{departure_city}")
    tz = ZoneInfo(tz_name)

    duration = await calculate_flight_duration(departure_city, arrival_city)
    if not duration:
        raise_error(400, "無法自動推算 flightDuration，請確認城市名稱是否正確")

    route["flightDuration"] = duration

    fixed_schedules = []
    for s in schedules:
        local_naive = datetime.fromisoformat(s["departureDate"])   # 'YYYY-MM-DDTHH:mm:ss'
        local_aware = local_naive.replace(tzinfo=tz)               # 指定為「出發城市當地時間」
        utc_dt = local_aware.astimezone(timezone.utc)              # 轉成 UTC 存庫
        available_seats = {c["category"]: c["totalSeats"] for c in cabin_classes}
        fixed_schedules.append({
            "departureDate": utc_dt,
            "availableSeats": available_seats
        })

    flight_data = {
        **data,
        "route": route,
        "schedules": fixed_schedules,
        "cabinClasses": cabin_classes
    }    

    flight = Flight.model_validate(flight_data) 
    await flight.insert()
    return success(data=flight)



# 更新航班
async def update_flight(flight_id: str, data: dict):
    flight = await Flight.get(flight_id)
    if not flight:
        raise_error(404, "找不到該航班")

    route = data.get("route", {})
    cabin_classes = data.get("cabinClasses")
    schedules = data.get("schedules")

    if "departureCity" in route:
        tz_name = get_time_zone_by_city(route["departureCity"])
        if not tz_name :
            raise_error(400, f"找不到城市時區資訊：{route['departureCity']}")
        flight.route.departure_city = route["departureCity"]  # 子模型存取 (Route)，要用 snake_case 屬性

    if cabin_classes:
        # 這裡 cabin_classes 還是前端傳來的 dict，所以要轉成 CabinClass 模型
        flight.cabin_classes = [CabinClass(**c) for c in cabin_classes]

    if route.get("departureCity") and route.get("arrivalCity"):
        duration = await calculate_flight_duration(route["departureCity"], route["arrivalCity"])
        if not duration:
            raise_error(400, "無法自動推算 flightDuration，請確認城市名稱是否正確")
        flight.route.flight_duration = duration
        flight.route.arrival_city = route["arrivalCity"]

    if schedules and flight.route.departure_city:
        tz_name = get_time_zone_by_city(flight.route.departure_city)
        if not tz_name:
            raise_error(400, f"找不到城市時區資訊：{flight.route.departure_city}")
        tz = ZoneInfo(tz_name)

        updated_schedules = []
        for s in schedules:
            local_naive = datetime.fromisoformat(s["departureDate"])
            local_aware = local_naive.replace(tzinfo=tz)
            utc_dt = local_aware.astimezone(timezone.utc)
            # flight.cabin_classes 已經是 CabinClass 模型列表
            available_seats = {c.category: c.total_seats for c in flight.cabin_classes}
            updated_schedules.append({
                "departureDate": utc_dt,
                "availableSeats": available_seats
            })
        flight.schedules = updated_schedules

    await flight.save()
    return success(data=flight)



# 獲取所有航班列表 || (日期開始 && 日期結束 && 起飛城市 && 目的城市)
async def list_flights(
    departure_city: Optional[str] = None,
    arrival_city: Optional[str] = None,
    start_date: Optional[str] = None,   # 'YYYY-MM-DD'
    end_date: Optional[str] = None      # 'YYYY-MM-DD'
):
    """
    對齊 Node 版 getAllFlights：
    - 搜尋模式：四參數必填；用起飛城市時區把 start/end 的「本地日界」轉成 UTC，篩 schedule.departureDate（UTC）
    - 非搜尋模式：回全部，但只回有至少一筆 schedule 的航班
    """
    is_search_mode = any([departure_city, arrival_city, start_date, end_date])

    # 只要進入搜尋模式就要求四個都要有
    if is_search_mode and not all([departure_city, arrival_city, start_date, end_date]):
        raise_error(400, "搜尋航班需要同時提供：出發地、目的地、起始時間、結束時間")

    if is_search_mode:
        # 嚴格驗證日期格式
        try:
            start_d = datetime.strptime(start_date, "%Y-%m-%d").date()
        except Exception:
            raise_error(400, f"startDate 格式不正確：{start_date}（需 'YYYY-MM-DD'）")
        try:
            end_d = datetime.strptime(end_date, "%Y-%m-%d").date()
        except Exception:
            raise_error(400, f"endDate 格式不正確：{end_date}（需 'YYYY-MM-DD'）")

        # 依城市求時區（字串）→ 轉 ZoneInfo
        tz_name = get_time_zone_by_city(departure_city)
        if not tz_name:
            raise_error(400, f"找不到城市時區資訊：{departure_city}")
        tz = ZoneInfo(tz_name)

        # 本地日界 → UTC
        start_local = datetime.combine(start_d, time(0, 0, 0), tzinfo=tz)
        end_local   = datetime.combine(end_d,   time(23, 59, 59, 999000), tzinfo=tz)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc   = end_local.astimezone(timezone.utc)

        # 先用城市過濾，再在記憶體內以區間篩選 schedules
        flights: List[Flight] = await Flight.find(
            (Flight.route.departure_city == departure_city) &
            (Flight.route.arrival_city == arrival_city)
        ).to_list()

        result = []
        for f in flights:
            filtered = []
            for s in (f.schedules or []):
                # 讀取 departureDate（兼容子模型或 dict）
                dep = getattr(s, "departure_date", None)
                if dep is None and isinstance(s, dict):
                    dep = s.get("departureDate")
                if not isinstance(dep, datetime):
                    continue
                # 若是 naive，視為 UTC；再確保是 UTC aware
                if dep.tzinfo is None:
                    dep = dep.replace(tzinfo=timezone.utc)
                dep = dep.astimezone(timezone.utc)

                if start_utc <= dep <= end_utc:
                    filtered.append(s)

            if filtered:
                result.append({
                    "_id": str(f.id),
                    "flightNumber": f.flight_number,
                    "route": f.route.model_dump(by_alias=True, exclude_none=True),
                    "schedules": filtered
                })

        return success(result)

    # 非搜尋模式：全部航班（只回有至少一筆 schedule 的）
    flights: List[Flight] = await Flight.find_all().to_list()
    result = []
    for f in flights:
        if f.schedules:
            result.append({
                "_id": str(f.id),
                "flightNumber": f.flight_number,
                "route": f.route.model_dump(by_alias=True, exclude_none=True),
                "schedules": f.schedules
            })
    return success(data=result)


# 獲取單個航班詳情
async def get_flight(flight_id: str):
    flight = await Flight.get(flight_id)
    if not flight:
        raise_error(404, "找不到該航班")

    formatted_schedules = []
    for idx, s in enumerate(flight.schedules or []):
        # 取出出發/到達時間
        dep_dt = s.departure_date
        arr_dt = s.arrival_date

        # 正規化為 UTC aware 再輸出 ISO
        if isinstance(dep_dt, datetime):
            if dep_dt.tzinfo is None:
                dep_dt = dep_dt.replace(tzinfo=timezone.utc)
            dep_dt = dep_dt.astimezone(timezone.utc)
        else:
            raise_error(500, "schedule.departureDate 缺失或格式錯誤")

        if isinstance(arr_dt, datetime):
            if arr_dt.tzinfo is None:
                arr_dt = arr_dt.replace(tzinfo=timezone.utc)
            arr_dt = arr_dt.astimezone(timezone.utc)
        else:
            arr_dt = None  # 理論上你的 before_event 會補好，這裡保險處理

        # 計算每個艙等的價格（await 你的 async 方法）
        prices = {}
        for c in flight.cabin_classes or []:
            raw = await flight.calculate_final_price(c.category, dep_dt)
            prices[c.category] = round(raw)

        # 取 schedule 的 _id/id（嵌入式模型預設沒有 id，就退回用索引）
        sched_id = (
            getattr(s, "id", None)
            or getattr(s, "_id", None)
            or idx
        )

        formatted_schedules.append({
            "_id": str(sched_id),
            "departureDate": dep_dt.isoformat(),
            "arrivalDate": arr_dt.isoformat() if isinstance(arr_dt, datetime) else None,
            "availableSeats": s.available_seats,
            "prices": prices,
        })

    return success(data={
        "_id": str(flight.id),
        "flightNumber": flight.flight_number,
        "route": flight.route.model_dump(by_alias=True, exclude_none=True),  # camelCase: departureCity/arrivalCity/flightDuration
        "schedules": formatted_schedules,
    })



# 刪除航班
async def delete_flight(flight_id: str):
    flight = await Flight.get(flight_id)
    if not flight:
        raise_error(404, "找不到該航班")
    await flight.delete()
    return success(message="刪除成功")




#-----------------------------------訂票FlightOrder------------------------------------

# 後台用：獲取全部機票訂單
async def get_all_flight_orders():
    try:
        orders = await FlightOrder.find_all().to_list()
        return success(data=orders)
    except Exception:
        raise_error(500, "獲取機票訂單失敗")


# 創建航班訂單 
async def create_flight_order(data: dict, user_id: str):
    from uuid import uuid4

    flight_id = data.get("flightId")
    category = data.get("category")
    passengers = data.get("passengerInfo")

    if not all([flight_id, category, passengers]):
        raise_error(400, "缺少必要的訂單信息")

    # 找航班
    flight = await Flight.get(flight_id)
    if not flight:
        raise_error(404, "找不到該航班")

    if not flight.schedules:
        raise_error(404, "該航班沒有班次")

    # 沒有 scheduleId → 預設用第一個班次
    schedule = flight.schedules[0]

    # 檢查座位
    if schedule.available_seats.get(category, 0) < len(passengers):
        raise_error(400, "座位數量不足")

    # 檢查是否已有相同待處理的訂單（比對 flightId + userId + category）
    existing_order = await FlightOrder.find_one({
        "userId": user_id,
        "flightId": flight_id,
        "category": category,
        "status": "PENDING"
    })
    if existing_order:
        raise_error(409, "您已有相同航班的待處理訂單")

    # 計算價格
    base_price = round(await flight.calculate_final_price(category, schedule.departure_date))
    tax = round(base_price * 0.1)
    total_price = round((base_price + tax) * len(passengers))

    # 訂單編號
    order_number = f"FO{str(uuid4()).split('-')[0]}"

    order = FlightOrder(
        userId=user_id,
        flightId=flight_id,
        orderNumber=order_number,
        passengerInfo=passengers,
        category=category,
        scheduleId=str(getattr(schedule, "id", None) or getattr(schedule, "_id", None) or 0),  
        price={
            "basePrice": base_price,
            "tax": tax,
            "totalPrice": total_price
        }
    )
    await order.insert()

    # 更新座位
    schedule.available_seats[category] -= len(passengers)
    await flight.save()

    return success(data=order)




# 獲取用戶的所有訂單
async def get_user_orders(user_id: str):
    orders = await FlightOrder.find(FlightOrder.userId == PydanticObjectId(user_id)).to_list()
    return success(data=orders)


# 獲取訂單詳情
async def get_order_detail(order_id: str):
    order = await FlightOrder.get(order_id)
    if not order:
        raise_error(404, "找不到該訂單")
    return success(data=order)


# 取消訂單
async def cancel_order(order_id: str, user_id: str):
    order = await FlightOrder.get(order_id)
    if not order:
        raise_error(404, "找不到該訂單")

    if order.userId != user_id:
        raise_error(403, "無權限取消此訂單")

    if order.status != "PENDING":
        raise_error(400, "只能取消待付款的訂單")

    flight = await Flight.get(order.flightId)
    if not flight:
        raise_error(404, "找不到相關航班")

    schedule = next((s for s in flight.schedules if str(s["_id"]) == order.scheduleId), None)
    if not schedule:
        raise_error(404, "找不到對應航班班次")

    order.status = "CANCELLED"
    await order.save()

    schedule["availableSeats"][order.category] += len(order.passengerInfo)
    await flight.save()

    return success(data=order)
