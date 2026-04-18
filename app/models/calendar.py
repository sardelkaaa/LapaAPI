from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime, time


class CalendarEventOut(BaseModel):
    """Событие в календаре (ответ API)"""
    id: str = Field(..., description="UUID события")
    title: str = Field(..., description="Название события", example="Выгул собаки")
    description: Optional[str] = Field(None, description="Описание", example="Прогулка в парке")
    task_id: Optional[str] = Field(None, description="ID связанной задачи")
    event_date: date = Field(..., description="Дата события", example="2025-04-20")
    start_time: Optional[time] = Field(None, description="Время начала", example="14:00:00")
    end_time: Optional[time] = Field(None, description="Время окончания", example="15:00:00")
    location: Optional[str] = Field(None, description="Место проведения", example="Москва, парк Горького")
    created_by: str = Field(..., description="ID создателя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "title": "Выгул собаки",
                "description": "Прогулка с Бимом в парке",
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_date": "2025-04-20",
                "start_time": "14:00:00",
                "end_time": "15:00:00",
                "location": "Москва, парк Горького",
                "created_by": "770e8400-e29b-41d4-a716-446655440002",
                "created_at": "2025-04-16T10:00:00Z",
                "updated_at": "2025-04-16T10:00:00Z"
            }
        }


class CalendarEventCreate(BaseModel):
    """Создание нового события"""
    title: str = Field(..., min_length=1, max_length=255, description="Название события",
                       example="Встреча с волонтёрами")
    description: Optional[str] = Field(None, max_length=1000, description="Описание",
                                       example="Обсуждение планов на неделю")
    task_id: Optional[str] = Field(None, description="ID связанной задачи")
    event_date: date = Field(..., description="Дата события", example="2025-04-25")
    start_time: Optional[time] = Field(None, description="Время начала", example="10:00:00")
    end_time: Optional[time] = Field(None, description="Время окончания", example="11:30:00")
    location: Optional[str] = Field(None, max_length=500, description="Место проведения", example="Онлайн")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Встреча с волонтёрами",
                "description": "Обсуждение планов на неделю",
                "task_id": None,
                "event_date": "2025-04-25",
                "start_time": "10:00:00",
                "end_time": "11:30:00",
                "location": "Онлайн"
            }
        }


class CalendarEventUpdate(BaseModel):
    """Обновление события (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Новое название")
    description: Optional[str] = Field(None, max_length=1000, description="Новое описание")
    task_id: Optional[str] = Field(None, description="Новый ID задачи")
    event_date: Optional[date] = Field(None, description="Новая дата")
    start_time: Optional[time] = Field(None, description="Новое время начала")
    end_time: Optional[time] = Field(None, description="Новое время окончания")
    location: Optional[str] = Field(None, max_length=500, description="Новое место")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Перенос встречи",
                "event_date": "2025-04-26",
                "start_time": "16:00:00",
                "end_time": "17:30:00"
            }
        }


class CalendarEventListResponse(BaseModel):
    """Список событий с пагинацией"""
    items: List[CalendarEventOut] = Field(..., description="Список событий")
    total: int = Field(..., description="Общее количество", example=42)
    next_offset: Optional[int] = Field(None, description="Следующий offset", example=20)


class CalendarMonthResponse(BaseModel):
    """События за месяц (сгруппированные по дням)"""
    year: int = Field(..., description="Год")
    month: int = Field(..., description="Месяц")
    events: Dict[str, List[CalendarEventOut]] = Field(..., description="События, сгруппированные по дням (YYYY-MM-DD)")
    total: int = Field(..., description="Общее количество событий")