from collections import defaultdict
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routers import events, health
from threading import Event
from app.infra.inmemory_queue import InMemoryQueue
from app.service.dispatcher import Dispatcher
import logging
from app.service.worker import Worker
from app.constants import EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    c = {
        "max_retries": 4,
        "max_timeout": 30,
        "jitter": 0.2
    }
    registry = { EventType.USER_CREATED: ["foo.com", "plaaaa.com"],
                EventType.EMAIL_NOTIFICATION: ["bar.com", "gherk.com"]

    }
    dedup = defaultdict(str)
    dlq = []
    event = Event
    q = InMemoryQueue()
    
    metrics= defaultdict(int)
    w = Worker(queue=q, config= c, dedup=dedup, dlq=dlq, metrics=metrics, stop_event=event)
    app.state.queue = q

    app.state.dispatcher = Dispatcher(
        queue=q, registry=registry, metrics=metrics
    )
    app.state.registry = registry
    app.state.metrics = metrics
    app.state.worker = w
    app.state.config = c
    app.state.dedup = dedup

    yield

    # Shutdown code
    logger.info("Shutdown initiated. Stopping worker...")
    # Signal stop and join the background worker
    logger.info("Worker stopped. Shutdown complete.")


app = FastAPI(title="subscriber-hook", version="0.1.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(events.router)
