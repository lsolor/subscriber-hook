from fastapi import APIRouter, Depends
from api.schemas.event import EventRequest, EventResponse 
from service.dispatcher import Dispatcher


router = APIRouter(prefix="/events", tags=["events"])
# Validate and then enqueue the event
@router.post("/", response_model=EventResponse, status_code=202)
async def create_event(event: EventRequest):
    # Logic to create the event
    dispatcher: Dispatcher = Dispatcher(
        queue=router.app.state.queue,
        registry=router.app.state.registry,
        metrics=router.app.state.metrics
    )
    dispatcher.enqueue_item(event, router.app.state.worker)
    return EventResponse(
        id=event.id,
        type=event.type,
        status="created",
        correlation_id=event.correlation_id,
        message="Event created successfully"
    )