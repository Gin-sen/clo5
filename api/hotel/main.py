import json
import logging
from os import getenv
from typing import Any
from fastapi import Depends, FastAPI, HTTPException
from starlette.datastructures import State

from sqlalchemy import event
from sqlalchemy.orm import Session
from aio_pika import connect_robust, Message, DeliveryMode

from . import influx_logger, crud, models, schemas

from .database import SessionLocal, engine

INITIAL_DATA = {
    'hotels': [
        {
            'id': 51,
            'name': 'Bobby’s Hotel',
            'address': '7 rue du voisin',
            'is_activ': True
        },
        {
            'id': 52,
            'name': 'Randy’s Hotel',
            'address': '14 rue du Four',
            'is_activ': True
        }
    ],
    'categories': [
        {'id': 51, 'name': 'Suite présidentielle', 'description': 'jusqu\'a 5 personnes, tarif de 1000$'},
        {'id': 52, 'name': 'Suite', 'description': 'jusqu\'a 3 personnes, tarif de 720$'},
        {'id': 53, 'name': 'Junior suite', 'description': 'jusqu\'a 2 personnes, tarif de 500$'},
        {'id': 54, 'name': 'Chambre de luxe', 'description': 'jusqu\'a 2 personnes, tarif de 300$'},
        {'id': 55, 'name': 'Chambre standard', 'description': 'jusqu\'a 2 personnes, tarif de 150$'}
    ],
    'rooms': [
        {'id': 51, 'title': '101', 'description': 'la 101', 'owner_id': 51, 'category_id': 52},
        {'id': 52, 'title': '102', 'description': 'la 102', 'owner_id': 51, 'category_id': 53},
        {'id': 53, 'title': '103', 'description': 'la 103', 'owner_id': 51, 'category_id': 54},
        {'id': 54, 'title': '104', 'description': 'la 104', 'owner_id': 51, 'category_id': 55},
        {'id': 55, 'title': '105', 'description': 'la 105', 'owner_id': 51, 'category_id': 55},
        {'id': 56, 'title': '101', 'description': 'la 101', 'owner_id': 52, 'category_id': 51},
        {'id': 57, 'title': '102', 'description': 'la 102', 'owner_id': 52, 'category_id': 51}
    ]
}

logger = logging.getLogger(__name__)

is_tu = getenv("IS_TU", 'False').lower() in ('true', '1', 't')

rabbit_host = getenv("RABBIT_HOST", "rabbitmq")
rabbit_port = getenv("RABBIT_PORT", 5672)
rabbit_user = getenv("RABBIT_USER", "user")
rabbit_pass = getenv("RABBIT_PASS", "password")
rabbit_vhost = getenv("RABBIT_VHOST", "my_vhost")

influx_url = getenv("INFLUX_URL", "http://influxdb.example.local")
influx_organization = getenv("INFLUX_ORGANIZATION", "influxdata")
influx_token = getenv("INFLUX_TOKEN", "BobbyGetToken")
influx_bucket = getenv("INFLUX_BUCKET", "hotel-api")


def initialize_table(target, connection, **kw):
    tablename = str(target)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])


# set up of event before table creation
event.listen(models.Hotel.__table__, 'after_create', initialize_table)
event.listen(models.CategoryRoom.__table__, 'after_create', initialize_table)
event.listen(models.Room.__table__, 'after_create', initialize_table)

app = FastAPI()

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


def check_hotel(db, hotel_id):
    hotel = crud.get_hotel(db, hotel_id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")


def check_category(db, category_id):
    hotel = crud.get_category(db, category_id=category_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Category not found")


def check_room(db, room_id):
    room = crud.get_room(db, room_id=room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Category not found")


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
    if not is_tu:
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

    models.Base.metadata.create_all(bind=engine)


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


# -------HOTEL------- #
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


@app.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    check_hotel(db, hotel_id)
    return crud.delete_hotel(db, hotel_id=hotel_id)


@app.put("/hotel/{hotel_id}", response_model=schemas.Hotel)
def update_hotel(hotel_id: int, hotel: schemas.HotelUpdate, db: Session = Depends(get_db)):
    db_hotel = crud.get_hotel(db, hotel_id=hotel_id)
    if db_hotel is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Hotel not found"}})
        raise HTTPException(status_code=404, detail="Hotel not found")
    my_hotel = crud.update_hotel(db, hotel_id=hotel_id, hotel=hotel)
    return my_hotel


# -------CATEGORY------- #
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


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    check_category(db, category_id)
    return crud.delete_category(db, category_id=category_id)


@app.put("/categories/{category_id}", response_model=schemas.CategoryRoom)
def update_category(category_id: int, category: schemas.CategoryRoomUpdate, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Category not found"}})
        raise HTTPException(status_code=404, detail="Category not found")
    my_category = crud.update_category(db, category_id=category_id, category=category)
    return my_category


# -------ROOM------- #
@app.post("/hotels/{hotel_id}/rooms/", response_model=schemas.Room)
def create_room_for_hotel(
        hotel_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)
):
    return crud.create_hotel_room(db=db, room=room, hotel_id=hotel_id)


@app.get("/rooms/", response_model=list[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    check_room(db, room_id)
    return crud.delete_room(db, room_id=room_id)


@app.put("/hotels/{hotel_id}/rooms/{room_id}", response_model=schemas.Room)
def update_room_for_hotel(hotel_id: int, room_id: int, room: schemas.RoomUpdate, db: Session = Depends(get_db)):
    db_hotel = crud.get_hotel(db, hotel_id=hotel_id)
    if db_hotel is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Hotel not found"}})
        raise HTTPException(status_code=404, detail="Hotel not found")
    db_room = crud.get_room(db, room_id=room_id)
    if db_room is None:
        ilogger.log({"measurement": "exception", "tags": {"log_level": "WARN"},
                     "fields": {"status_code": 404, "detail": "Room not found"}})
        raise HTTPException(status_code=404, detail="Room not found")
    my_room = crud.update_room(db, room_id=room_id, room=room)
    return my_room
