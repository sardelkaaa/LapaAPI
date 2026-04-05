from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time
from enum import Enum

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


class AnimalTypeOut(BaseModel):
    """Тип животного"""
    id: int = Field(..., ge=1, description="ID типа животного")
    name: str = Field(..., description="Название")

    class Config:
        json_schema_extra = {"example": {"id": 1, "name": "Собаки"}}


class InteractionType(str, Enum):
    """Тип взаимодействия"""
    SHELTER = "shelter"
    FOSTER = "foster"
    STREET = "street"

class DaySchedule(BaseModel):
    """Расписание на один день недели"""
    day_of_week: int = Field(..., ge=0, le=6, description="0-пн, 1-вт, 2-ср, 3-чт, 4-пт, 5-сб, 6-вс")
    start_time: time = Field(..., description="Время начала", examples=["09:00:00"])
    end_time: time = Field(..., description="Время окончания", examples=["18:00:00"])
    is_working: bool = Field(True, description="Рабочий день")


class WeeklySchedule(BaseModel):
    """Еженедельное расписание (все дни)"""
    monday: Optional[DaySchedule] = None
    tuesday: Optional[DaySchedule] = None
    wednesday: Optional[DaySchedule] = None
    thursday: Optional[DaySchedule] = None
    friday: Optional[DaySchedule] = None
    saturday: Optional[DaySchedule] = None
    sunday: Optional[DaySchedule] = None


class SimpleSchedule(BaseModel):
    """Простое расписание (список дней)"""
    days: List[DaySchedule] = Field(default=[], description="Список дней с расписанием")


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
    skill_ids: List[str] = Field(..., description="Список ID навыков")


class UpdateVolunteerPreferencesRequest(BaseModel):
    preference_ids: List[str] = Field(..., description="Список ID предпочтений")


class UpdateVolunteerAnimalPreferencesRequest(BaseModel):
    animal_type_ids: List[int] = Field(..., description="Список ID типов животных")

class UpdateVolunteerInteractionPreferencesRequest(BaseModel):
    interaction_types: List[InteractionType] = Field(..., description="Типы взаимодействия")

class UpdateScheduleRequest(BaseModel):
    """Обновление расписания (полная замена)"""
    schedule: List[DaySchedule] = Field(..., description="Новое расписание")
