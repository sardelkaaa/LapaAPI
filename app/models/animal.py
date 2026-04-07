from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class AnimalCreate(BaseModel):
    """Создание нового животного"""
    name: str = Field(..., min_length=1, max_length=255, example="Бим")
    age: int = Field(..., ge=0, example=3)
    description: Optional[str] = Field(None, example="Дружелюбный пёс, ищет дом")
    type_id: int = Field(..., example=1)
    location_text: str = Field(..., min_length=1, max_length=255, example="Москва, ул. Ленина 5")
    location_lat: Optional[float] = Field(None, example=55.7558)
    location_lng: Optional[float] = Field(None, example=37.6176)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Бим",
                "age": 3,
                "description": "Дружелюбный пёс, ищет дом",
                "type_id": 1,
                "location_text": "Москва, ул. Ленина 5",
                "location_lat": 55.7558,
                "location_lng": 37.6176,
            }
        }


class AnimalUpdate(BaseModel):
    """Обновление данных животного"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, example="Бимка")
    age: Optional[int] = Field(default=None, ge=0, example=4)
    description: Optional[str] = Field(None, example="Очень ласковый и спокойный")
    type_id: Optional[int] = Field(None, example=2)
    location_text: Optional[str] = Field(default=None, min_length=1, max_length=255, example="Москва, ул. Пушкина 10")
    location_lat: Optional[float] = Field(None, example=55.7559)
    location_lng: Optional[float] = Field(None, example=37.6177)
    is_active: Optional[bool] = Field(None, example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Бимка",
                "age": 4,
                "description": "Очень ласковый и спокойный",
                "is_active": False,
            }
        }


class AnimalTypeOut(BaseModel):
    """Тип животного"""
    id: int = Field(..., ge=1, description="ID типа животного", example=1)
    name: str = Field(..., description="Название", example="Собаки")

    class Config:
        json_schema_extra = {"example": {"id": 1, "name": "Собаки"}}


class AnimalOut(BaseModel):
    """Данные животного"""
    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    name: str = Field(..., example="Бим")
    age: int = Field(..., example=3)
    description: Optional[str] = Field(None, example="Дружелюбный пёс, ищет дом")

    type_id: int = Field(..., example=1)
    type_name: Optional[str] = Field(None, example="Собаки")

    curator_id: str = Field(..., example="volunteer-uuid-12345")

    location_text: str = Field(..., example="Москва, ул. Ленина 5")
    location_lat: Optional[float] = Field(None, example=55.7558)
    location_lng: Optional[float] = Field(None, example=37.6176)

    photo_url: Optional[str] = Field(None, example="https://example.com/photos/dog_bim.jpg")

    is_active: bool = Field(True, example=True)

    created_at: datetime = Field(..., example="2024-01-15T10:30:00Z")
    updated_at: datetime = Field(..., example="2024-01-20T14:25:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Бим",
                "age": 3,
                "description": "Дружелюбный пёс, ищет дом",
                "type_id": 1,
                "type_name": "Собаки",
                "curator_id": "volunteer-uuid-12345",
                "location_text": "Москва, ул. Ленина 5",
                "location_lat": 55.7558,
                "location_lng": 37.6176,
                "photo_url": "https://example.com/photos/dog_bim.jpg",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:25:00Z",
            }
        }


class AnimalListResponse(BaseModel):
    """Список животных"""
    items: List[AnimalOut]
    total: int = Field(..., example=42)

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Бим",
                        "age": 3,
                        "description": "Дружелюбный пёс",
                        "type_id": 1,
                        "type_name": "Собаки",
                        "curator_id": "volunteer-uuid-12345",
                        "location_text": "Москва, ул. Ленина 5",
                        "location_lat": 55.7558,
                        "location_lng": 37.6176,
                        "photo_url": "https://example.com/photos/dog_bim.jpg",
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-20T14:25:00Z",
                    },
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "name": "Мурка",
                        "age": 2,
                        "description": "Ласковая кошка",
                        "type_id": 2,
                        "type_name": "Кошки",
                        "curator_id": "volunteer-uuid-67890",
                        "location_text": "Москва, ул. Лермонтова 3",
                        "location_lat": 55.7560,
                        "location_lng": 37.6180,
                        "photo_url": "https://example.com/photos/cat_murka.jpg",
                        "is_active": True,
                        "created_at": "2024-02-01T09:15:00Z",
                        "updated_at": "2024-02-10T11:20:00Z",
                    }
                ],
                "total": 2
            }
        }


class AnimalDeleteResponse(BaseModel):
    """Ответ на удаление"""
    success: bool = Field(..., example=True)
    message: str = Field(..., example="Animal successfully deleted")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Animal successfully deleted"
            }
        }

class AnimalPhotoUploadResponse(BaseModel):
    """Ответ на загрузку фото животного"""
    message: str = Field(..., example="Animal photo uploaded successfully")
    photo_url: str = Field(..., example="https://xyz.supabase.co/storage/v1/object/public/animal-photos/user123/animal456/uuid-photo.jpg")
    animal: Dict[str, Any] = Field(..., description="Обновленные данные животного")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Animal photo uploaded successfully",
                "photo_url": "https://xyzcompany.supabase.co/storage/v1/object/public/animal-photos/volunteer-uuid-12345/550e8400-e29b-41d4-a716-446655440000/123e4567-e89b-12d3-a456-426614174000.jpeg",
                "animal": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Бим",
                    "age": 3,
                    "description": "Дружелюбный пёс, ищет дом",
                    "type_id": 1,
                    "type_name": "Собаки",
                    "curator_id": "volunteer-uuid-12345",
                    "location_text": "Москва, ул. Ленина 5",
                    "location_lat": 55.7558,
                    "location_lng": 37.6176,
                    "photo_url": "https://xyzcompany.supabase.co/storage/v1/object/public/animal-photos/volunteer-uuid-12345/550e8400-e29b-41d4-a716-446655440000/123e4567-e89b-12d3-a456-426614174000.jpeg",
                    "is_active": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-20T14:25:00Z",
                    "deleted_at": None
                }
            }
        }