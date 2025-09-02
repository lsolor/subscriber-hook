from fastapi import APIRouter, Depends
from api.schemas.event import EventRequest, EventResponse 

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(event: EventRequest, heap: Session = Depends(get_heap)):
    # Logic to create the event
    return EventResponse(
        id=event.id,
        type=event.type,
        status="created",
        correlation_id=event.correlation_id,
        message="Event created successfully"
    )