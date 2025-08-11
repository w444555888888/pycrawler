from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from beanie import Document, Indexed, before_event, Insert  
from app.utils.flight_time_util import calculate_arrival_date


class CabinClass(BaseModel):
    category: Literal['ECONOMY', 'BUSINESS', 'FIRST']
    base_price: float = Field(alias="basePrice")
    total_seats: int = Field(alias="totalSeats")
    booked_seats: int = Field(default=0, alias="bookedSeats")


class PeakSeasonPeriod(BaseModel):
    start: datetime
    end: datetime
    multiplier: float = 1.2


class EarlyBirdDiscount(BaseModel):
    days_in_advance: int = Field(default=30, alias="daysInAdvance")
    discount: float = 0.9


class PriceRules(BaseModel):
    peak_season_dates: List[PeakSeasonPeriod] = Field(default=[], alias="peakSeasonDates")
    holiday_multiplier: float = Field(default=1.1, alias="holidayMultiplier")
    early_bird_discount: EarlyBirdDiscount = Field(default_factory=EarlyBirdDiscount, alias="earlyBirdDiscount")


class Schedule(BaseModel):
    departure_date: datetime = Field(alias="departureDate")
    arrival_date: Optional[datetime] = Field(default=None, alias="arrivalDate")
    available_seats: dict[str, int] = Field(alias="availableSeats")
    prices: dict[str, float]


class Route(BaseModel):
    departure_city: str = Field(alias="departureCity")
    arrival_city: str = Field(alias="arrivalCity")
    flight_duration: int = Field(alias="flightDuration")


class Flight(Document):
    flight_number: Indexed(str, unique=True) = Field(alias="flightNumber")
    route: Route
    cabin_classes: List[CabinClass] = Field(alias="cabinClasses")
    price_rules: PriceRules = Field(default_factory=PriceRules, alias="priceRules")
    schedules: List[Schedule] = Field(default=[], alias="schedules")

    class Settings:
        name = "flights"

    class Config:
        populate_by_name = True

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
        now = datetime.now(timezone.utc)
        days_until = (departure_date - now).days
        if days_until >= self.price_rules.early_bird_discount.days_in_advance:
            multiplier *= self.price_rules.early_bird_discount.discount

        return base_price * multiplier

    @before_event(Insert)
    async def fill_schedule_arrival_dates(self):
        updated_schedules = []
        for s in self.schedules:
            if s.arrival_date is None:
                arrival_date = await calculate_arrival_date(
                    s.departure_date,
                    self.route.flight_duration,
                    self.route.departure_city,
                    self.route.arrival_city
                )
                updated_schedules.append(Schedule(
                    departure_date=s.departure_date,
                    arrival_date=arrival_date,
                    available_seats=s.available_seats,
                    prices=s.prices
                ))
            else:
                updated_schedules.append(s)
        self.schedules = updated_schedules
