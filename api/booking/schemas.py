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
    title: str


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    nights: int
    usernames: str
    people: int
    owner_id: int
    services: list[Services] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    firstname = str
    lastname = str
    age = int
    phone = int
    password = str
    created_date = datetime
    update_date = datetime
    # is_active: bool
    bookings: list[Booking] = []

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    price: int


class Payment(PaymentBase):
    id: int
    promo: bool | None
    total: int

    class Config:
        orm_mode = True
