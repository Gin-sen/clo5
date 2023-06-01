import logging
from os import getenv
from typing import Any

from aio_pika import connect_robust
from fastapi.testclient import TestClient

from ..main import app, logstash_log
from starlette.datastructures import State

client = TestClient(app)
logger = logging.getLogger(__name__)


def override_logstash_log(log: Any):
    print(log)


app.dependency_overrides[logstash_log] = override_logstash_log


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Healthy"


def test_read_item_test():
    response = client.get("/itemstest/foo", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "title": "Foo",
        "description": "There goes my hero",
    }


def test_read_item_bad_token_test():
    response = client.get("/itemstest/foo", headers={"X-Token": "meh"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_read_inexistent_item_test():
    response = client.get("/itemstest/baz", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_create_item_test():
    response = client.post(
        "/itemstest/",
        headers={"X-Token": "coneofsilence"},
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }


def test_create_item_bad_token_test():
    response = client.post(
        "/itemstest/",
        headers={"X-Token": "meh"},
        json={"id": "bazz", "title": "Bazz", "description": "Drop the bazz"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_create_existing_item_test():
    response = client.post(
        "/itemstest/",
        headers={"X-Token": "coneofsilence"},
        json={
            "id": "foo",
            "title": "The Foo ID Stealers",
            "description": "There goes my stealer",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Item already exists"}
