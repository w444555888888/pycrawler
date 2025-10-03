from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr, ConfigDict, Field
from beanie import Document


class User(Document):
    model_config = ConfigDict(populate_by_name=True)
    username: str = Field(..., alias="username", unique=True)
    email: EmailStr = Field(..., alias="email", unique=True)
    password: str = Field(..., alias="password")  # hashed password
    is_admin: bool = Field(default=True, alias="isAdmin")

    address: Optional[str] = Field(default=None, alias="address")
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    real_name: Optional[str] = Field(default=None, alias="realName")

    reset_password_token: Optional[str] = Field(default=None, alias="resetPasswordToken")
    reset_password_expires: Optional[datetime] = Field(default=None, alias="resetPasswordExpires")

    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "users"

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
