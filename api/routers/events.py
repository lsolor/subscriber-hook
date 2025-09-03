from fastapi import APIRouter, Request
from api.schemas.event import EventRequest, EventResponse 


router = APIRouter(prefix="/events", tags=["events"])
# Validate and then enqueue the event
@router.post("/", response_model=EventResponse, status_code=202)
async def create_event(request: Request, event: EventRequest):
    # Logic to create the event
    request.app.state.dispatcher.enqueue(event)
    return EventResponse(
        id=event.id,
        status="created",
        correlation_id=event.correlation_id,
        message="Event created successfully",
    )
