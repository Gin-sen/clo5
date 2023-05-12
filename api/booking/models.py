from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base


booking_service = Table('booking_service', Base.metadata,
    Column('booking_id', Integer, ForeignKey('bookings.id')),
    Column('additional_service_id', Integer, ForeignKey('additionalServices.id'))
)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users_name = Column(String, unique=True, index=True)
    reservation_number = Column(Integer, index=True)
    numbers_people = Column(Integer, index=True)
    nights = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    payment_id = Column(Integer, ForeignKey("payment.id"))
    additional_service = relationship("AdditionalService", secondary=booking_service, back_populates="booking")
    owner = relationship("User", back_populates="bookings")
    payment = relationship("Payment", primaryjoin="Booking.payment_id == Payment.id")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    lastname = Column(String, index=True)
    firstname = Column(String, index=True)
    age = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    bookings = relationship("Booking", back_populates="owner")


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Integer, index=True)


class AdditionalService(Base):
    __tablename__ = "additionalServices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Integer, index=True)

    booking = relationship("Booking", secondary=booking_service, back_populates="additional_service")
