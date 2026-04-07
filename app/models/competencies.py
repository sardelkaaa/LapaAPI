from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time
from enum import Enum

from app.models.animal import AnimalTypeOut


class SkillOut(BaseModel):
    """Навык волонтёра"""
    id: str = Field(..., description="UUID навыка")
    name: str = Field(..., description="Название навыка")

    class Config:
        json_schema_extra = {"example": {"id": "uuid", "name": "Выгул собак"}}


class PreferenceOut(BaseModel):
    """Предпочтение волонтёра"""
    id: str = Field(..., description="UUID предпочтения")
    name: str = Field(..., description="Название предпочтения")

    class Config:
        json_schema_extra = {"example": {"id": "uuid", "name": "Помощь приютам"}}


class InteractionType(str, Enum):
    """Тип взаимодействия"""
    SHELTER = "shelter"
    FOSTER = "foster"
    STREET = "street"

class DaySchedule(BaseModel):
    """Расписание на один день недели"""
    day_of_week: int = Field(..., ge=0, le=6, description="0-пн, 1-вт, 2-ср, 3-чт, 4-пт, 5-сб, 6-вс", example=0)
    start_time: time = Field(..., description="Время начала", example="09:00:00")
    end_time: time = Field(..., description="Время окончания", example="18:00:00")
    is_working: bool = Field(True, description="Рабочий день", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": 0,
                "start_time": "09:00:00",
                "end_time": "18:00:00",
                "is_working": True
            }
        }

class VolunteerAvailability(BaseModel):
    """Доступность волонтёра"""
    schedule: List[DaySchedule] = Field(default=[], description="Расписание по дням недели")
    timezone: str = Field("UTC", description="Часовой пояс")

    class Config:
        json_schema_extra = {
            "example": {
                "schedule": [
                    {"day_of_week": 0, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 1, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 2, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 3, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 4, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 5, "start_time": "10:00:00", "end_time": "15:00:00", "is_working": True}
                ],
                "timezone": "Europe/Moscow"
            }
        }

class VolunteerCompetenciesResponse(BaseModel):
    """Полный профиль компетенций волонтёра"""
    skills: List[SkillOut] = Field(..., description="Навыки")
    preferences: List[PreferenceOut] = Field(..., description="Предпочтения")
    animal_preferences: List[AnimalTypeOut] = Field(..., description="Предпочитаемые животные")
    interaction_preferences: List[InteractionType] = Field(..., description="Типы взаимодействия")
    availability: VolunteerAvailability = Field(..., description="Доступность")

    class Config:
        json_schema_extra = {
            "example": {
                "skills": [{"id": "uuid1", "name": "Выгул собак"}],
                "preferences": [{"id": "uuid2", "name": "Помощь приютам"}],
                "animal_preferences": [{"id": 1, "name": "Собаки"}],
                "interaction_preferences": ["shelter"],
                "availability": {
                    "schedule": [{"day_of_week": 0, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True}],
                    "timezone": "Europe/Moscow"
                },
            }
        }

class UpdateVolunteerSkillsRequest(BaseModel):
    """Обновление навыков волонтёра"""
    skill_ids: List[str] = Field(..., description="Список ID навыков", example=["uuid1", "uuid2", "uuid3"])

    class Config:
        json_schema_extra = {
            "example": {
                "skill_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001",
                    "770e8400-e29b-41d4-a716-446655440002"
                ]
            }
        }

class UpdateVolunteerPreferencesRequest(BaseModel):
    """Обновление предпочтений волонтёра"""
    preference_ids: List[str] = Field(..., description="Список ID предпочтений", example=["uuid1", "uuid2"])

    class Config:
        json_schema_extra = {
            "example": {
                "preference_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001"
                ]
            }
        }

class UpdateVolunteerAnimalPreferencesRequest(BaseModel):
    """Обновление предпочтений животных"""
    animal_type_ids: List[int] = Field(..., description="Список ID типов животных", example=[1, 2, 3])

    class Config:
        json_schema_extra = {
            "example": {
                "animal_type_ids": [1, 2, 3]
            }
        }

class UpdateVolunteerInteractionPreferencesRequest(BaseModel):
    """Обновление предпочтений взаимодействий"""
    interaction_types: List[InteractionType] = Field(..., description="Типы взаимодействия", example=["shelter", "foster"])

    class Config:
        json_schema_extra = {
            "example": {
                "interaction_types": ["shelter", "foster", "street"]
            }
        }

class UpdateScheduleRequest(BaseModel):
    """Обновление расписания (полная замена)"""
    schedule: List[DaySchedule] = Field(..., description="Новое расписание")

    class Config:
        json_schema_extra = {
            "example": {
                "schedule": [
                    {"day_of_week": 0, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 1, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 2, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": False},
                    {"day_of_week": 3, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 4, "start_time": "09:00:00", "end_time": "18:00:00", "is_working": True},
                    {"day_of_week": 5, "start_time": "10:00:00", "end_time": "15:00:00", "is_working": True},
                    {"day_of_week": 6, "start_time": "12:00:00", "end_time": "16:00:00", "is_working": True}
                ]
            }
        }