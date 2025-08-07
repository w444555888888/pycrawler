from fastapi import HTTPException
from datetime import datetime
from app.models.flight import Flight
from app.models.flight_order import FlightOrder
from app.utils.response import success
from app.utils.flight_time_util import calculate_arrival_date
from app.utils.flight_duration import calculate_flight_duration
from app.utils.timezone import get_time_zone_by_city


async def list_flights():
    flights = await Flight.find_all().to_list()
    return success(flights)


async def create_flight(data: dict):
    flight_number = data.get("flightNumber")
    existing = await Flight.find_one(Flight.flightNumber == flight_number)
    if existing:
        raise HTTPException(status_code=400, detail="flightNumber已存在")

    route = data.get("route")
    schedules = data.get("schedules", [])
    cabin_classes = data.get("cabinClasses")
    if not cabin_classes:
        raise HTTPException(status_code=400, detail="缺少 cabinClasses")

    departure_city = route.get("departureCity")
    arrival_city = route.get("arrivalCity")

    tz = get_time_zone_by_city(departure_city)
    if not tz:
        raise HTTPException(status_code=404, detail=f"找不到城市時區資訊：{departure_city}")

    duration = calculate_flight_duration(departure_city, arrival_city)
    if not duration:
        raise HTTPException(status_code=400, detail="無法自動推算 flightDuration，請確認城市名稱是否正確")

    route["flightDuration"] = duration

    fixed_schedules = []
    for s in schedules:
        local_dt = datetime.fromisoformat(s["departureDate"])
        available_seats = {c["category"]: c["totalSeats"] for c in cabin_classes}
        fixed_schedules.append({
            "departureDate": local_dt.astimezone(tz).astimezone(datetime.timezone.utc),
            "availableSeats": available_seats
        })

    flight = Flight(**data)
    flight.route = route
    flight.schedules = fixed_schedules
    await flight.insert()
    return success(flight)


async def get_flight(flight_id: str):
    flight = await Flight.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="找不到該航班")
    return success(flight)


async def update_flight(flight_id: str, data: dict):
    flight = await Flight.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="找不到該航班")

    route = data.get("route", {})
    cabin_classes = data.get("cabinClasses")
    schedules = data.get("schedules")

    if "departureCity" in route:
        tz = get_time_zone_by_city(route["departureCity"])
        if not tz:
            raise HTTPException(status_code=400, detail=f"找不到城市時區資訊：{route['departureCity']}")
        flight.route["departureCity"] = route["departureCity"]

    if cabin_classes:
        flight.cabinClasses = cabin_classes

    if route.get("departureCity") and route.get("arrivalCity"):
        duration = calculate_flight_duration(route["departureCity"], route["arrivalCity"])
        if not duration:
            raise HTTPException(status_code=400, detail="無法自動推算 flightDuration，請確認城市名稱是否正確")
        flight.route["flightDuration"] = duration
        flight.route["arrivalCity"] = route["arrivalCity"]

    if schedules and flight.route.get("departureCity"):
        tz = get_time_zone_by_city(flight.route["departureCity"])
        updated_schedules = []
        for s in schedules:
            local_dt = datetime.fromisoformat(s["departureDate"])
            available_seats = {c["category"]: c["totalSeats"] for c in flight.cabinClasses}
            updated_schedules.append({
                "departureDate": local_dt.astimezone(tz).astimezone(datetime.timezone.utc),
                "availableSeats": available_seats
            })
        flight.schedules = updated_schedules

    await flight.save()
    return success(flight)


async def delete_flight(flight_id: str):
    flight = await Flight.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="找不到該航班")
    await flight.delete()
    return success(flight)


async def create_flight_order(data: dict, user_id: str):
    from uuid import uuid4

    flight_id = data.get("flightId")
    category = data.get("category")
    schedule_id = data.get("scheduleId")
    passengers = data.get("passengerInfo")

    if not all([flight_id, category, schedule_id, passengers]):
        raise HTTPException(status_code=400, detail="缺少必要的訂單信息")

    flight = await Flight.get(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="找不到該航班")

    schedule = next((s for s in flight.schedules if str(s["_id"]) == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="找不到該航班班次")

    if schedule["availableSeats"].get(category, 0) < len(passengers):
        raise HTTPException(status_code=400, detail="座位數量不足")

    existing_order = await FlightOrder.find_one({
        "userId": user_id,
        "flightId": flight_id,
        "scheduleId": schedule_id,
        "status": "PENDING"
    })
    if existing_order:
        raise HTTPException(status_code=409, detail="您已有相同航班的待處理訂單")

    base_price = round(flight.calculate_final_price(category, schedule["departureDate"]))
    tax = round(base_price * 0.1)
    total_price = round((base_price + tax) * len(passengers))

    order_number = f"FO{str(uuid4()).split('-')[0]}"

    order = FlightOrder(
        userId=user_id,
        flightId=flight_id,
        orderNumber=order_number,
        passengerInfo=passengers,
        category=category,
        scheduleId=schedule_id,
        price={
            "basePrice": base_price,
            "tax": tax,
            "totalPrice": total_price
        }
    )
    await order.insert()

    # update seat
    schedule["availableSeats"][category] -= len(passengers)
    await flight.save()

    return success(order)


async def cancel_order(order_id: str, user_id: str):
    order = await FlightOrder.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="找不到該訂單")

    if order.userId != user_id:
        raise HTTPException(status_code=403, detail="無權限取消此訂單")

    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="只能取消待付款的訂單")

    flight = await Flight.get(order.flightId)
    if not flight:
        raise HTTPException(status_code=404, detail="找不到相關航班")

    schedule = next((s for s in flight.schedules if str(s["_id"]) == order.scheduleId), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="找不到對應航班班次")

    order.status = "CANCELLED"
    await order.save()

    schedule["availableSeats"][order.category] += len(order.passengerInfo)
    await flight.save()

    return success(order)


async def get_user_orders(user_id: str):
    orders = await FlightOrder.find(FlightOrder.userId == user_id).to_list()
    return success(orders)


async def get_order_detail(order_id: str):
    order = await FlightOrder.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="找不到該訂單")
    return success(order)
