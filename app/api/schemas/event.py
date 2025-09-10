from pydantic import BaseModel, Field
from typing import Any, Dict


class EventRequest(BaseModel):
    id: int
    type: str
    data: Dict[str, Any] = Field(
        ..., description="A non-empty JSON object containing event data"
    )


class EventResponse(BaseModel):
    id: int
    status: str
    message: str
