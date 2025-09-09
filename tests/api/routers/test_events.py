from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.schemas.event import EventRequest, EventResponse
from api.routers.events import router

# happy path: Post with a valid request 
def test_create_event_happy_path():
    # Arrange
    client = TestClient(router)
    request = EventRequest(id=1, type="user.created", payload={"user_id": 123})
    expected_response = EventResponse(id=1, status="created", correlation_id="some-correlation-id", message="Event has been accepted for processing")
    # Act
    response = client.post("/events", json=request.dict())

    # Assert
    assert response.status_code == 202
    assert response.json() == expected_response.dict()


def test_create_event_happy_path_no_correlation_id():
    # Arrange
    client = TestClient(router)
    request = EventRequest(id=1, type="user.created", payload={"user_id": 123})
    expected_response = EventResponse(id=1, status="created", correlation_id="some-correlation-id", message="Event has been accepted for processing")
    # Act
    response = client.post("/events", json=request.dict())

    # Assert
    assert response.status_code == 202
    assert response.json() == expected_response.dict()