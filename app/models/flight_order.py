from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from beanie import Document, Indexed, PydanticObjectId


class PassengerInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., alias="name")
    gender: Literal[0, 1] = Field(..., alias="gender")  # 0: 女, 1: 男
    birth_date: datetime = Field(..., alias="birthDate")
    passport_number: str = Field(..., alias="passportNumber")
    email: str = Field(..., alias="email")


class PriceInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    base_price: float = Field(..., alias="basePrice")
    tax: float = Field(..., alias="tax")
    total_price: float = Field(..., alias="totalPrice")


class PaymentInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    method: Optional[str] = Field(None, alias="method")
    transaction_id: Optional[str] = Field(None, alias="transactionId")
    paid_at: Optional[datetime] = Field(None, alias="paidAt")


class FlightOrder(Document):
    model_config = ConfigDict(populate_by_name=True)
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

    created_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "flight_orders"

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
