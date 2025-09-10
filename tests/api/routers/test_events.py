import unittest
from fastapi.testclient import TestClient
from app.api.schemas.event import EventRequest, EventResponse
from app.main import app

client = TestClient(app)

class TestEventRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_create_event_happy_path(self):
        # Arrange
        payload = {
            "id": "1",
            "type": "user.created",
            "payload": {"user_id": 123}
        }

        # Act
        resp = self.client.post("/events", json=payload)

        # Assert
        self.assertEqual(resp.status_code, 202)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], "accepted")
        self.assertTrue(body["message"])
        
        corr = resp.headers.get("X-Correlation-Id")
        self.assertIsNotNone(corr)
        self.assertIsInstance(corr, str)

    def test_create_event_happy_path_no_correlation_id(self):
        # Arrange
        payload = {
            "id": "1",
            "type": "user.created",
            "payload": {"user_id": 123}
        }
        supplied = "1234"

        # Act
        resp = self.client.post("/events", json=payload, headers={"X-Correlation-Id": supplied})

        # Assert
        self.assertEqual(resp.status_code, 202)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], "accepted")
        self.assertTrue(body["message"])

        self.assertEqual(resp.headers.get("X-Correlation-Id"), supplied)

    def test_create_event_missing_required_field_returns_422(self):
        resp = self.client.post("/events", json={"type": "user.created", "payload": {}})

        self.assertEqual(resp.status_code, 422)