from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Статус задачи"""
    IN_PENDING = "in_pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    class Config:
        json_schema_extra = {
            "example": "in_pending",
            "description": "Статус задачи: ожидает, назначена, в процессе, выполнена, отменена"
        }


class TaskRequiredSkill(BaseModel):
    """Навык, необходимый для выполнения задачи"""
    skill_id: str = Field(..., description="UUID навыка", example="550e8400-e29b-41d4-a716-446655440000")
    skill_name: Optional[str] = Field(None, description="Название навыка", example="Выгул собак")

    class Config:
        json_schema_extra = {
            "example": {
                "skill_id": "550e8400-e29b-41d4-a716-446655440000",
                "skill_name": "Выгул собак"
            }
        }


class TaskOut(BaseModel):
    """Полная информация о задаче (ответ API)"""
    id: str = Field(..., description="UUID задачи", example="660e8400-e29b-41d4-a716-446655440001")
    title: str = Field(..., description="Название задачи", min_length=1, max_length=255, example="Выгулять собаку")
    description: Optional[str] = Field(None, description="Подробное описание", example="Нужно выгулять Бима в парке")
    animal_id: str = Field(..., description="ID животного", example="770e8400-e29b-41d4-a716-446655440002")
    animal_name: Optional[str] = Field(None, description="Имя животного", example="Бим")
    creator_id: str = Field(..., description="ID создателя задачи (куратор или организация)", example="880e8400-e29b-41d4-a716-446655440003")
    assignee_id: Optional[str] = Field(None, description="ID назначенного волонтёра", example="990e8400-e29b-41d4-a716-446655440004")
    assignee_name: Optional[str] = Field(None, description="Имя волонтёра", example="Анна Смирнова")
    due_time: Optional[datetime] = Field(None, description="Крайний срок выполнения", example="2025-05-20T18:00:00Z")
    is_urgent: bool = Field(False, description="Срочная задача", example=True)
    status: TaskStatus = Field(..., description="Текущий статус", example=TaskStatus.IN_PENDING)
    required_skills: List[TaskRequiredSkill] = Field(default=[], description="Список необходимых навыков")
    location_text: Optional[str] = Field(None, description="Текстовое описание локации (берётся от животного)", example="Москва, парк Горького")
    location_lat: Optional[float] = Field(None, description="Широта", example=55.7558)
    location_lng: Optional[float] = Field(None, description="Долгота", example=37.6176)
    created_at: datetime = Field(..., description="Дата создания", example="2025-05-10T10:00:00Z")
    updated_at: datetime = Field(..., description="Дата последнего обновления", example="2025-05-10T10:30:00Z")
    assigned_at: Optional[datetime] = Field(None, description="Дата назначения волонтёра", example="2025-05-10T11:00:00Z")
    completed_at: Optional[datetime] = Field(None, description="Дата выполнения", example="2025-05-20T17:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "title": "Выгулять собаку",
                "description": "Нужно выгулять Бима в парке",
                "animal_id": "770e8400-e29b-41d4-a716-446655440002",
                "animal_name": "Бим",
                "creator_id": "880e8400-e29b-41d4-a716-446655440003",
                "assignee_id": "990e8400-e29b-41d4-a716-446655440004",
                "assignee_name": "Анна Смирнова",
                "due_time": "2025-05-20T18:00:00Z",
                "is_urgent": True,
                "status": "assigned",
                "required_skills": [
                    {
                        "skill_id": "550e8400-e29b-41d4-a716-446655440000",
                        "skill_name": "Выгул собак"
                    }
                ],
                "location_text": "Москва, парк Горького",
                "location_lat": 55.7558,
                "location_lng": 37.6176,
                "created_at": "2025-05-10T10:00:00Z",
                "updated_at": "2025-05-10T10:30:00Z",
                "assigned_at": "2025-05-10T11:00:00Z",
                "completed_at": None
            }
        }


class TaskCreate(BaseModel):
    """Данные для создания новой задачи"""
    title: str = Field(..., min_length=1, max_length=255, description="Название задачи", example="Покормить кошек")
    description: Optional[str] = Field(None, description="Подробное описание", example="В приюте закончился корм, нужно привезти 5 кг")
    animal_id: str = Field(..., description="ID животного, к которому относится задача", example="770e8400-e29b-41d4-a716-446655440002")
    due_time: Optional[datetime] = Field(None, description="Крайний срок", example="2025-05-15T12:00:00Z")
    is_urgent: bool = Field(False, description="Срочная задача", example=True)
    skill_ids: List[str] = Field(default=[], description="Список ID необходимых навыков", example=["550e8400-e29b-41d4-a716-446655440000"])

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Покормить кошек",
                "description": "В приюте закончился корм, нужно привезти 5 кг",
                "animal_id": "770e8400-e29b-41d4-a716-446655440002",
                "due_time": "2025-05-15T12:00:00Z",
                "is_urgent": True,
                "skill_ids": ["550e8400-e29b-41d4-a716-446655440000"]
            }
        }


class TaskUpdate(BaseModel):
    """Данные для обновления задачи (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название", example="Покормить и причесать кошек")
    description: Optional[str] = Field(None, description="Новое описание", example="Добавить расчёсывание")
    due_time: Optional[datetime] = Field(None, description="Новый срок", example="2025-05-16T12:00:00Z")
    is_urgent: Optional[bool] = Field(None, description="Срочность", example=False)
    status: Optional[TaskStatus] = Field(None, description="Новый статус", example="in_progress")
    skill_ids: Optional[List[str]] = Field(None, description="Обновлённый список ID навыков", example=["550e8400-e29b-41d4-a716-446655440000", "660e8400-e29b-41d4-a716-446655440001"])

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Покормить и причесать кошек",
                "description": "Добавить расчёсывание",
                "due_time": "2025-05-16T12:00:00Z",
                "is_urgent": False,
                "status": "in_progress",
                "skill_ids": ["550e8400-e29b-41d4-a716-446655440000", "660e8400-e29b-41d4-a716-446655440001"]
            }
        }


class TaskListResponse(BaseModel):
    """Ответ со списком задач (для пагинации)"""
    items: List[TaskOut] = Field(..., description="Список задач")
    total: int = Field(..., description="Общее количество задач (без учёта пагинации)", example=42)
    next_offset: Optional[int] = Field(None, description="Смещение для следующей страницы (null, если больше нет)", example=20)

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "title": "Выгулять собаку",
                        "description": "Нужно выгулять Бима в парке",
                        "animal_id": "770e8400-e29b-41d4-a716-446655440002",
                        "animal_name": "Бим",
                        "creator_id": "880e8400-e29b-41d4-a716-446655440003",
                        "assignee_id": None,
                        "assignee_name": None,
                        "due_time": "2025-05-20T18:00:00Z",
                        "is_urgent": True,
                        "status": "in_pending",
                        "required_skills": [],
                        "location_text": "Москва, парк Горького",
                        "location_lat": 55.7558,
                        "location_lng": 37.6176,
                        "created_at": "2025-05-10T10:00:00Z",
                        "updated_at": "2025-05-10T10:00:00Z",
                        "assigned_at": None,
                        "completed_at": None
                    }
                ],
                "total": 1,
                "next_offset": None
            }
        }