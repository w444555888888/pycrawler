from datetime import datetime, timezone, timedelta
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict 
from beanie import Document, PydanticObjectId
from dateutil.parser import parse as parse_date
from app.models.hotel import Hotel


class Service(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    parking: bool = Field(default=False, alias="parking")
    dinner: bool = Field(default=False, alias="dinner")
    breakfast: bool = Field(default=True, alias="breakfast")


class PaymentOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal['credit_card', 'paypal', 'bank_transfer', 'on_site_payment'] = Field(..., alias="type")
    description: str = Field(..., alias="description")
    refundable: bool = Field(default=False, alias="refundable")


class WeekdayPricing(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    days_of_week: List[int] = Field(..., alias="days_of_week")
    price: float = Field(..., alias="price")


class HolidayPricing(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date: str = Field(..., alias="date")  # e.g. "2025-12-25"
    price: float = Field(..., alias="price")


class Room(Document):
    model_config = ConfigDict(populate_by_name=True)
    title: str = Field(..., alias="title")
    desc: List[str] = Field(..., alias="desc")
    room_type: Literal['Single Room', 'Double Room', 'Twin Room', 'Family Room', 'Deluxe Room', 'Triple Room'] = Field(..., alias="roomType")
    max_people: int = Field(..., alias="maxPeople")
    service: Service = Field(default_factory=Service, alias="service")
    hotel_id: PydanticObjectId = Field(..., alias="hotelId")
    payment_options: List[PaymentOption] = Field(..., alias="paymentOptions")
    pricing: List[WeekdayPricing] = Field(..., alias="pricing")
    holidays: List[HolidayPricing] = Field(..., alias="holidays")

    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "rooms"

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)


    def calculate_total_price(self, start_date: str, end_date: str) -> float:
        """計算房型在指定日期區間的總價格"""
        if not start_date or not end_date:
            print("缺少日期參數")
            return 0.0

        total_price = 0.0
        current_date = parse_date(start_date).date()
        end_date_obj = parse_date(end_date).date()
        if current_date >= end_date_obj:
            print("起訖日期不合法")
            return 0.0

        while current_date < end_date_obj:
            date_str = current_date.isoformat()
            node_day = (current_date.weekday() + 1) % 7  # Python週一=0 → Node週日=0
            # print(f"📆 {date_str} (Node週={node_day})")

            # 假日優先
            holiday_price = None
            for h in self.holidays or []:
                if isinstance(h, dict):
                    date_val, price_val = h.get("date"), h.get("price")
                else:
                    date_val, price_val = getattr(h, "date", None), getattr(h, "price", None)

                if date_val == date_str:
                    holiday_price = float(price_val.get("$numberInt", price_val)) if isinstance(price_val, dict) else float(price_val)
                    break

            if holiday_price is not None:
                total_price += holiday_price
            else:
                found = False
                for p in self.pricing or []:
                    raw_days = p.get("days_of_week", []) if isinstance(p, dict) else getattr(p, "days_of_week", [])
                    normalized_days = [
                        int(d["$numberInt"]) if isinstance(d, dict) and "$numberInt" in d else int(d)
                        for d in raw_days or []
                    ]
                    price_val = p.get("price") if isinstance(p, dict) else getattr(p, "price", None)
                    price_value = float(price_val.get("$numberInt", price_val)) if isinstance(price_val, dict) else float(price_val or 0)

                    if node_day in normalized_days:
                        total_price += price_value
                        found = True
                        break

                if not found:
                    print(f"無匹配價格，略過")

            current_date += timedelta(days=1)

        print(f"總金額: {total_price}\n")
        return total_price







