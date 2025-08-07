from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
import secrets


class Payment(BaseModel):
    method: Literal['credit_card', 'paypal', 'bank_transfer', 'on_site_payment'] = 'on_site_payment'
    status: Literal['pending', 'paid', 'failed', 'refunded'] = 'pending'
    transaction_id: str = Field(default_factory=lambda: secrets.token_hex(16))


class Order(Document):
    user_id: PydanticObjectId
    hotel_id: PydanticObjectId
    room_id: PydanticObjectId
    check_in_date: datetime
    check_out_date: datetime
    total_price: float

    status: Literal['pending', 'confirmed', 'cancelled', 'completed'] = 'pending'
    payment: Payment = Field(default_factory=Payment)

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "orders"

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
