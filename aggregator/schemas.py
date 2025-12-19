from pydantic import BaseModel
from datetime import datetime
from typing import Any, List

class EventBase(BaseModel):
    topic: str
    event_id: str
    timestamp: datetime
    source: str
    payload: dict

class EventResponse(EventBase):
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    received: int
    unique_processed: int
    duplicate_dropped: int
    topics: List[str]
    uptime_seconds: float