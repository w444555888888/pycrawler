from datetime import datetime, timezone, timedelta
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from beanie import Document, PydanticObjectId, Indexed, before_event, Insert, Replace 
from app.utils.flight_time_util import calculate_arrival_date


class CabinClass(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    category: Literal['ECONOMY', 'BUSINESS', 'FIRST']
    base_price: float = Field(alias="basePrice")
    total_seats: int = Field(alias="totalSeats")
    booked_seats: int = Field(default=0, alias="bookedSeats")


class PeakSeasonPeriod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start: datetime
    end: datetime
    multiplier: float = 1.2


class EarlyBirdDiscount(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    days_in_advance: int = Field(default=30, alias="daysInAdvance")
    discount: float = 0.9


class PriceRules(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    peak_season_dates: List[PeakSeasonPeriod] = Field(default_factory=list, alias="peakSeasonDates")
    holiday_multiplier: float = Field(default=1.1, alias="holidayMultiplier")
    early_bird_discount: EarlyBirdDiscount = Field(default_factory=EarlyBirdDiscount, alias="earlyBirdDiscount")


class Schedule(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    departure_date: datetime = Field(alias="departureDate")
    arrival_date: Optional[datetime] = Field(default=None, alias="arrivalDate")
    available_seats: dict[str, int] = Field(alias="availableSeats")
    prices: dict[str, float] = Field(default_factory=dict)


class Route(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    departure_city: str = Field(alias="departureCity")
    arrival_city: str = Field(alias="arrivalCity")
    flight_duration: int = Field(alias="flightDuration")


class Flight(Document):
    model_config = ConfigDict(populate_by_name=True)
    flight_number: Indexed(str, unique=True) = Field(alias="flightNumber")
    route: Route
    cabin_classes: List[CabinClass] = Field(alias="cabinClasses")
    price_rules: PriceRules = Field(default_factory=PriceRules, alias="priceRules")
    schedules: List[Schedule] = Field(default_factory=list, alias="schedules")

    class Settings:
        name = "flights"

    async def calculate_final_price(self, category: str, departure_date: datetime) -> float:
        """
        計算指定艙等在某出發時間的最終票價。
        - 價格規則包含：旺季、週末假日加成、早鳥折扣。
        - 一律以 UTC 為基準做時間比較，避免跨時區誤差。
        """
        # CHANGED: 統一把 departure_date 正規化為 UTC-aware
        dep = departure_date
        if dep.tzinfo is None:
            dep = dep.replace(tzinfo=timezone.utc)
        else:
            dep = dep.astimezone(timezone.utc)

        # 取艙等基礎價   
        base_price = next((c.base_price for c in self.cabin_classes if c.category == category), 0.0)
        multiplier = 1.0

         # CHANGED: 旺季期間比較也正規化為 UTC，避免 naive/aware 混淆
        for period in self.price_rules.peak_season_dates:
            start = period.start if period.start.tzinfo else period.start.replace(tzinfo=timezone.utc)
            end = period.end if period.end.tzinfo else period.end.replace(tzinfo=timezone.utc)
            if start <= dep <= end:
                multiplier *= period.multiplier
                break

        # 假日（週六=5、週日=6）
        if dep.weekday() in (5, 6):
            multiplier *= self.price_rules.holiday_multiplier

        # CHANGED: 早鳥用 timedelta 滿「整數天數」比較，不受 .days 向下取整影響
        now = datetime.now(timezone.utc)
        need_days = self.price_rules.early_bird_discount.days_in_advance
        if dep - now >= timedelta(days=need_days):
            multiplier *= self.price_rules.early_bird_discount.discount

        return base_price * multiplier

   
    @before_event([Insert, Replace])  # 新增/覆寫都會跑，確保更新時也重算
    async def fill_schedule_arrival_dates(self):
        if not self.schedules:
            return

        updated = []
        for s in self.schedules:
            # 確保 departure_date 是 UTC-aware（你的 service 已轉 UTC，這裡保險再正規化）
            dep = s.departure_date
            if isinstance(dep, datetime):
                dep = dep.replace(tzinfo=timezone.utc) if dep.tzinfo is None else dep.astimezone(timezone.utc)

            # 計算抵達時間（轉為 UTC）
            arr =  calculate_arrival_date(
                dep,
                self.route.flight_duration,
                self.route.departure_city,
                self.route.arrival_city,
            )

            if isinstance(arr, datetime):
                arr = arr.replace(tzinfo=timezone.utc) if arr.tzinfo is None else arr.astimezone(timezone.utc)

            updated.append(type(s)(
                departure_date=dep,
                arrival_date=arr,  # ← 覆寫為剛算出的值
                available_seats=s.available_seats,
                prices=s.prices,
            ))

        self.schedules = updated
