from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    users_name = Column(String, unique=True, index=True)
    reservation_number = Column(Integer, index=True)
    numbers_people = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)

    users_id = relationship("User", back_populates="owner")
    payment = relationship("Payment", back_populates="owner")
    additional_services_id = relationship("AdditionalService", back_populates="owner")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, unique=True, index=True)
    first_name = Column(String, unique=True, index=True)
    age = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    bookings = relationship("User", back_populates="owner")


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(String, unique=True, index=True)
    promo = Column(String, unique=True, index=True)
    total = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class AdditionalService(Base):
    __tablename__ = "additionalService"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    booking = relationship("Booking", back_populates="owner")
