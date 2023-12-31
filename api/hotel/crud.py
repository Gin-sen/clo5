from sqlalchemy.orm import Session

from . import models, schemas

# -------HOTEL------- #
def get_hotel(db: Session, hotel_id: int):
    return db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()


def get_hotel_by_name(db: Session, name: str):
    return db.query(models.Hotel).filter(models.Hotel.name == name).first()


def get_hotels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hotel).offset(skip).limit(limit).all()


def create_hotel(db: Session, hotel: schemas.HotelCreate):
    db_hotel = models.Hotel(name=hotel.name, address=hotel.address)
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

    
def delete_hotel(db: Session, hotel_id: int):
    db_hotel = get_hotel(db, hotel_id)
    db.delete(db_hotel)
    db.commit()
    return db_hotel



def update_hotel(db: Session, hotel_id: int, hotel: schemas.HotelUpdate):
    db_hotel = get_hotel(db, hotel_id)
    update_data = hotel.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hotel, key, value)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel


# -------CATEGORY------- #
def get_category(db: Session, category_id: int):
    return db.query(models.CategoryRoom).filter(models.CategoryRoom.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(models.CategoryRoom).filter(models.CategoryRoom.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CategoryRoom).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryRoomCreate):
    db_category = models.CategoryRoom(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    db.delete(db_category)
    db.commit()
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryRoomUpdate):
    db_category = get_hotel(db, category_id)
    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


# -------ROOM------- #
def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()


def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()


def create_hotel_room(db: Session, room: schemas.RoomCreate, hotel_id: int):
    db_room = models.Room(**room.dict(), owner_id=hotel_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def delete_room(db: Session, room_id: int):
    db_room = get_room(db, room_id)
    db.delete(db_room)
    db.commit()


def update_room(db: Session, room_id: int, room: schemas.RoomUpdate):
    db_room = get_room(db, room_id)
    update_data = room.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room
