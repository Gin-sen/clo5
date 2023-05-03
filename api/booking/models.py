from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    users_name = Column(String, unique=True, index=True)
    reservation_number = Column(Integer, index=True)
    numbers_people = Column(Integer, index=True)
    numbers_night = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    payment_id = Column(Integer, ForeignKey("payment.id"))

    additional_service_id = Column(Integer, ForeignKey('additionalServices.id'))
    additional_service = relationship("AdditionalService",
                                      primaryjoin="Booking.additional_service_id == AdditionalService.id")
    owner = relationship("User", back_populates="bookings")
    payment = relationship("Payment", back_populates="owner")




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, unique=True, index=True)
    first_name = Column(String, unique=True, index=True)
    age = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    bookings = relationship("Booking", back_populates="owner")


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Integer, unique=True, index=True)
    promo = Column(Integer, unique=True, index=True)
    total = Column(Integer, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Booking", back_populates="payment")


class AdditionalService(Base):
    __tablename__ = "additionalServices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Integer, unique=True, index=True)