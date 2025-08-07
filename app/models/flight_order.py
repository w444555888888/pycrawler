from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from beanie import Document, Indexed, PydanticObjectId


class PassengerInfo(BaseModel):
    name: str
    gender: Literal[0, 1]  # 0: 女, 1: 男
    birth_date: datetime
    passport_number: str
    email: str


class PriceInfo(BaseModel):
    base_price: float
    tax: float
    total_price: float


class PaymentInfo(BaseModel):
    method: Optional[str] = None
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None


class FlightOrder(Document):
    user_id: PydanticObjectId
    flight_id: PydanticObjectId
    order_number: Indexed(str, unique=True)

    passenger_info: List[PassengerInfo]
    category: Literal["ECONOMY", "BUSINESS", "FIRST"]
    schedule_id: PydanticObjectId

    price: PriceInfo
    status: Literal["PENDING", "PAID", "CANCELLED", "COMPLETED"] = "PENDING"
    payment_info: Optional[PaymentInfo] = None

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "flight_orders"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
