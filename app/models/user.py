from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., description="帳號", max_length=100)
    email: EmailStr
    password: str
    isAdmin: bool = True
    address: Optional[str] = None
    phoneNumber: Optional[str] = None
    realName: Optional[str] = None
    resetPasswordToken: Optional[str] = None
    resetPasswordExpires: Optional[datetime] = None

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
