from pydantic import BaseModel
from typing import Optional

class ActivityBase(BaseModel):
    type: str  # call, email, meeting, note
    note: Optional[str] = None
    timestamp: Optional[str] = None  # ISO date string
    duration: Optional[float] = None  # in minutes
    channel: Optional[str] = None  # e.g., email, phone, in-person

class ActivityCreate(ActivityBase):
    id: str
    user_id: str
    lead_id: str

class ActivityUpdate(BaseModel):
    type: Optional[str] = None
    note: Optional[str] = None
    timestamp: Optional[str] = None
    duration: Optional[float] = None
    channel: Optional[str] = None

class Activity(ActivityBase):
    id: str
    user_id: str
    lead_id: str

    class Config:
        from_attributes = True
