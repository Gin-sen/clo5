from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.hashed_password + "bob"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db, user, user_id):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()
    return db_user


# -------BOOKINGS-------#
def get_booking(db: Session, user_id: int, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == user_id).first()


def get_bookings(db: Session):
    return db.query(models.Booking).all()


def create_booking(db: Session, booking: schemas.BookingCreate, user_id: int):
    db_booking = models.Booking(**booking.dict(), user_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def delete_booking_for_user(db: Session, user_id: int, booking_id: int):
    db_booking = get_booking(db, user_id, booking_id)
    db.delete(db_booking)
    db.commit()
    return db_booking


def update_booking_for_user(db: Session, user_id: int, booking_id: int, booking: schemas.BookingUpdate):
    db_booking = get_booking(db, user_id, booking_id)
    update_data = booking.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# -------ADDITIONAL SERVICES-------#
def get_additional_services(db: Session):
    return db.query(models.AdditionalService)


def get_additional_service(db: Session, additional_service_id: int):
    return db.query(models.AdditionalService).filter(models.AdditionalService.id == additional_service_id).first()


def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()
