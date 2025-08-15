from datetime import datetime, timezone, timedelta
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict 
from beanie import Document, PydanticObjectId
from dateutil.parser import parse as parse_date


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
    room_type: Literal['Single Room', 'Double Room', 'Twin Room', 'Family Room', 'Deluxe Room'] = Field(..., alias="roomType")
    max_people: int = Field(..., alias="maxPeople")
    service: Service = Field(default_factory=Service, alias="service")
    hotel_id: PydanticObjectId = Field(..., alias="hotelId")
    payment_options: List[PaymentOption] = Field(..., alias="paymentOptions")
    pricing: List[WeekdayPricing] = Field(..., alias="pricing")
    holidays: List[HolidayPricing] = Field(..., alias="holidays")

    created_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "rooms"

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)

    def calculate_total_price(self, start_date: str, end_date: str) -> float:
        total_price = 0.0
        current_date = parse_date(start_date).date()
        end_date_obj = parse_date(end_date).date()

        while current_date < end_date_obj:
            date_str = current_date.isoformat()
            day_of_week = current_date.weekday()

            # 節假日價格優先
            holiday_price = next((h.price for h in self.holidays if h.date == date_str), None)

            if holiday_price is not None:
                total_price += holiday_price
            else:
                # 找對應的平日價格
                for p in self.pricing:
                    if day_of_week in p.days_of_week:
                        total_price += p.price
                        break

            current_date += timedelta(days=1)

        return total_price
