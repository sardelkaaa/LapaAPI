from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    """Роли пользователей"""
    user = "user"
    volunteer = "volunteer"
    curator = "curator"
    admin = "admin"
    organization = "organization"

    class Config:
        json_schema_extra = {
            "example": "volunteer",
            "examples": ["user", "volunteer", "curator", "admin", "organization"]
        }

class UserOut(BaseModel):
    """Схема для вывода пользователя"""
    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    email: EmailStr = Field(..., example="ivan.volunteer@example.com")
    name: Optional[str] = Field(None, example="Иван Петров")
    description: Optional[str] = Field(None, example="Волонтёр с 5-летним стажем, люблю животных")
    role: UserRole = Field(..., example=UserRole.volunteer)
    phone: Optional[str] = Field(None, example="+7 (999) 123-45-67")
    location_text: Optional[str] = Field(None, example="Москва, ЦАО")
    location_lat: Optional[float] = Field(None, example=55.7558)
    location_lng: Optional[float] = Field(None, example=37.6176)
    radius_preference: Optional[int] = Field(None, example=10, description="Радиус поиска в км")
    is_urgent_available: bool = Field(False, example=True, description="Готов к срочным вызовам")
    avatar_url: Optional[str] = Field(None, example="https://example.com/avatars/user123.jpg")
    is_active: bool = Field(..., example=True)
    created_at: datetime = Field(..., example="2024-01-15T10:30:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "ivan.volunteer@example.com",
                "name": "Иван Петров",
                "description": "Волонтёр с 5-летним стажем, люблю животных",
                "role": "volunteer",
                "phone": "+7 (999) 123-45-67",
                "location_text": "Москва, ЦАО",
                "location_lat": 55.7558,
                "location_lng": 37.6176,
                "radius_preference": 10,
                "is_urgent_available": True,
                "avatar_url": "https://example.com/avatars/user123.jpg",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

class UserUpdateRequests(BaseModel):
    """Схема для обновления пользователя"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="Иван Сидоров")
    description: Optional[str] = Field(None, max_length=1000, example="Люблю помогать бездомным животным")
    phone: Optional[str] = Field(None, example="+7 (999) 987-65-43")
    location_text: Optional[str] = Field(None, max_length=255, example="Санкт-Петербург, Васильевский остров")
    location_lat: Optional[float] = Field(None, ge=-90, le=90, example=59.9343)
    location_lng: Optional[float] = Field(None, ge=-180, le=180, example=30.3351)
    radius_preference: Optional[int] = Field(None, ge=1, le=100, example=25)
    is_urgent_available: bool = Field(False, example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Иван Сидоров",
                "description": "Люблю помогать бездомным животным",
                "phone": "+7 (999) 987-65-43",
                "location_text": "Санкт-Петербург, Васильевский остров",
                "location_lat": 59.9343,
                "location_lng": 30.3351,
                "radius_preference": 25,
                "is_urgent_available": True
            }
        }

# class PasswordResetRequest(BaseModel):
#
#     email: EmailStr
#
# class PasswordUpdateRequest(BaseModel):
#
#     access_token: str
#     new_password: str