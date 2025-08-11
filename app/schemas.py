from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: Optional[str] = "client"


class UserResponse(UserBase):
    id: int
    role: str

    model_config = ConfigDict(from_attributes=True)


class FoodBagOwner(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class FoodBagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float                     # добавлено поле price (без скидки)
    discounted_price: float
    quantity: int
    address: str
    pickup_time: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodBagResponse(FoodBagCreate):
    id: int
    owner: FoodBagOwner
    photo_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    food_bag_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BookingCreate):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
