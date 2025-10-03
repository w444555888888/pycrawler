from datetime import datetime, timezone
from typing import Literal, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from beanie import Document, Link, PydanticObjectId
import secrets


if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.room  import Room

class Payment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
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
    model_config = ConfigDict(populate_by_name=True)
    # Node 是 ref User；通常不需要 populate 使用者，使用ID
    user_id: PydanticObjectId = Field(..., alias="userId")
    # 等同 Node 的 ref 'Hotel' / 'Room'
    hotel_id: Link["Hotel"] = Field(..., alias="hotelId")
    room_id:  Link["Room"]  = Field(..., alias="roomId")
    check_in_date: datetime = Field(..., alias="checkInDate")
    check_out_date: datetime = Field(..., alias="checkOutDate")
    total_price: float = Field(..., alias="totalPrice")

    status: Literal['pending', 'confirmed', 'cancelled', 'completed'] = Field(default='pending', alias="status")
    payment: Payment = Field(default_factory=Payment, alias="payment")

    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "orders"

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
