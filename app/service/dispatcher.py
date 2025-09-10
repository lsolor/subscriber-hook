# thin service api used by the router to push deliveries to the queue
import logging
import time
from app.api.schemas.event import EventRequest
from app.infra.inmemory_queue import InMemoryQueue
from app.infra.models.enqueue_item import EnqueueItem

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, queue: InMemoryQueue, registry, metrics):
        self.queue = queue
        # self.registry = registry
        # self.metrics = metrics

    def enqueue(self, event: EventRequest, correlation_id: str) -> None:
        # logic to enqueue item
        # Make a delivery item for each endpoint in the registry for the event type
        # endpoints = self.registry.get(event.type, [])
        # for endpoint in endpoints:
        #     enqueue_item = EnqueueItem(
        #         event_id=event.id,
        #         event_type=event.type,
        #         data=event.data,
        #         due_time= time.monotonic(),  # immediate delivery
        #         correlation_id=event.correlation_id,
        #         endpoint_url=endpoint,
        #         max_attempts=4
        #     )
        #     self.queue.enqueue(enqueue_item)
        placeholder = "example.com"
        enqueue_item = EnqueueItem(
            event_id=event.id,
            event_type=event.type,
            data=event.data,
            due_time=time.monotonic(),  # immediate delivery
            correlation_id=correlation_id,
            endpoint_url=placeholder,  # placeholder, in real use would come from registry
            max_attempts=4,
        )
        self.queue.enqueue(enqueue_item)
        # self.metrics["events_received"] += 1
        logger.info(
            f"Enqueued item: {event.type} for endpoint {placeholder} at {enqueue_item.due_time}"
        )
