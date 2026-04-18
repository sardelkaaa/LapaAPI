from app.core.database import get_supabase_admin
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timezone


class CalendarRepository:
    @staticmethod
    def create_event(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создать событие в календаре"""
        supabase = get_supabase_admin()
        result = supabase.table("calendar_events").insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
        """Получить событие по ID"""
        supabase = get_supabase_admin()
        result = supabase.table("calendar_events").select("*").eq("id", event_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_user_events(
            user_id: str,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить события пользователя с фильтрацией по дате"""
        supabase = get_supabase_admin()

        query = supabase.table("calendar_events").select("*", count="exact").eq("created_by", user_id)

        if start_date:
            query = query.gte("event_date", start_date.isoformat())
        if end_date:
            query = query.lte("event_date", end_date.isoformat())

        result = query.order("event_date").order("start_time").range(offset, offset + limit - 1).execute()

        return result.data or []

    @staticmethod
    def get_total_count(user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
        """Получить общее количество событий пользователя"""
        supabase = get_supabase_admin()

        query = supabase.table("calendar_events").select("*", count="exact").eq("created_by", user_id)

        if start_date:
            query = query.gte("event_date", start_date.isoformat())
        if end_date:
            query = query.lte("event_date", end_date.isoformat())

        result = query.execute()
        return result.count or 0

    @staticmethod
    def update_event(event_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить событие (только если пользователь - владелец)"""
        supabase = get_supabase_admin()
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = supabase.table("calendar_events").update(data).eq("id", event_id).eq("created_by", user_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def delete_event(event_id: str, user_id: str) -> bool:
        """Удалить событие (только если пользователь - владелец)"""
        supabase = get_supabase_admin()
        result = supabase.table("calendar_events").delete().eq("id", event_id).eq("created_by", user_id).execute()
        return len(result.data or []) > 0

    @staticmethod
    def get_events_by_task(task_id: str) -> List[Dict[str, Any]]:
        """Получить все события, связанные с задачей"""
        supabase = get_supabase_admin()
        result = supabase.table("calendar_events").select("*").eq("task_id", task_id).execute()
        return result.data or []

    @staticmethod
    def delete_events_by_task(task_id: str) -> None:
        """Удалить все события, связанные с задачей"""
        supabase = get_supabase_admin()
        supabase.table("calendar_events").delete().eq("task_id", task_id).execute()