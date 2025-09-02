from collections import defaultdict
from fastapi import FastAPI
from api.routers import events
import service

app = FastAPI(title="subscriber-hook", version="0.1.0")

app.include_router(events.router)


def main():
    print("Hello from subscriber-hook!")
    # App startup:
    # build subscriber registry
    registry = {"type1": ["http://example.com/callback1", "http://example.com/callback2"],
                "type2": ["http://example.com/callback3"]}
    app.state.registry = registry
    print("Subscriber registry:", app.state.registry)
    # metrics
    metrics = {"events_received": 0, "events_processed": 0, "events_failed": 0}
    app.state.metrics = metrics
    print("Metrics initialized:", app.state.metrics)
    dlq = []
    app.state.dlq = dlq
    print("Dead-letter queue initialized.")
    queue = infra.inmemory_queue.heap
    app.state.queue = queue
    print("In-memory queue initialized.")
    # dedupe set
    in_flight_set = set()
    app.state.in_flight_set = in_flight_set
    print("In-flight deduplication set initialized.")
    delivered_set = set()
    app.state.delivered_set = delivered_set
    print("Delivered deduplication set initialized.")
    config = {
        "max_retries": 4,
        "base_backoff": 2,  # seconds
        "worker_count": 4,
        "in_flight_limit_per_endpoint": 2
    }
    app.state.config = config
    print("Configuration loaded:", app.state.config)
    stop_flag = False
    app.state.stop_flag = stop_flag
    print("Stop flag initialized.")
    # start worker
    in_flight_cap = defaultdict(int)
    app.state.in_flight_cap = in_flight_cap
    worker = service.worker.Worker(queue, config, in_flight_cap, in_flight_set, delivered_set, dlq, metrics, stop_flag)
    app.state.worker = worker
    print("Worker initialized.")


    # app shutdown:
    # stop worker cleanly
    # flush logs/counters



if __name__ == "__main__":
    main()
