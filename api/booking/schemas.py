from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ServicesBase(BaseModel):
    name: str
    price: str | None = None


class ServicesCreate(ServicesBase):
    pass


class Services(ServicesBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class BookingBase(BaseModel):
    name: str
    nights: int
    users_name: str
    numbers_people: int


class BookingCreate(BookingBase):
    pass


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
