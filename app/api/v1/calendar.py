from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.v1.deps import get_current_user
from app.services.calendar_service import CalendarService
from app.models.calendar import (
    CalendarEventOut,
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventListResponse,
    CalendarMonthResponse
)
from typing import Optional, Dict, Any
from datetime import date

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.post("/events", response_model=CalendarEventOut, status_code=status.HTTP_201_CREATED)
def create_event(
        payload: CalendarEventCreate,
        current_user=Depends(get_current_user)
):
    """
    Создать новое событие в календаре
    """
    return CalendarService.create_event(current_user["id"], payload.model_dump())


@router.get("/events", response_model=CalendarEventListResponse)
def get_events(
        start_date: Optional[date] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
        limit: int = Query(50, ge=1, le=200, description="Количество событий на странице"),
        offset: int = Query(0, ge=0, description="Смещение для пагинации"),
        current_user=Depends(get_current_user)
):
    """
    Получить список событий пользователя
    """
    return CalendarService.get_user_events(
        current_user["id"],
        start_date,
        end_date,
        limit,
        offset
    )


@router.get("/events/month", response_model=CalendarMonthResponse)
def get_events_by_month(
        year: int = Query(..., description="Год", ge=2020, le=2030),
        month: int = Query(..., description="Месяц", ge=1, le=12),
        current_user=Depends(get_current_user)
):
    """
    Получить события за конкретный месяц (группировка по дням)
    """
    return CalendarService.get_events_by_month(current_user["id"], year, month)


@router.get("/events/{event_id}", response_model=CalendarEventOut)
def get_event(
        event_id: str,
        current_user=Depends(get_current_user)
):
    """
    Получить событие по ID
    """
    return CalendarService.get_event_by_id(event_id, current_user["id"])


@router.put("/events/{event_id}", response_model=CalendarEventOut)
def update_event(
        event_id: str,
        payload: CalendarEventUpdate,
        current_user=Depends(get_current_user)
):
    """
    Обновить событие
    """
    return CalendarService.update_event(
        event_id,
        current_user["id"],
        payload.model_dump(exclude_unset=True)
    )


@router.delete("/events/{event_id}")
def delete_event(
        event_id: str,
        current_user=Depends(get_current_user)
):
    """
    Удалить событие
    """
    return CalendarService.delete_event(event_id, current_user["id"])