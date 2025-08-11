from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
import secrets


class Payment(BaseModel):
    method: Literal['credit_card', 'paypal', 'bank_transfer', 'on_site_payment'] = Field(
        default='on_site_payment',
        alias="method"
    )
    status: Literal['pending', 'paid', 'failed', 'refunded'] = Field(
        default='pending',
        alias="status"
    )
    transaction_id: str = Field(
        default_factory=lambda: secrets.token_hex(16),
        alias="transactionId"
    )


class Order(Document):
    user_id: PydanticObjectId = Field(..., alias="userId")
    hotel_id: PydanticObjectId = Field(..., alias="hotelId")
    room_id: PydanticObjectId = Field(..., alias="roomId")
    check_in_date: datetime = Field(..., alias="checkInDate")
    check_out_date: datetime = Field(..., alias="checkOutDate")
    total_price: float = Field(..., alias="totalPrice")

    status: Literal['pending', 'confirmed', 'cancelled', 'completed'] = Field(default='pending', alias="status")
    payment: Payment = Field(default_factory=Payment, alias="payment")

    created_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "orders"

    class Config:
        allow_population_by_field_name = True

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
