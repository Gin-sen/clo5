from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()


def get_additional_service(db: Session, additional_service_id: int):
    return db.query(models.AdditionalService).filter(models.AdditionalService.id == additional_service_id).first()


def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()


def get_additional_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AdditionalService).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.hashed_password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_booking(db: Session, booking: schemas.BookingCreate, user_id: int):
    db_booking = models.Booking(**booking.dict(), owner_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(price=payment.price, total=payment.total)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def create_service(db: Session, service: schemas.ServicesCreate):
    db_service = models.AdditionalService(name=service.name, price=service.price)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service
