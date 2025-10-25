from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    role: str
    region: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    id: str  # unique user ID

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    region: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: str

    class Config:
        from_attributes = True
