from collections import defaultdict
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routers import events, health
from threading import Event
from app.infra.inmemory_queue import InMemoryQueue
from app.service.dispatcher import Dispatcher
import logging

# from app.service.worker import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Hello from subscriber-hook!")

    q = InMemoryQueue()
    app.state.queue = q

    app.state.dispatcher = Dispatcher(
        queue=q, registry=defaultdict(list), metrics=defaultdict(int)
    )

    yield

    # Shutdown code
    logger.info("Shutdown initiated. Stopping worker...")
    # Signal stop and join the background worker
    logger.info("Worker stopped. Shutdown complete.")


app = FastAPI(title="subscriber-hook", version="0.1.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(events.router)
