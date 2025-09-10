import unittest
from fastapi.testclient import TestClient
from app.api.schemas.event import EventRequest, EventResponse
from app.main import app
from app.constants import CORRELATION_HDR

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
        with self.assertLogs("app.api.routers.events", level="INFO") as cm:
            resp = self.client.post("/events", json=payload)

        # Assert
        self.assertEqual(resp.status_code, 202)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], "accepted")
        self.assertTrue(body["message"])

        corr = resp.headers.get(CORRELATION_HDR)
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
        with self.assertLogs("app.api.routers.events", level="INFO") as cm:
            resp = self.client.post("/events", json=payload, headers={"X-Correlation-Id": supplied})

        # Assert
        self.assertEqual(resp.status_code, 202)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], "accepted")
        self.assertTrue(body["message"])
        self.assertEqual(resp.headers.get(CORRELATION_HDR), supplied)

        record = cm.records[0]
        self.assertIn("event_received", record.msg)
        self.assertEqual(record.levelname, "INFO")
        self.assertEqual(record.correlation_id, supplied)
        self.assertEqual(record.event_id, 1)

    def test_create_event_missing_required_field_returns_422(self):
        resp = self.client.post("/events", json={"type": "user.created", "payload": {}})

        self.assertEqual(resp.status_code, 422)

    def test_create_event_invalid_type_returns_422(self):
        resp = self.client.post("/events", json={"id": "1", "type": "bad", "payload": {}})

        self.assertEqual(resp.status_code, 422)

    def test_create_event_missing_payload_returns_422(self):
        resp = self.client.post("/events", json={"id": "1", "type": "user.created"})

        self.assertEqual(resp.status_code, 422)