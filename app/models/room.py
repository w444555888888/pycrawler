from datetime import datetime, date, timedelta
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from dateutil.parser import parse as parse_date


class Service(BaseModel):
    parking: bool = False
    dinner: bool = False
    breakfast: bool = True


class PaymentOption(BaseModel):
    type: Literal['credit_card', 'paypal', 'bank_transfer', 'on_site_payment']
    description: str
    refundable: bool = False


class WeekdayPricing(BaseModel):
    days_of_week: List[int]  # 0 ~ 6
    price: float


class HolidayPricing(BaseModel):
    date: str  # e.g. "2025-12-25"
    price: float


class Room(Document):
    title: str
    desc: List[str]
    room_type: Literal['Single Room', 'Double Room', 'Twin Room', 'Family Room', 'Deluxe Room']
    max_people: int
    service: Service = Service()
    hotel_id: PydanticObjectId
    payment_options: List[PaymentOption]
    pricing: List[WeekdayPricing]
    holidays: List[HolidayPricing]

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rooms"

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def calculate_total_price(self, start_date: str, end_date: str) -> float:
        total_price = 0.0
        current_date = parse_date(start_date).date()
        end_date_obj = parse_date(end_date).date()

        while current_date < end_date_obj:
            date_str = current_date.isoformat()
            day_of_week = current_date.weekday()

            # 1. check holiday
            holiday_price = next((h.price for h in self.holidays if h.date == date_str), None)

            if holiday_price is not None:
                total_price += holiday_price
            else:
                # 2. weekday price
                for p in self.pricing:
                    if day_of_week in p.days_of_week:
                        total_price += p.price
                        break

            current_date += timedelta(days=1)

        return total_price
