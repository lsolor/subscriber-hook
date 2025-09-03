from collections import defaultdict
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routers import events
from threading import Event
from infra.inmemory_queue import InMemoryQueue
from service.worker import Worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Hello from subscriber-hook!")
    registry = {"type1": ["http://example.com/callback1", "http://example.com/callback2"],
                "type2": ["http://example.com/callback3"],
                "type3": ["http://example.com/callback4", "http://example.com/callback5", "http://example.com/callback6"]}
    
    app.state.registry = registry
    metrics = {"events_received": 0, "events_processed": 0, "events_failed": 0}
    app.state.metrics = metrics
    dlq = []
    app.state.dlq = dlq
    queue = InMemoryQueue()
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
        "in_flight_limit_per_endpoint": 2
    }
    app.state.config = config
    print("Configuration loaded:", app.state.config)
    stop_event = Event()
    app.state.stop_event = stop_event
    print("Stop event initialized.")
    # start worker
    in_flight_cap = defaultdict(int)
    app.state.in_flight_cap = in_flight_cap
    worker = Worker(queue, config, in_flight_cap, in_flight_set, delivered_set, dlq, metrics, stop_event)
    app.state.worker = worker
    worker.start_background()
    print("Worker started.")

    yield

    # Shutdown code
    print("Shutdown initiated. Stopping worker...")
    # Signal stop and join the background worker
    app.state.stop_event.set()
    app.state.worker.stop()
    print("Worker stopped. Shutdown complete.")


app = FastAPI(title="subscriber-hook", version="0.1.0", lifespan=lifespan)

app.include_router(events.router)




