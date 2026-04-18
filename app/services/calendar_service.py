from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from datetime import datetime, timezone, date
import uuid
from app.db.repositories.calendar import CalendarRepository
from app.db.repositories.tasks import TasksRepository


class CalendarService:
    @staticmethod
    def _format_time(time_value) -> Optional[str]:
        """Форматирует время в строку"""
        if time_value is None:
            return None
        if hasattr(time_value, "strftime"):
            return time_value.strftime("%H:%M:%S")
        return str(time_value)

    @staticmethod
    def _enrich_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """Обогатить событие дополнительными данными"""
        return {
            "id": event.get("id"),
            "title": event.get("title"),
            "description": event.get("description"),
            "task_id": event.get("task_id"),
            "event_date": event.get("event_date"),
            "start_time": event.get("start_time"),
            "end_time": event.get("end_time"),
            "location": event.get("location"),
            "created_by": event.get("created_by"),
            "created_at": event.get("created_at"),
            "updated_at": event.get("updated_at"),
        }

    @staticmethod
    def create_event(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новое событие"""
        # Проверяем, что время начала меньше времени окончания
        if payload.get("start_time") and payload.get("end_time"):
            if payload["start_time"] >= payload["end_time"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_time must be less than end_time"
                )

        # Если указана задача, проверяем её существование
        if payload.get("task_id"):
            task = TasksRepository.get_task_by_id(payload["task_id"])
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

        # Подготавливаем время
        start_time_str = None
        if payload.get("start_time"):
            start_time = payload["start_time"]
            start_time_str = start_time.strftime("%H:%M:%S") if hasattr(start_time, "strftime") else str(start_time)

        end_time_str = None
        if payload.get("end_time"):
            end_time = payload["end_time"]
            end_time_str = end_time.strftime("%H:%M:%S") if hasattr(end_time, "strftime") else str(end_time)

        event_data = {
            "id": str(uuid.uuid4()),
            "title": payload["title"],
            "description": payload.get("description"),
            "task_id": payload.get("task_id"),
            "event_date": payload["event_date"].isoformat(),
            "start_time": start_time_str,
            "end_time": end_time_str,
            "location": payload.get("location"),
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        event = CalendarRepository.create_event(event_data)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create calendar event"
            )

        return CalendarService._enrich_event(event)

    @staticmethod
    def get_user_events(
            user_id: str,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            limit: int = 50,
            offset: int = 0
    ) -> Dict[str, Any]:
        """Получить события пользователя с пагинацией"""
        events = CalendarRepository.get_user_events(user_id, start_date, end_date, limit, offset)
        total = CalendarRepository.get_total_count(user_id, start_date, end_date)

        enriched_events = [CalendarService._enrich_event(event) for event in events]

        return {
            "items": enriched_events,
            "total": total,
            "next_offset": offset + limit if offset + limit < total else None
        }

    @staticmethod
    def update_event(event_id: str, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить событие"""
        # Проверяем существование события
        existing_event = CalendarRepository.get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Проверяем права доступа
        if existing_event["created_by"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own events"
            )

        # Проверяем время
        start_time = payload.get("start_time") or existing_event.get("start_time")
        end_time = payload.get("end_time") or existing_event.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_time must be less than end_time"
                )

        # Если указана задача, проверяем её существование
        if payload.get("task_id"):
            task = TasksRepository.get_task_by_id(payload["task_id"])
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

        # Подготавливаем данные для обновления
        update_data = {}

        if "title" in payload:
            update_data["title"] = payload["title"]
        if "description" in payload:
            update_data["description"] = payload["description"]
        if "task_id" in payload:
            update_data["task_id"] = payload["task_id"]
        if "event_date" in payload:
            update_data["event_date"] = payload["event_date"].isoformat()
        if "start_time" in payload:
            start_time_val = payload["start_time"]
            update_data["start_time"] = start_time_val.strftime("%H:%M:%S") if hasattr(start_time_val,
                                                                                       "strftime") else str(
                start_time_val)
        if "end_time" in payload:
            end_time_val = payload["end_time"]
            update_data["end_time"] = end_time_val.strftime("%H:%M:%S") if hasattr(end_time_val, "strftime") else str(
                end_time_val)
        if "location" in payload:
            update_data["location"] = payload["location"]

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        updated_event = CalendarRepository.update_event(event_id, user_id, update_data)
        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update event"
            )

        return CalendarService._enrich_event(updated_event)

    @staticmethod
    def delete_event(event_id: str, user_id: str) -> Dict[str, Any]:
        """Удалить событие"""
        existing_event = CalendarRepository.get_event_by_id(event_id)
        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if existing_event["created_by"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own events"
            )

        deleted = CalendarRepository.delete_event(event_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete event"
            )

        return {
            "success": True,
            "message": "Event deleted successfully"
        }

    @staticmethod
    def get_event_by_id(event_id: str, user_id: str) -> Dict[str, Any]:
        """Получить событие по ID с проверкой прав"""
        event = CalendarRepository.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        if event["created_by"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own events"
            )

        return CalendarService._enrich_event(event)

    @staticmethod
    def get_events_by_month(user_id: str, year: int, month: int) -> Dict[str, Any]:
        """Получить события за конкретный месяц"""
        start_date = date(year, month, 1)

        # Определяем последний день месяца
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        events = CalendarRepository.get_user_events(user_id, start_date, end_date, limit=1000, offset=0)

        # Группируем события по дням
        events_by_day = {}
        for event in events:
            event_date = event["event_date"]
            if event_date not in events_by_day:
                events_by_day[event_date] = []
            events_by_day[event_date].append(CalendarService._enrich_event(event))

        return {
            "year": year,
            "month": month,
            "events": events_by_day,
            "total": len(events)
        }