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
    db_payment = create_payment(db=db, payment=schemas.PaymentCreate(price=42))
    db_booking = models.Booking(**booking.dict(exclude={'additional_service_ids'}), user_id=user_id, payment_id=db_payment.id)
    for additional_service_id in booking.additional_service_ids:
        additional_service = get_additional_service(db, additional_service_id)
        db_booking.additional_service.append(additional_service)
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


def bound_booking_and_service(db: Session, user_id: int, booking_id: int, booking: schemas.BoundBookingAndServices):
    db_booking = get_booking(db, user_id, booking_id)
    update_data = booking.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# -------ADDITIONAL SERVICES-------#
def get_additional_services(db: Session):
    return db.query(models.AdditionalService).all()


def get_additional_service(db: Session, additional_service_id: int):
    return db.query(models.AdditionalService).filter(models.AdditionalService.id == additional_service_id).first()


def create_additional_service(db: Session, service: schemas.ServicesCreate):
    db_service = models.AdditionalService(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def delete_additional_service(db: Session, additional_service_id: int):
    db_service = get_additional_service(db, additional_service_id)
    db.delete(db_service)
    db.commit()
    return db_service


def update_additional_service(db: Session, additional_service_id: int, additional_service: schemas.ServiceUpdate):
    db_service = get_additional_service(db, additional_service_id)
    update_data = additional_service.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)
    return db_service


# -------PAYMENT-------#

def get_payment(db: Session, booking_id: int):
    db_booking: models.Booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    return db_booking.payment


def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
