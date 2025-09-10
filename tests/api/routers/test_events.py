from collections import defaultdict
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.infra.inmemory_queue import InMemoryQueue
from app.main import app
from app.constants import CORRELATION_HDR
from app.service.dispatcher import Dispatcher

client = TestClient(app)


class TestEventRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        q = InMemoryQueue()
        dispatcher = Dispatcher(
            queue=q, registry=defaultdict(list), metrics=defaultdict(int)
        )
        app.state.queue = q
        app.state.dispatcher = dispatcher

    def test_create_event_happy_path(self):
        # Arrange
        payload = {"id": "1", "type": "user.created", "data": {"user_id": 123}}

        # Act
        with self.assertLogs("app.api.routers.events", level="INFO") as cm:
            resp = self.client.post("/events/", json=payload)

        # Assert
        self.assertEqual(resp.status_code, 202)
        body = resp.json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["status"], "accepted")
        self.assertTrue(body["message"])

        corr = resp.headers.get(CORRELATION_HDR)
        self.assertIsNotNone(corr)
        self.assertIsInstance(corr, str)

        item = app.state.queue.items[0]
        self.assertEqual(item.event_id, 1)

        record = cm.records[0]
        record = cm.records[0]
        self.assertIn("event_received", record.msg)
        self.assertEqual(record.levelname, "INFO")
        self.assertEqual(record.event_id, 1)

    def test_create_event_happy_path_no_correlation_id(self):
        # Arrange
        payload = {"id": "1", "type": "user.created", "data": {"user_id": 123}}
        supplied = "1234"

        # Act
        with self.assertLogs("app.api.routers.events", level="INFO") as cm:
            resp = self.client.post(
                "/events/", json=payload, headers={CORRELATION_HDR: supplied}
            )

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

        item = app.state.queue.items[0]
        self.assertEqual(item.event_id, 1)

    def test_create_event_missing_required_field_returns_422(self):
        resp = self.client.post("/events/", json={"type": "user.created", "data": {}})

        self.assertEqual(resp.status_code, 422)
        self.assertEqual(len(app.state.queue), 0)

    def test_create_event_invalid_type_returns_422(self):
        resp = self.client.post("/events/", json={"id": "1", "type": "bad", "data": {}})

        self.assertEqual(resp.status_code, 422)

    def test_create_event_missing_data_returns_422(self):
        resp = self.client.post("/events/", json={"id": "1", "type": "user.created"})

        self.assertEqual(resp.status_code, 422)

    @patch(
        "app.service.dispatcher.Dispatcher.enqueue",
        side_effect=TimeoutError("Queue full"),
    )
    def test_create_event_dispatcher_raises_timeout_returns_503(self, mock_enqueue):
        # Arrange
        payload = {"id": "1", "type": "user.created", "data": {"user_id": 123}}
        # Act
        with self.assertLogs("app.api.routers.events", level="ERROR") as cm:
            resp = self.client.post("/events/", json=payload)

        # Assert
        self.assertEqual(resp.status_code, 503)
        self.assertIn("enqueue_timeout", cm.output[0])
        self.assertEqual(len(app.state.queue), 0)
        mock_enqueue.assert_called_once()

    @patch(
        "app.service.dispatcher.Dispatcher.enqueue",
        side_effect=Exception("Unexpected error"),
    )
    def test_create_event_dispatcher_raises_exception_returns_500(self, mock_enqueue):
        # Arrange
        payload = {"id": "1", "type": "user.created", "data": {"user_id": 123}}
        # Act
        with self.assertLogs("app.api.routers.events", level="ERROR") as cm:
            resp = self.client.post("/events/", json=payload)

        # Assert
        self.assertEqual(resp.status_code, 500)
        self.assertIn("enqueue_error", cm.output[0])
        self.assertEqual(len(app.state.queue), 0)
        mock_enqueue.assert_called_once()
