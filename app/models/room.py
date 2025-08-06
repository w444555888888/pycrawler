from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta

class PaymentOption(BaseModel):
    type: str
    description: str
    refundable: bool = False

class PricingOption(BaseModel):
    days_of_week: List[int]  # 0=Sunday
    price: float

class HolidayPrice(BaseModel):
    date: str  # YYYY-MM-DD
    price: float

class ServiceOptions(BaseModel):
    parking: bool = False
    dinner: bool = False
    breakfast: bool = True

class RoomBase(BaseModel):
    title: str
    desc: List[str]
    roomType: str
    maxPeople: int
    service: ServiceOptions
    hotelId: str
    paymentOptions: List[PaymentOption]
    pricing: List[PricingOption]
    holidays: List[HolidayPrice]

class RoomInDB(RoomBase):
    id: str = Field(..., alias="_id")

# 價格計算函式（根據 startDate, endDate）
def calculate_total_price(room: RoomBase, start_date: str, end_date: str) -> float:
    try:
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        return 0

    total_price = 0

    while current < end:
        date_str = current.strftime("%Y-%m-%d")

        # Python 的 weekday() 回傳 0=星期一，6=星期日 7會超過
        # 為了符合 JS 或資料庫中使用的 0=星期日 格式，我們用 (weekday + 1) % 7 做轉換
        weekday = (current.weekday() + 1) % 7  

        # 假日優先
        holiday = next((h for h in room.holidays if h.date == date_str), None)
        if holiday:
            total_price += holiday.price
        else:
            matched_price = next(
                (p.price for p in room.pricing if weekday in p.days_of_week),
                0
            )
            total_price += matched_price

        current += timedelta(days=1)

    return total_price
