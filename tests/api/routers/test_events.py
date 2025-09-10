from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.schemas.event import EventRequest, EventResponse
from api.routers.events import router
from main import app

client = TestClient(app)

# happy path: Post with a valid request 
def test_create_event_happy_path():
    # Arrange
    request = EventRequest(id=1, type="user.created", payload={"user_id": 123})

    # Act
    resp = client.post("/events", json=request)

    # Assert
    assert resp.status_code == 202
    body = resp.json()
    assert body["id"] == "1"
    assert body["status"] == "accepted"
    assert body["message"]
    
    corr = resp.headers.get("X-Correlation-Id")
    assert corr and isinstance(corr, str)

def test_create_event_happy_path_no_correlation_id():
    # Arrange
    request = EventRequest(id=1, type="user.created", payload={"user_id": 123})
    supplied = "1234"

    # Act
    resp = client.post("/events", json=request, headers={"X-Correlation-Id": supplied})

    # Assert
    assert resp.status_code == 202
    body = resp.json()
    assert body["id"] == "1"
    assert body["status"] == "accepted"
    assert body["message"]
    
    assert resp.headers.get("X-Correlation-Id") == supplied

def test_create_event_missing_required_field_returns_422():
    resp = client.post("/events", json={"type": "user.created", "payload": {}})

    assert resp.status_code == 422