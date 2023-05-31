from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    rooms = relationship("Room", back_populates="owner")


class CategoryRoom(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

    rooms = relationship("Room", back_populates="category")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("hotels.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    owner = relationship("Hotel", back_populates="rooms")
    category = relationship("CategoryRoom", back_populates="rooms")
