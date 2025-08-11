from typing import Optional, List, Literal
from pydantic import BaseModel, EmailStr, Field
from beanie import Document
from datetime import datetime, timezone


class Coordinates(BaseModel):
    latitude: float = Field(..., alias="latitude")
    longitude: float = Field(..., alias="longitude")


class Facilities(BaseModel):
    wifi: bool = Field(default=False, alias="wifi")
    parking: bool = Field(default=False, alias="parking")
    pool: bool = Field(default=False, alias="pool")
    gym: bool = Field(default=False, alias="gym")
    spa: bool = Field(default=False, alias="spa")
    restaurant: bool = Field(default=False, alias="restaurant")
    bar: bool = Field(default=False, alias="bar")


class Hotel(Document):
    name: str = Field(..., alias="name")
    type: Literal['hotel', 'apartment', 'guesthouse', 'villa', 'hostel', 'motel', 'capsule', 'resort'] = Field(..., alias="type")
    city: str = Field(..., alias="city")
    address: str = Field(..., alias="address")
    distance: Optional[str] = Field(default=None, alias="distance")
    photos: List[str] = Field(..., alias="photos")
    title: str = Field(..., alias="title")
    desc: str = Field(..., alias="desc")
    rating: Optional[float] = Field(default=None, ge=0, le=10, alias="rating")
    cheapest_price: float = Field(..., alias="cheapestPrice")
    popular_hotel: Optional[bool] = Field(default=False, alias="popularHotel")
    comments: Optional[int] = Field(default=0, alias="comments")
    facilities: Facilities = Field(default_factory=Facilities, alias="facilities")
    check_in_time: str = Field(..., alias="checkInTime")
    check_out_time: str = Field(..., alias="checkOutTime")
    coordinates: Coordinates = Field(..., alias="coordinates")
    email: EmailStr = Field(..., alias="email")
    nearby_attractions: List[str] = Field(..., alias="nearbyAttractions")
    phone: str = Field(..., alias="phone")

    created_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc), alias="updatedAt")

    class Settings:
        name = "hotels"

    class Config:
        allow_population_by_field_name = True  # 允許使用欄位名或 alias 存取

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)
