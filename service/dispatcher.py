# thin service api used by the router to push deliveries to the queue
from api.schemas.event import EventRequest


class Dispatcher:
    def __init__(self, queue, registry, metrics):
        self.queue = queue
        self.registry = registry
        self.metrics = metrics

    def enqueue_item(self, item: EventRequest):
        # logic to enqueue item
        self.queue.enqueue(item)
        self.metrics["events_received"] += 1
        print(f"Enqueued item: {item.event_type} to {item.endpoint_url}")