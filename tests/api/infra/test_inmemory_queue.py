import unittest
from app.infra.inmemory_queue import InMemoryQueue
from app.infra.models.enqueue_item import EnqueueItem
from app.constants import EventType
import time

class TestInMemoryQueue(unittest.TestCase):

    def setUp(self):
        self.q = InMemoryQueue()
        
    def test_enqueue_valid_item(self):
        item = EnqueueItem(
            event_id=1,
            event_type=EventType.USER_CREATED,
            data = {"name" : "some_name"},
            due_time=0.0,
            correlation_id="123",
            endpoint_url="foo.com",
            max_attempts=4,
        )

        self.q.enqueue(item, due_time=0.0)
        self.assertEqual(len(self.q) , 1)

    def test_dequeue_valid_items(self):
        item = EnqueueItem(
            event_id=1,
            event_type=EventType.USER_CREATED,
            data = {"name" : "some_name"},
            due_time=0.0,
            correlation_id="123",
            endpoint_url="foo.com",
            max_attempts=4,
        )
        item2 = EnqueueItem(
            event_id=1,
            event_type=EventType.USER_CREATED,
            data = {"name" : "some_name"},
            due_time=5.2,
            correlation_id="123",
            endpoint_url="foo.com",
            max_attempts=4,
        )

        self.q.enqueue(item, due_time=0.0)
        self.q.enqueue(item2, due_time=5.2)
        
        self.assertEqual(len(self.q), 2)

        dequeued_item = self.q.dequeue(time.monotonic())

        self.assertEqual(item, dequeued_item)
        self.assertEqual(dequeued_item.due_time, 0.0)
        self.assertEqual(len(self.q), 1)

    def test_dequeue_same_due_time_items(self):
        before = time.monotonic()
        item = EnqueueItem(
            event_id=1,
            event_type=EventType.USER_CREATED,
            data = {"name" : "some_name"},
            due_time=before,
            correlation_id="123",
            endpoint_url="foo.com",
            max_attempts=4,
        )
        item2 = EnqueueItem(
            event_id=1,
            event_type=EventType.USER_CREATED,
            data = {"name" : "some_name"},
            due_time=before,
            correlation_id="123",
            endpoint_url="foo.com",
            max_attempts=4,
        )
        

        self.q.enqueue(item, due_time=before)
        self.q.enqueue(item2, due_time=before)
        
        self.assertEqual(len(self.q), 2)

        dequeued_item = self.q.dequeue(time.monotonic())

        self.assertEqual(item, dequeued_item)
        self.assertEqual(dequeued_item.due_time, before)
        dequeued_item2 = self.q.dequeue(time.monotonic())
        self.assertEqual(item2, dequeued_item2)
        self.assertEqual(dequeued_item2.due_time, before)
    
    def test_queue_returns_empty(self):
        item = self.q.dequeue(time.monotonic())
        self.assertIsNone(item)


