from fastapi import APIRouter, Request, Response, status, HTTPException
from app.api.schemas.event import EventRequest, EventResponse
from uuid import uuid4
import logging
from app.constants import CORRELATION_HDR, EventType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["events"])

ALLOWED_EVENT_TYPES = {t.value for t in EventType}


def get_correlation_id(request: Request) -> str:
    return request.headers.get(CORRELATION_HDR) or str(uuid4())


def validate_event(event: EventRequest) -> None:
    if not event.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Event 'id' is required",
        )
    if not event.type or event.type not in ALLOWED_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Event 'type' must be one of {ALLOWED_EVENT_TYPES}",
        )
    if not event.data or not isinstance(event.data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Event 'data' must be a non-empty JSON object",
        )


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation Error"}
    },
)
async def create_event(event: EventRequest, request: Request, response: Response):
    correlation_id = get_correlation_id(request)
    response.headers[CORRELATION_HDR] = correlation_id

    validate_event(event)

    logger.info(
        "event_received",
        extra={
            "correlation_id": correlation_id,
            "event_id": event.id,
            "event_type": event.type,
            "data": event.data,
        },
    )
    try:
        request.app.state.dispatcher.enqueue(event, correlation_id)
    except TimeoutError:
        logger.error(
            "enqueue_timeout",
            extra={"correlation_id": correlation_id, "event_id": event.id},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is busy, try again later",
        )
    except Exception as e:
        logger.error(
            "enqueue_error",
            extra={
                "correlation_id": correlation_id,
                "event_id": event.id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return EventResponse(
        id=event.id,
        status="accepted",
        correlation_id=correlation_id,
        message="Event has been accepted for processing",
    )
