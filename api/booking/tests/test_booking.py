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
    global db
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "bobby@test.com", "hashed_password": "test", "firstname": "bobby", "lastname": "bobby"
            , "age": 1, "phone": 4004040404
              },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "bobby@test.com"
    assert data["hashed_password"] == "testbob"
    assert data["firstname"] == "bobby"
    assert data["lastname"] == "bobby"
    assert data["age"] == 1
    assert data["phone"] == 4004040404
    assert "id" in data
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "bobby@test.com"
    assert data["hashed_password"] == "testbob"
    assert data["firstname"] == "bobby"
    assert data["lastname"] == "bobby"
    assert data["age"] == 1
    assert data["phone"] == 4004040404
    assert data["id"] == user_id


def test_create_booking():
    response = client.post(
        "/users/1/bookings/",
        json={"nights": 2, "numbers_people": 2, "users_name": "bobby",
              "additional_service_ids": []},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nights"] == 2
    assert data["numbers_people"] == 2
    assert data["user_id"] == 1
    assert data["users_name"] == "bobby"
    assert "id" in data
    booking_id = data["id"]
    user_id = data["user_id"]

    response = client.get(f"users/{user_id}/bookings/{booking_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nights"] == 2
    assert data["numbers_people"] == 2
    assert data["user_id"] == 1
    assert data["users_name"] == "bobby"
    assert data["id"] == booking_id


def test_create_additional_services():
    response = client.post(
        "/additional_services/",
        json={"name": "piscine", "price": 20},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "piscine"
    assert data["price"] == 20
    assert "id" in data
    additional_service_id = data["id"]

    response = client.get(f"/additional_services/{additional_service_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "piscine"
    assert data["price"] == 20
    assert data["id"] == additional_service_id
