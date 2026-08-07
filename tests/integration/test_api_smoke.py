"""Integration smoke tests — API routes (requires fastapi)."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")

from sovereign.main import app  # noqa: E402


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index_banner(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["brand"] == "SOVEREIGN"


def test_task_submission(client):
    response = client.post(
        "/api/v1/tasks/",
        json={"type": "reason", "payload": {"input": "smoke"}, "priority": 5},
    )
    assert response.status_code == 200
    assert response.json()["type"] == "reason"


def test_system_info(client):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    assert response.json()["palette"]["cyan"] == "#00E5FF"
