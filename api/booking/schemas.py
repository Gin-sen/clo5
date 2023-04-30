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


class Booking():
    id: int
    is_active: bool
    rooms: list = []

    class Config:
        orm_mode = True