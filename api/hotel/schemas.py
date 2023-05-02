from pydantic import BaseModel


class RoomBase(BaseModel):
    title: str
    description: str | None = None


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
