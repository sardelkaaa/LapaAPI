from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    description: Optional[str] = None
    role: Enum("curator", "volunteer", "organization")
    phone: Optional[str] = None
    location_text: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    radius_preference: Optional[int] = None
    is_urgent_available: bool
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime