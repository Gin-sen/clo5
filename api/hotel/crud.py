from sqlalchemy.orm import Session

from . import models, schemas


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


def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()


def create_hotel_room(db: Session, room: schemas.RoomCreate, hotel_id: int):
    db_room = models.Room(**room.dict(), owner_id=hotel_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room