from pydantic import BaseModel, Field
from typing import List, Optional

class EventRequest(BaseModel):
    id: int
    type: str
    payload: dict


class EventResponse(BaseModel):
    id: int
    status: str
    message: str


