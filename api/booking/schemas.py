import datetime

from pydantic import BaseModel


# User class
class User:
    firstname = str
    lastname = str
    id = id
    age = int
    phone = int
    password = str
    email = str
    created_date = datetime
    update_date = datetime


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class HotelBase(BaseModel):
    name: str


class HotelCreate(HotelBase):
    address: str


class Hotel(HotelBase):
    id: int
    is_active: bool
    rooms: list[Room] = []

    class Config:
        orm_mode = True