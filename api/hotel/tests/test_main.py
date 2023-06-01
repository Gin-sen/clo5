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
