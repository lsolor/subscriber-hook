import threading
import time
from collections import defaultdict
from app.infra.inmemory_queue import InMemoryQueue
from app.infra.models.enqueue_item import EnqueueItem
import requests
import logging
from fastapi import status

logger = logging.getLogger(__name__)

class Worker:
    def __init__(
        self,
        queue: InMemoryQueue,
        config: dict,
        # in_flight_cap: defaultdict,
        # in_flight_set: set,
        # delivered_set: set,
        dedup : dict,
        metrics: dict,
        stop_event: threading.Event,
    ):
        self.queue = queue
        self.config = config
        # self.in_flight_cap = in_flight_cap
        # self.in_flight_set = in_flight_set
        # self.delivered_set = delivered_set
        self.dedup = dedup
        self.metrics = metrics
        self.stop_event = stop_event
        self._thread: threading.Thread | None = None

    def start_background(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run(self):
        # Minimal loop placeholder; flesh out delivery handling later
        while not self.stop_event.is_set():
            now = time.monotonic()
            item = self.queue.dequeue(now)
            
            if not item: 
                logger.info("No item available for worker")
                continue

            if self.dedup[item.idempotent_key] in ("processed", "failed"):
                logger.info("already processed")            
            self.process(item, now)

    def process(self, item: EnqueueItem, now: float) -> None:

        resp = requests.post(item.endpoint_url, json=item.data)

        if resp.status_code == status.HTTP_202_ACCEPTED:
            self.dedup[item.idempotent_key] = "completed"
            self.metrics["success"] += 1 
            logger.info(f"{item.idempotent_key} succeeded")
        
        elif resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS or 500 <= resp.status_code < 600:
            if item.attempts + 1 < 4:
                logger.info(f"{item.idempotent_key} failed, but is retryable. recalculating retrying")
                self.metrics["retries"] += 1
                backoff = self.calc_backoff()
                item.attempts += 1
                self.queue.nack_requeue(item, now + backoff)
            
            else:
                logger.info(f"{item.idempotent_key} failed, and has hit max attempts")
                self.dedup[item.idempotent_key] = "failed"
                self.metrics["failure"] += 1
                self.dlq.append(item.idempotent_key)

        else:
            self.dedup[item.idempotent_key] = "failed"
            self.metrics["failure"] += 1
            self.dlq.append(item.idempotent_key)
    
    def calc_backoff(self, item: EnqueueItem):
        return 2.2



