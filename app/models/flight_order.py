from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from beanie import Document, Indexed, PydanticObjectId


class PassengerInfo(BaseModel):
    name: str = Field(..., alias="name")
    gender: Literal[0, 1] = Field(..., alias="gender")  # 0: 女, 1: 男
    birth_date: datetime = Field(..., alias="birthDate")
    passport_number: str = Field(..., alias="passportNumber")
    email: str = Field(..., alias="email")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class PriceInfo(BaseModel):
    base_price: float = Field(..., alias="basePrice")
    tax: float = Field(..., alias="tax")
    total_price: float = Field(..., alias="totalPrice")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class PaymentInfo(BaseModel):
    method: Optional[str] = Field(None, alias="method")
    transaction_id: Optional[str] = Field(None, alias="transactionId")
    paid_at: Optional[datetime] = Field(None, alias="paidAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class FlightOrder(Document):
    user_id: PydanticObjectId = Field(..., alias="userId")
    flight_id: PydanticObjectId = Field(..., alias="flightId")
    order_number: str = Field(..., alias="orderNumber")
    passenger_info: List[PassengerInfo] = Field(..., alias="passengerInfo")
    category: Literal["ECONOMY", "BUSINESS", "FIRST"] = Field(..., alias="category")
    schedule_id: PydanticObjectId = Field(..., alias="scheduleId")
    price: PriceInfo = Field(..., alias="price")
    status: Literal["PENDING", "PAID", "CANCELLED", "COMPLETED"] = Field(
        default="PENDING", alias="status"
    )
    payment_info: Optional[PaymentInfo] = Field(None, alias="paymentInfo")

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Settings:
        name = "flight_orders"

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
