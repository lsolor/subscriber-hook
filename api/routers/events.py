from fastapi import APIRouter, Request
from api.schemas.event import EventRequest, EventResponse 
from service.dispatcher import Dispatcher


router = APIRouter(prefix="/events", tags=["events"])
# Validate and then enqueue the event
@router.post("/", response_model=event_response : EventResponse, status_code=202)
async def create_event(request : Request, event: EventRequest):
    # Logic to create the event
    dispatcher: Dispatcher = Dispatcher(
        queue=request.app.state.queue,
        registry=request.app.state.registry,
        metrics=request.app.state.metrics
    )
    dispatcher.enqueue_item(event)
    return EventResponse(
        id=event.id,
        type=event.type,
        status="created",
        correlation_id=event.correlation_id,
        message="Event created successfully"
    )