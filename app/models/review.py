from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ReviewOut(BaseModel):
    """Отзыв о волонтёре (ответ API)"""
    id: str = Field(..., description="UUID отзыва")
    volunteer_id: str = Field(..., description="ID волонтёра")
    volunteer_name: Optional[str] = Field(None, description="Имя волонтёра")
    reviewer_id: str = Field(..., description="ID автора отзыва")
    reviewer_name: Optional[str] = Field(None, description="Имя автора отзыва")
    task_id: Optional[str] = Field(None, description="ID задачи")
    task_title: Optional[str] = Field(None, description="Название задачи")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Текст отзыва")
    created_at: datetime = Field(..., description="Дата создания")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "volunteer_id": "volunteer-uuid",
                "volunteer_name": "Анна Смирнова",
                "reviewer_id": "curator-uuid",
                "reviewer_name": "Иван Петров",
                "task_id": "task-uuid",
                "task_title": "Выгулять собаку",
                "rating": 5,
                "comment": "Отличная работа! Волонтёр очень ответственный.",
                "created_at": "2025-04-16T10:00:00Z"
            }
        }


class ReviewCreate(BaseModel):
    """Создание отзыва"""
    volunteer_id: str = Field(..., description="ID волонтёра")
    task_id: str = Field(..., description="ID выполненной задачи")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий")

    @validator('task_id')
    def validate_task_id(cls, v):
        if not v:
            raise ValueError('task_id is required')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "volunteer_id": "volunteer-uuid",
                "task_id": "task-uuid",
                "rating": 5,
                "comment": "Отличная работа!"
            }
        }


class ReviewUpdate(BaseModel):
    """Обновление отзыва (только для администратора)"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Новая оценка")
    comment: Optional[str] = Field(None, max_length=1000, description="Новый комментарий")

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 4,
                "comment": "Хорошая работа, но можно лучше"
            }
        }


class VolunteerStatsOut(BaseModel):
    """Статистика волонтёра"""
    user_id: str = Field(..., description="ID волонтёра")
    tasks_count: int = Field(..., description="Количество выполненных задач", example=42)
    rating_avg: float = Field(..., description="Средний рейтинг", example=4.8)
    reviews_count: int = Field(..., description="Количество отзывов", example=35)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "volunteer-uuid",
                "tasks_count": 42,
                "rating_avg": 4.85,
                "reviews_count": 35
            }
        }


class ReviewListResponse(BaseModel):
    """Список отзывов с пагинацией"""
    items: List[ReviewOut] = Field(..., description="Список отзывов")
    total: int = Field(..., description="Общее количество", example=42)
    next_offset: Optional[int] = Field(None, description="Следующий offset", example=20)


class RatingDistribution(BaseModel):
    """Распределение оценок"""
    rating_1: int = Field(0, description="Количество оценок 1")
    rating_2: int = Field(0, description="Количество оценок 2")
    rating_3: int = Field(0, description="Количество оценок 3")
    rating_4: int = Field(0, description="Количество оценок 4")
    rating_5: int = Field(0, description="Количество оценок 5")


class VolunteerDetailedStats(BaseModel):
    """Детальная статистика волонтёра"""
    basic: VolunteerStatsOut = Field(..., description="Базовая статистика")
    rating_distribution: RatingDistribution = Field(..., description="Распределение оценок")
    recent_reviews: List[ReviewOut] = Field(..., description="Последние 5 отзывов")