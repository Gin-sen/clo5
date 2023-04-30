from os import getenv
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}

db_host = getenv("DB_HOST", "locahlost")
db_port = getenv("DB_PORT", "5432")
db_user = getenv("DB_USER", "Bobby")
db_pass = getenv("DB_PASS", "BR")
db_name = getenv("DB_NAME", "booking-db")

app = FastAPI()


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None


@app.get("/")
def health_check():
    return "Healthy"


@app.get("/items/{item_id}", response_model=Item)
async def read_main(item_id: str, x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@app.post("/items/", response_model=Item)
async def create_item(item: Item, x_token: Annotated[str | None, Header()] = None):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item.id] = item
    return item