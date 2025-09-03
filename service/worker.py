# dequeue implementation, sends HTTP, classifies, schedules retries and moves to DLQ after meax attempts 

from collections import defaultdict
from anyio import current_time
from infra.inmemory_queue import InMemoryQueue
from service.dispatcher import enqueue_item

class Worker:
    def __init__(self, queue: InMemoryQueue, config: dict, in_flight_cap: defaultdict, in_flight_set: set, delivered_set: set, dlq: list, metrics: dict, stop_flag: bool):
        self.queue = queue
        self.config = config
        self.in_flight_cap = in_flight_cap
        self.in_flight_set = in_flight_set
        self.delivered_set = delivered_set
        self.dlq = dlq
        self.metrics = metrics
        self.stop_flag = stop_flag

    def start(self):
        while True:
            due_time, item = self.queue.dequeue()
            # processs time is not now
            if due_time < current_time():
                enqueue_item(item, self.processor)
            else:
                self.queue.enqueue(item)