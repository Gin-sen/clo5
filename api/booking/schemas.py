from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServicesBase(BaseModel):
    name: str
    price: str | None = None


class ServicesCreate(ServicesBase):
    pass


class Services(BaseModel):
    id: int
    name: str
    price: float


class BookingBase(BaseModel):
    nights: int
    numbers_people: int
    # additional_services_id: Services.id\\\\


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    nights: int
    numbers_people: int


class BookingDelete(BaseModel):
    id: int


class Booking(BookingBase):
    id: int
    user_id: int
    reservation_number: int
    services: list[Services] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(UserBase):
    id: int
    hashed_password: Optional[str] = None


class UserDelete(BaseModel):
    id: int


class User(UserBase):
    id: int
    firstname = str
    lastname = str
    age = int
    phone = int
    hashed_password: str
    created_date = datetime
    update_date = datetime
    # is_active: bool
    bookings: list[Booking] = []

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    price: int
    total: int


class PaymentCreate(PaymentBase):
    pass


class Payment(PaymentBase):
    id: int

    class Config:
        orm_mode = True
