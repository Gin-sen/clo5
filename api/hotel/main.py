import json
import logging
from os import getenv
from typing import Annotated, Any
from fastapi import Depends, FastAPI, Header, HTTPException
from starlette.datastructures import State

from pydantic import BaseModel
from sqlalchemy.orm import Session
from aio_pika import connect_robust, Message, DeliveryMode

from utils.main import InfluxLogger
import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
logger = logging.getLogger(__name__)

class ItemTest(BaseModel):
    id: str
    title: str
    description: str | None = None


fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

rabbit_host = getenv("RABBIT_HOST", "rabbitmq")
rabbit_port = getenv("RABBIT_PORT", 5672)
rabbit_user = getenv("RABBIT_USER", "user")
rabbit_pass = getenv("RABBIT_PASS", "password")
rabbit_vhost = getenv("RABBIT_VHOST",  "my_vhost")

influx_url = getenv("INFLUX_URL", "http://influxdb.example.local")
influx_organization = getenv("INFLUX_ORGANIZATION", "influxdata")
influx_token = getenv("INFLUX_TOKEN", "BobbyGetToken")
influx_bucket = getenv("INFLUX_BUCKET", "hotel-api")

app = FastAPI()


ilogger = InfluxLogger(
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


async def logstash_log(log: Any):
    message = Message(
        json.dumps(log, ensure_ascii=False).encode('utf-8'),
        delivery_mode=DeliveryMode.PERSISTENT
    )
    await app.state.channel.default_exchange.publish(
        message, routing_key="logstash"
    )

@app.get("/")
async def health_check():
    await logstash_log({"status": "Healthy"})
    return "Healthy"


@app.on_event('startup')
async def startup():
    """
    Executes on application startup.

    Connects to RabbitMQ HOST and to the channel QUEUE_NAME.
    """
    app.state.connection = await connect_robust(
        host=rabbit_host,
        port=rabbit_port,
        virtualhost=rabbit_vhost,
        login=rabbit_user,
        password=rabbit_pass,
        connection_attempts=5,
        retry_delay=10,
    )
    app.state.channel = await app.state.connection.channel()
    logger.info(f'Connected pika producer to {rabbit_host}')

    await app.state.channel.declare_queue("logstash", durable=True)


@app.on_event('startup')
async def startup():
    """
    Executes on application startup.

    Connects to RabbitMQ HOST and to the channel QUEUE_NAME.
    """
    app.state.connection = await connect_robust(
        host=rabbit_host,
        port=rabbit_port,
        virtualhost=rabbit_vhost,
        login=rabbit_user,
        password=rabbit_pass,
        connection_attempts=5,
        retry_delay=10,
    )
    app.state.channel = await app.state.connection.channel()
    logger.info(f'Connected pika producer to {rabbit_host}')

    await app.state.channel.declare_queue("logstash", durable=True)


@app.on_event('shutdown')
async def shutdown():
    """
    Executes on application shutdown.

    Disconnects from RabbitMQ HOST.
    """
    if not app.state.channel.is_closed:
        await app.state.channel.close()
        logger.debug('channel closed')
    if not app.state.connection.is_closed:
        await app.state.connection.close()
        logger.debug('connection closed')


@app.get("/itemstest/{item_id}", response_model=ItemTest)
async def read_main(item_id: str,
                    x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        ex = HTTPException(status_code=400, detail="Invalid X-Token header")
        await logstash_log({"exception": {"status_code": ex.status_code, "detail": ex.detail}, "log_level": "WARN"})
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Invalid X-Token header"}})
        raise ex
    if item_id not in fake_db:
        ex = HTTPException(status_code=404, detail="Item not found")
        await logstash_log({"exception": {"status_code": ex.status_code, "detail": ex.detail}, "log_level": "INFO"})
        ilogger.log({"measurement": "exception", "tags": {"log_level": "INFO"},
                     "fields": {"status_code": 404, "detail": "Item not found"}})
        raise ex
    return fake_db[item_id]


@app.post("/itemstest/", response_model=ItemTest)
async def create_item(item: ItemTest,
                      x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        ex = HTTPException(status_code=400, detail="Invalid X-Token header")
        await logstash_log({"exception": {"status_code": ex.status_code, "detail": ex.detail}, "log_level": "WARN"})
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 400, "detail": "Invalid X-Token header"}})
        raise ex
    if item.id in fake_db:
        ex = HTTPException(status_code=400, detail="Item already exists")
        await logstash_log({"exception": {"status_code": ex.status_code, "detail": ex.detail}, "log_level": "ERROR"})
        ilogger.log({"measurement": "exception", "tags": {"log_level": "ERROR"},
                     "fields": {"status_code": 400, "detail": "Item already exists"}})
        raise ex
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
