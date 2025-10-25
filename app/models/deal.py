from pydantic import BaseModel
from typing import Optional

class DealBase(BaseModel):
    name: str
    amount: Optional[float] = None
    status: Optional[str] = "Open"
    closed_date: Optional[str] = None  # ISO date string

class DealCreate(DealBase):
    id: str
    opportunity_id: str  # link to Opportunity

class DealUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    closed_date: Optional[str] = None

class Deal(DealBase):
    id: str
    opportunity_id: str

    class Config:
        from_attributes = True
