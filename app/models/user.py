from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from beanie import Document


class User(Document):
    username: str = Field(..., unique=True)
    email: EmailStr = Field(..., unique=True)
    password: str  # hashed
    is_admin: bool = True

    address: Optional[str] = None
    phone_number: Optional[str] = None
    real_name: Optional[str] = None

    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None

    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()