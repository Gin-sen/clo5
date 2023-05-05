from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServicesBase(BaseModel):
    name: str
    price: int


class ServicesCreate(ServicesBase):
    pass


class ServiceUpdate(ServicesBase):
    pass


class Services(ServicesBase):
    id: int

    class Config:
        orm_mode = True


class BookingBase(BaseModel):
    nights: int
    numbers_people: int
    users_name: str


class BookingCreate(BookingBase):
    additional_service_ids: list[int]


class BookingUpdate(BaseModel):
    nights: int
    numbers_people: int
    users_name: str


class BoundBookingAndServices(BookingBase):
    pass


class BookingDelete(BaseModel):
    id: int


class Booking(BookingBase):
    id: int
    user_id: int
    reservation_number: int
    additional_service: list[Services]
    # payment: Payment TODO

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(UserBase):
    hashed_password: Optional[str] = None
    firstname = str
    lastname = str
    age = int
    phone = int
    # update_date = datetime


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


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass


class Payment(PaymentBase):
    id: int

    class Config:
        orm_mode = True
