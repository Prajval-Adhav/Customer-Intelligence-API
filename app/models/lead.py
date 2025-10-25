from pydantic import BaseModel, EmailStr
from typing import Optional

class LeadBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    source: Optional[str] = None
    status: Optional[str] = "New"
    score: Optional[float] = None
    value: Optional[float] = None

class LeadCreate(LeadBase):
    id: str
    assigned_to: Optional[str] = None  # User ID
    account_id: Optional[str] = None

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    source: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None
    value: Optional[float] = None
    assigned_to: Optional[str] = None
    account_id: Optional[str] = None

class Lead(LeadBase):
    id: str
    assigned_to: Optional[str] = None
    account_id: Optional[str] = None

    class Config:
        from_attributes = True
