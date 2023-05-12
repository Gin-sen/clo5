from __future__ import annotations

from random import randint

from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


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


def check_user(db, user_id):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")


def check_booking(booking_id, db, user_id):
    db_booking = crud.get_booking(db, user_id=user_id, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")


def check_service(db, additional_service_id):
    additional_service = crud.get_additional_service(db, additional_service_id=additional_service_id)
    if additional_service is None:
        raise HTTPException(status_code=404, detail="Additional service not found")


def check_payment(db, booking_id):
    payment = crud.get_payment(db, booking_id=booking_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    check_user(db, user_id)
    my_user = crud.update_user(db, user=user, user_id=user_id)
    return my_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    check_user(db, user_id)
    return crud.delete_user(db, user_id=user_id)


@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    check_user(db, user_id)
    user = crud.get_user(db, user_id=user_id)
    return user


@app.post("/users/{user_id}/bookings/", response_model=schemas.Booking)
def create_booking_for_user(user_id: int, booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    check_user(db, user_id)
    db_booking = crud.create_booking(db=db, booking=booking, user_id=user_id)
    db.refresh(db_booking)
    db_booking.reservation_number = randint(1, 999999)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@app.get("/bookings/", response_model=list[schemas.Booking])
def get_bookings(db: Session = Depends(get_db)):
    return crud.get_bookings(db)


@app.get("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def read_booking_user(user_id: int, booking_id: int, db: Session = Depends(get_db)):
    check_booking(booking_id, db, user_id)
    booking = crud.get_booking(db, user_id=user_id, booking_id=booking_id)
    return booking


@app.put("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def update_booking_for_user(user_id: int, booking_id: int, booking: schemas.BookingUpdate,
                            db: Session = Depends(get_db)):
    check_booking(booking_id, db, user_id)
    booking = crud.update_booking_for_user(db=db, booking=booking, user_id=user_id, booking_id=booking_id)
    return booking


@app.put("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def bound_booking_and_service(user_id: int, booking_id: int, booking: schemas.BoundBookingAndServices,
                              db: Session = Depends(get_db)):
    check_booking(booking_id, db, user_id)
    booking = crud.bound_booking_and_service(db=db, booking=booking, user_id=user_id, booking_id=booking_id)
    return booking


@app.delete("/users/{user_id}/bookings/{booking_id}", response_model=schemas.Booking)
def delete_booking_for_user(user_id: int, booking_id: int, db: Session = Depends(get_db)):
    check_booking(booking_id, db, user_id)
    if crud.get_booking(db=db, user_id=user_id, booking_id=booking_id).user_id != user_id:
        raise HTTPException(status_code=400, detail="This booking doesnt match with this user")
    return crud.delete_booking_for_user(db=db, booking_id=booking_id, user_id=user_id)


# -------ADDITIONAL SERVICES-------#

@app.get("/additional_services/", response_model=list[schemas.Services])
def read_additional_services(db: Session = Depends(get_db)):
    return crud.get_additional_services(db)


@app.get("/additional_services/{additional_service_id}", response_model=schemas.Services)
def read_additional_service(additional_service_id: int, db: Session = Depends(get_db)):
    check_service(db, additional_service_id)
    additional_service = crud.get_additional_service(db, additional_service_id=additional_service_id)
    return additional_service


@app.post("/additional_services/", response_model=schemas.Services)
def create_additional_service(service: schemas.ServicesCreate, db: Session = Depends(get_db)):
    return crud.create_additional_service(db=db, service=service)


@app.put("/additional_services/{additional_service_id}", response_model=schemas.Services)
def update_additional_service(additional_service_id: int, additional_service: schemas.ServiceUpdate,
                              db: Session = Depends(get_db)):
    check_service(db, additional_service_id)
    my_additional_service = crud.update_additional_service(db, additional_service_id=additional_service_id,
                                                           additional_service=additional_service)
    return my_additional_service


@app.delete("/additional_services/{additional_service_id}")
def delete_additional_service(additional_service_id: int, db: Session = Depends(get_db)):
    check_service(db, additional_service_id)
    return crud.delete_additional_service(db, additional_service_id=additional_service_id)


# -------PAYMENT-------#

@app.get("/bookings/{booking_id}/payment/", response_model=schemas.Payment)
def read_payment(booking_id: int, db: Session = Depends(get_db)):
    check_payment(db, booking_id)
    payment = crud.get_payment(db, booking_id=booking_id)
    return payment


# @app.post("/bookings/{booking_id}/payment/", response_model=schemas.Payment)
# def create_payment_for_user(user_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
#     check_user(db, user_id)
#     db_payment = crud.create_payment(db=db, payment=payment, user_id=user_id)
#     db.refresh(db_payment)
#     db.commit()
#     db.refresh(db_payment)
#     return db_payment
