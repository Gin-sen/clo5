from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db, logstash_log

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_logstash_log(log: Any):
    print(log)


app.dependency_overrides[logstash_log] = override_logstash_log
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_hotel():
    response = client.post(
        "/hotels/",
        json={"name": "deadpool@example.com", "address": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "deadpool@example.com"
    assert "id" in data
    hotel_id = data["id"]

    response = client.get(f"/hotels/{hotel_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "deadpool@example.com"
    assert data["id"] == hotel_id


def test_create_category():
    response = client.post(
        "/categories/",
        json={"name": "testcat", "description": "loremipsum"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "testcat"
    assert "id" in data
    category_id = data["id"]

    response = client.get(f"/categories/{category_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "testcat"
    assert data["id"] == category_id


def test_create_room():
    response = client.post(
        "/categories/",
        json={"name": "galdius", "description": "T-1000"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "galdius"
    assert "id" in data
    category_id = data["id"]

    response = client.post(
        "/hotels/1/rooms/",
        json={"title": "testcat", "description": "loremipsum", "category_id": category_id},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "testcat"
    assert "id" in data

