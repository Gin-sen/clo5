from os import getenv
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

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

app = FastAPI()

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


@app.get("/bookings/", response_model=list[schemas.Booking])
def read_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_booking(db)
    return bookings