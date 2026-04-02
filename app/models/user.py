from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    user = "user"
    volunteer = "volunteer"
    curator = "curator"
    admin = "admin"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    description: Optional[str] = None
    role: UserRole
    phone: Optional[str] = None
    location_text: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    radius_preference: Optional[int] = None
    is_urgent_available: bool = False
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

class UserUpdateRequests(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    location_text: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    radius_preference: Optional[int] = None
    is_urgent_available: bool = False

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordUpdateRequest(BaseModel):
    access_token: str
    new_password: str