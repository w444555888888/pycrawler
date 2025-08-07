from datetime import datetime, date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from beanie import Document, Indexed, PydanticObjectId, before_event
from utils.flight_time import calculate_arrival_date


class CabinClass(BaseModel):
    category: Literal['ECONOMY', 'BUSINESS', 'FIRST']
    base_price: float
    total_seats: int
    booked_seats: int = 0


class PeakSeasonPeriod(BaseModel):
    start: datetime
    end: datetime
    multiplier: float = 1.2


class EarlyBirdDiscount(BaseModel):
    days_in_advance: int = 30
    discount: float = 0.9


class PriceRules(BaseModel):
    peak_season_dates: List[PeakSeasonPeriod] = []
    holiday_multiplier: float = 1.1
    early_bird_discount: EarlyBirdDiscount = EarlyBirdDiscount()


class Schedule(BaseModel):
    departure_date: datetime
    arrival_date: Optional[datetime] = None
    available_seats: dict[str, int]
    prices: dict[str, float]


class Route(BaseModel):
    departure_city: str
    arrival_city: str
    flight_duration: int  # minutes or hours


class Flight(Document):
    flight_number: Indexed(str, unique=True)
    route: Route
    cabin_classes: List[CabinClass]
    price_rules: PriceRules = PriceRules()
    schedules: List[Schedule] = []

    class Settings:
        name = "flights"

    async def calculate_final_price(self, category: str, departure_date: datetime) -> float:
        base_price = next((c.base_price for c in self.cabin_classes if c.category == category), 0)
        multiplier = 1.0

        # 旺季
        for period in self.price_rules.peak_season_dates:
            if period.start <= departure_date <= period.end:
                multiplier *= period.multiplier
                break

        # 假日（週六日）
        if departure_date.weekday() in (5, 6):
            multiplier *= self.price_rules.holiday_multiplier

        # 早鳥
        now = datetime.utcnow()
        days_until = (departure_date - now).days
        if days_until >= self.price_rules.early_bird_discount.days_in_advance:
            multiplier *= self.price_rules.early_bird_discount.discount

        return base_price * multiplier

    @before_event("insert")
    async def compute_arrival_dates(self):
        for schedule in self.schedules:
            if not schedule.arrival_date:
                schedule.arrival_date = await calculate_arrival_date(
                    schedule.departure_date,
                    self.route.flight_duration,
                    self.route.departure_city,
                    self.route.arrival_city
                )
