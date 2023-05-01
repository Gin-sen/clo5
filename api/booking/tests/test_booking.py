from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

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


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_hotel():
    response = client.post(
        "/bookings/",
        json={"name": "deadpool@example.com", "address": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "deadpool@example.com"
    assert "id" in data
    booking_id = data["id"]

    response = client.get(f"/bookings/{booking_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "deadpool@example.com"
    assert data["id"] == booking_id