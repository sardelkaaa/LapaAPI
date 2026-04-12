from typing import Dict, Any, List, Optional
from app.core.database import get_supabase, get_supabase_admin
from datetime import datetime, timezone

class TasksRepository:
    @staticmethod
    def create_task(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
        supabase = get_supabase()
        result = supabase.table("tasks").select("*").eq("id", task_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_task_with_details(task_id: str) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("tasks").select("""
            *,
            animal:animal_id (id, name, location_text, location_lat, location_lng, type_id),
            creator:creator_id (id, name),
            assignee:assignee_id (id, name),
            required_skills:task_required_skills (
                skill_id,
                skill:skill_id (id, name)
            )
        """).eq("id", task_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_task(task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def list_tasks_with_filters(
        filters: Dict[str, Any],
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        supabase = get_supabase()
        query = supabase.table("tasks").select("*", count="exact")
        if "status" in filters:
            query = query.eq("status", filters["status"])
        if "assignee_id" in filters:
            query = query.eq("assignee_id", filters["assignee_id"])
        if "creator_id" in filters:
            query = query.eq("creator_id", filters["creator_id"])
        if "animal_id" in filters:
            query = query.eq("animal_id", filters["animal_id"])
        if "is_urgent" in filters:
            query = query.eq("is_urgent", filters["is_urgent"])
        query = query.order("is_urgent", desc=True).order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []

    @staticmethod
    def add_required_skills(task_id: str, skill_ids: List[str]) -> None:
        supabase = get_supabase_admin()
        if not skill_ids:
            return
        records = [{"task_id": task_id, "skill_id": sid} for sid in skill_ids]
        supabase.table("task_required_skills").insert(records).execute()

    @staticmethod
    def update_required_skills(task_id: str, skill_ids: List[str]) -> None:
        supabase = get_supabase_admin()
        supabase.table("task_required_skills").delete().eq("task_id", task_id).execute()
        if skill_ids:
            TasksRepository.add_required_skills(task_id, skill_ids)

    @staticmethod
    def get_required_skills(task_id: str) -> List[Dict[str, Any]]:
        supabase = get_supabase()
        result = supabase.table("task_required_skills").select("skill_id, skills(*)").eq("task_id", task_id).execute()
        return [item["skills"] for item in result.data if item.get("skills")] if result.data else []

    @staticmethod
    def add_status_history(task_id: str, old_status: Optional[str], new_status: str, user_id: Optional[str], comment: Optional[str] = None):
        supabase = get_supabase_admin()
        data = {
            "task_id": task_id,
            "old_status": old_status,
            "new_status": new_status,
            "user_id": user_id,
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "comment": comment
        }
        supabase.table("task_status_history").insert(data).execute()

    @staticmethod
    def get_status_history(task_id: str) -> List[Dict[str, Any]]:
        supabase = get_supabase()
        result = supabase.table("task_status_history").select("*").eq("task_id", task_id).order("changed_at").execute()
        return result.data or []