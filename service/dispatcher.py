# thin service api used by the router to push deliveries to the queue
from api.schemas.event import EventRequest
from infra.models.enqueue_item import EnqueueItem


class Dispatcher:
    def __init__(self, queue, registry, metrics):
        self.queue = queue
        self.registry = registry
        self.metrics = metrics

    def enqueue_item(self, event: EventRequest):
        # logic to enqueue item
        # Make a delivery item for each endpoint in the registry for the event type
        endpoints = self.registry.get(event.event_type, [])
        for endpoint in endpoints:
            enqueue_item = EnqueueItem(
                event_id=event.id,
                event_type=event.event_type,
                data=event.data,
                due_time=now(),  # immediate
                correlation_id=event.correlation_id,
                endpoint_url=endpoint
            )
            self.queue.enqueue(enqueue_item)
        self.metrics["events_received"] += 1
        print(f"Enqueued item: {event.event_type} to {len(endpoints)} endpoints.")