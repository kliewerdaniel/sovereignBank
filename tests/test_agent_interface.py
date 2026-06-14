"""Tests for the FastAPI agent interface."""

import pytest
from fastapi.testclient import TestClient

from sovereign_memory_bank.api.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_list_memory(client):
    response = client.get("/api/memory/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_get_memory(client):
    # Create
    create_response = client.post(
        "/api/memory/",
        json={
            "type": "concept",
            "title": "Test Concept via API",
            "description": "Created through the API",
            "confidence": 0.75,
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    obj_id = created["id"]

    # Get
    get_response = client.get(f"/api/memory/{obj_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test Concept via API"


def test_create_and_delete_memory(client):
    create_response = client.post(
        "/api/memory/",
        json={"type": "claim", "title": "To Be Deleted"},
    )
    obj_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/memory/{obj_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/api/memory/{obj_id}")
    assert get_response.status_code == 404


def test_update_memory(client):
    create_response = client.post(
        "/api/memory/",
        json={"type": "concept", "title": "Original Title"},
    )
    obj_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/memory/{obj_id}",
        json={"title": "Updated Title", "confidence": 0.9},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"


def test_graph_stats(client):
    response = client.get("/api/graph/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "total_edges" in data
