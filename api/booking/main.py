from __future__ import annotations

from random import randint

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


class ItemTest(BaseModel):
    id: str
    title: str
    description: str | None = None


fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero", "is_active": True, "booking.owner_id": 1},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders", "is_active": True, "booking.owner_id": 1}

}

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return "Healthy booking"


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = crud.update_user(db, user=user, user_id=user_id)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user_id=user_id)
    return {"message": "User deleted successfully"}


@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/bookings/", response_model=schemas.Booking)
def create_booking_for_user(user_id: int, booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_booking = crud.create_booking(db=db, booking=booking, user_id=user_id)
    db.refresh(db_booking)
    db_booking.reservation_number = randint(1, 999999)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@app.get("/bookings/", response_model=list[schemas.Booking])
def read_hotels(db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db)
    return bookings


# FIXME
@app.get("/users/{user_id}/bookings/{booking_id}", response_model=list[schemas.Booking])
def read_booking_user(user_id: int, booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db, user_id=user_id, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking



@app.put("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def update_booking_for_user(user_id: int, booking_id: int, booking: schemas.BookingUpdate,
                            db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db, user_id=user_id, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    db_booking = crud.update_booking_for_user(db=db, booking=booking, user_id=user_id, booking_id=booking_id)
    return db_booking


@app.delete("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def delete_booking_for_user(user_id: int, booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db=db, user_id=user_id, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.user_id != user_id:
        raise HTTPException(status_code=400, detail="This booking doesnt match with this user")
    return crud.delete_booking_for_user(db=db, booking_id=booking_id, user_id=user_id)
