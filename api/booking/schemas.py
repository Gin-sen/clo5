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
    username: str
    peoples: int


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    owner_id: int
    reservation_number: int
    user: list[User] = []
    payment: list[Payment] = []
    services: list[Services] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    firstname = str
    lastname = str
    age = int
    phone = int
    password: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
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
