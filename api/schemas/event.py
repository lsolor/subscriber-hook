from pydantic import BaseModel, Field
from typing import List, Optional

class EventRequest(BaseModel):
    id: int
    type: str
    correlation_id: Optional[str] = None
    payload: Optional[dict] = None


class EventResponse(BaseModel):
    id: int
    status: str
    correlation_id: Optional[str] = None
    message: Optional[str] = None


