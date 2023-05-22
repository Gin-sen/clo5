from pydantic import BaseModel


class RoomBase(BaseModel):
    title: str
    description: str | None = None
    category_id: int


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class CategoryRoomBase(BaseModel):
    name: str
    description: str | None = None


class CategoryRoomCreate(CategoryRoomBase):
    pass


class CategoryRoom(CategoryRoomBase):
    id: int
    rooms: list[Room] = []

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
