from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    isAdmin: bool = False
    address: Optional[str] = None
    phoneNumber: Optional[str] = None
    realName: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    account: str
    password: str

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserOut(UserBase):
    id: str = Field(alias="_id")