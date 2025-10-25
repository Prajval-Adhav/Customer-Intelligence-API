from pydantic import BaseModel
from typing import Optional

class OpportunityBase(BaseModel):
    name: str
    stage: Optional[str] = "Prospecting"
    estimated_value: Optional[float] = None
    probability: Optional[float] = None
    expected_close_date: Optional[str] = None  # ISO date string

class OpportunityCreate(OpportunityBase):
    id: str
    lead_id: str  # link to Lead

class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    stage: Optional[str] = None
    estimated_value: Optional[float] = None
    probability: Optional[float] = None
    expected_close_date: Optional[str] = None

class Opportunity(OpportunityBase):
    id: str
    lead_id: str

    class Config:
        from_attributes = True
