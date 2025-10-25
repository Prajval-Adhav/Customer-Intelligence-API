from pydantic import BaseModel
from typing import Optional

class AccountBase(BaseModel):
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    revenue: Optional[float] = None

class AccountCreate(AccountBase):
    id: str

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    revenue: Optional[float] = None

class Account(AccountBase):
    id: str

    class Config:
        from_attributes = True
