from functools import lru_cache
from os import getenv
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

import influx_logger
import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


class ItemTest(BaseModel):
    id: str
    title: str
    description: str | None = None


fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

influx_url = getenv("INFLUX_URL", "http://influxdb.example.local")
influx_organization = getenv("INFLUX_ORGANIZATION", "influxdata")
influx_token = getenv("INFLUX_TOKEN", "BobbyGetToken")
influx_bucket = getenv("INFLUX_BUCKET", "hotel-api")

app = FastAPI()


# @lru_cache
# def influx_logger():
#     return influx_logger.InfluxLogger(url=influx_url, organization=influx_organization, token=influx_token, bucket=influx_bucket)

ilogger = influx_logger.InfluxLogger(
    url=influx_url,
    organization=influx_organization,
    token=influx_token,
    bucket=influx_bucket)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return "Healthy"


@app.get("/itemstest/{item_id}", response_model=ItemTest)
async def read_main(item_id: str,
                    x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Invalid X-Token header"}})
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "INFO"},
                     "fields": {"status_code": 404, "detail": "Item not found"}})
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/itemstest/", response_model=ItemTest)
async def create_item(item: ItemTest,
                      x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Invalid X-Token header"}})
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "ERROR"},
                     "fields": {"status_code": 400, "detail": "Item already exists"}})
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item


@app.post("/hotels/", response_model=schemas.Hotel)
def create_hotel(hotel: schemas.HotelCreate, db: Session = Depends(get_db)):
    db_hotel = crud.get_hotel_by_name(db, name=hotel.name)
    if db_hotel:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Hotel already registered"}})
        raise HTTPException(status_code=400, detail="Hotel already registered")
    return crud.create_hotel(db=db, hotel=hotel)


@app.get("/hotels/", response_model=list[schemas.Hotel])
def read_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hotels = crud.get_hotels(db, skip=skip, limit=limit)
    return hotels


@app.get("/hotels/{hotel_id}", response_model=schemas.Hotel)
def read_hotel(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = crud.get_hotel(db, hotel_id=hotel_id)
    if db_hotel is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Hotel not found"}})
        raise HTTPException(status_code=404, detail="Hotel not found")
    return db_hotel


@app.post("/categories/", response_model=schemas.CategoryRoom)
def create_category(category: schemas.CategoryRoomCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Category already registered"}})
        raise HTTPException(status_code=400, detail="Category already registered")
    return crud.create_category(db=db, category=category)


@app.get("/categories/", response_model=list[schemas.CategoryRoom])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@app.get("/categories/{category_id}", response_model=schemas.CategoryRoom)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Category not found"}})
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.post("/hotels/{hotel_id}/rooms/", response_model=schemas.Room)
def create_room_for_hotel(
        hotel_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)
):
    return crud.create_hotel_room(db=db, room=room, hotel_id=hotel_id)


@app.get("/rooms/", response_model=list[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms
