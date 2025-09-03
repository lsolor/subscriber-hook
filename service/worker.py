import threading
import time
from collections import defaultdict
from infra.inmemory_queue import InMemoryQueue


class Worker:
    def __init__(
        self,
        queue: InMemoryQueue,
        config: dict,
        in_flight_cap: defaultdict,
        in_flight_set: set,
        delivered_set: set,
        dlq: list,
        metrics: dict,
        stop_event: threading.Event,
    ):
        self.queue = queue
        self.config = config
        self.in_flight_cap = in_flight_cap
        self.in_flight_set = in_flight_set
        self.delivered_set = delivered_set
        self.dlq = dlq
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
            # In an MVP, you can poll the queue periodically
            time.sleep(0.1)
