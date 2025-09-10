from fastapi import APIRouter, Request, Response, status
from app.api.schemas.event import EventRequest, EventResponse 
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_event(event: EventRequest, request: Request, response: Response):
    # Validate the event
    logger.info(f"Received event: {event}")
    # Reuse incoming correlation id if present; otherwise create one
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())


    response.headers["X-Correlation-ID"] = correlation_id
    
    logger.info("event_received",
                extra={"correlation_id": correlation_id, "event_id": event.id, "event_type": event.type})
    
    return EventResponse(
        id=event.id,
        status="accepted",
        correlation_id=correlation_id,
        message="Event has been accepted for processing"
    )

