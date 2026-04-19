from typing import Dict, Any
from fastapi import HTTPException
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.animals import AnimalsRepository
from app.db.repositories.volunteer_competencies import VolunteerCompetenciesRepository
from datetime import datetime, timezone
import uuid
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

class TaskService:
    @staticmethod
    def _check_manager_role(user: Dict[str, Any]):
        if user.get("role") not in ["curator", "organization"]:
            raise HTTPException(403, "Only curator or organization can manage tasks")

    @staticmethod
    def _check_volunteer_role(user: Dict[str, Any]):
        if user.get("role") != "volunteer":
            raise HTTPException(403, "Only volunteer can take tasks")

    @staticmethod
    def _enrich_task(task_id: str) -> Dict[str, Any]:
        detailed = TasksRepository.get_task_with_details(task_id)
        if not detailed:
            raise HTTPException(404, "Task not found")
        animal = detailed.get("animal") or {}
        creator = detailed.get("creator") or {}
        assignee = detailed.get("assignee") or {}
        required_skills = []
        for rs in detailed.get("required_skills", []):
            skill = rs.get("skill")
            if skill:
                required_skills.append({"skill_id": skill["id"], "skill_name": skill["name"]})
        return {
            "id": detailed["id"],
            "title": detailed["title"],
            "description": detailed["description"],
            "animal_id": detailed["animal_id"],
            "animal_name": animal.get("name"),
            "creator_id": detailed["creator_id"],
            "assignee_id": detailed.get("assignee_id"),
            "assignee_name": assignee.get("name"),
            "due_time": detailed.get("due_time"),
            "is_urgent": detailed.get("is_urgent"),
            "status": detailed.get("status"),
            "required_skills": required_skills,
            "location_text": animal.get("location_text"),
            "location_lat": animal.get("location_lat"),
            "location_lng": animal.get("location_lng"),
            "created_at": detailed["created_at"],
            "updated_at": detailed["updated_at"],
            "assigned_at": detailed.get("assigned_at"),
            "completed_at": detailed.get("completed_at"),
        }

    @staticmethod
    def create_task(user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        TaskService._check_manager_role(user)
        animal = AnimalsRepository.get_animal_by_id(payload["animal_id"])
        if not animal:
            raise HTTPException(404, "Animal not found")
        if user["role"] == "curator" and animal["curator_id"] != user["id"]:
            raise HTTPException(403, "You can only create tasks for your own animals")

        task_data = {
            "id": str(uuid.uuid4()),
            "title": payload["title"],
            "description": payload.get("description"),
            "animal_id": payload["animal_id"],
            "creator_id": user["id"],
            "due_time": payload.get("due_time").isoformat(),
            "is_urgent": payload.get("is_urgent", False),
            "status": "in_pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        task = TasksRepository.create_task(task_data)
        if not task:
            raise HTTPException(400, "Failed to create task")
        skill_ids = payload.get("skill_ids", [])
        if skill_ids:
            TasksRepository.add_required_skills(task["id"], skill_ids)
        TasksRepository.add_status_history(task["id"], None, "in_pending", user["id"])
        return TaskService._enrich_task(task["id"])

    @staticmethod
    def get_task(task_id: str) -> Dict[str, Any]:
        return TaskService._enrich_task(task_id)

    @staticmethod
    def update_task(user: Dict[str, Any], task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        task = TasksRepository.get_task_by_id(task_id)
        if not task:
            raise HTTPException(404, "Task not found")
        if user["role"] not in ["admin"] and task["creator_id"] != user["id"]:
            raise HTTPException(403, "Only creator can update task")
        update_data = {}
        if "title" in payload:
            update_data["title"] = payload["title"]
        if "description" in payload:
            update_data["description"] = payload["description"]
        if "due_time" in payload:
            update_data["due_time"] = payload["due_time"]
        if "is_urgent" in payload:
            update_data["is_urgent"] = payload["is_urgent"]
        if "status" in payload:
            old = task["status"]
            new = payload["status"]
            update_data["status"] = new
            if new == "completed":
                update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            TasksRepository.add_status_history(task_id, old, new, user["id"])
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            TasksRepository.update_task(task_id, update_data)
        if "skill_ids" in payload:
            TasksRepository.update_required_skills(task_id, payload["skill_ids"])
        return TaskService._enrich_task(task_id)

    @staticmethod
    def take_task(user: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        TaskService._check_volunteer_role(user)
        task = TasksRepository.get_task_by_id(task_id)
        if not task or task["status"] != "in_pending" or task.get("assignee_id"):
            raise HTTPException(400, "Task not available")
        update_data = {
            "assignee_id": user["id"],
            "status": "assigned",
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        TasksRepository.update_task(task_id, update_data)
        TasksRepository.add_status_history(task_id, task["status"], "assigned", user["id"])
        return TaskService._enrich_task(task_id)

    @staticmethod
    def cancel_task(user: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        task = TasksRepository.get_task_by_id(task_id)
        if not task:
            raise HTTPException(404, "Task not found")
        if task["status"] not in ["assigned", "in_progress"]:
            raise HTTPException(400, "Cannot cancel task")
        if user["role"] == "volunteer" and task["assignee_id"] != user["id"]:
            raise HTTPException(403, "Not assignee")
        if user["role"] not in ["volunteer", "curator", "organization", "admin"]:
            raise HTTPException(403, "No permission")
        update_data = {
            "assignee_id": None,
            "status": "in_pending",
            "assigned_at": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        TasksRepository.update_task(task_id, update_data)
        TasksRepository.add_status_history(task_id, task["status"], "in_pending", user["id"])
        return TaskService._enrich_task(task_id)

    @staticmethod
    def complete_task(user: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        task = TasksRepository.get_task_by_id(task_id)
        if not task or task["assignee_id"] != user["id"]:
            raise HTTPException(403, "Only assignee can complete")
        if task["status"] not in ["assigned", "in_progress"]:
            raise HTTPException(400, "Task cannot be completed")
        update_data = {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        TasksRepository.update_task(task_id, update_data)
        TasksRepository.add_status_history(task_id, task["status"], "completed", user["id"])
        return TaskService._enrich_task(task_id)

    @staticmethod
    def list_tasks(user: Dict[str, Any], limit: int, offset: int) -> Dict[str, Any]:
        if user["role"] == "volunteer":
            # Все in_pending + свои назначенные
            all_tasks = TasksRepository.list_tasks_with_filters({}, limit=1000, offset=0)
            filtered = [t for t in all_tasks if t["status"] == "in_pending" or t.get("assignee_id") == user["id"]]
            total = len(filtered)
            items = [TaskService._enrich_task(t["id"]) for t in filtered[offset:offset+limit]]
            return {"items": items, "total": total, "next_offset": offset+limit if offset+limit < total else None}
        else:
            tasks = TasksRepository.list_tasks_with_filters({"creator_id": user["id"]}, limit, offset)
            items = [TaskService._enrich_task(t["id"]) for t in tasks]
            total = len(tasks)  # не точное, но для demo
            return {"items": items, "total": total, "next_offset": offset+limit if offset+limit < total else None}

    @staticmethod
    def recommend_tasks(user: Dict[str, Any], limit: int, offset: int) -> Dict[str, Any]:
        TaskService._check_volunteer_role(user)
        volunteer_id = user["id"]
        skills = VolunteerCompetenciesRepository.get_volunteer_skills(volunteer_id)
        skill_ids = [s["id"] for s in skills]
        animal_prefs = VolunteerCompetenciesRepository.get_volunteer_animal_preferences(volunteer_id)
        animal_type_ids = [a["id"] for a in animal_prefs]
        schedule = VolunteerCompetenciesRepository.get_schedule(volunteer_id)  # не используется в простой версии

        all_tasks = TasksRepository.list_tasks_with_filters({"status": "in_pending"}, limit=1000, offset=0)
        scored = []
        for task in all_tasks:
            animal = task.get("animal") or {}
            if animal_type_ids and animal.get("type_id") not in animal_type_ids:
                continue
            required = TasksRepository.get_required_skills(task["id"])
            required_ids = [r["id"] for r in required]
            if required_ids and not any(sid in skill_ids for sid in required_ids):
                continue
            score = 0
            if task.get("is_urgent"):
                score += 10
            match_count = len([sid for sid in required_ids if sid in skill_ids])
            score += match_count * 2
            if user.get("location_lat") and animal.get("location_lat"):
                dist = haversine(user["location_lat"], user["location_lng"], animal["location_lat"], animal["location_lng"])
                score += max(0, 20 - dist)
            scored.append((score, task))
        scored.sort(key=lambda x: x[0], reverse=True)
        total = len(scored)
        items = [TaskService._enrich_task(t["id"]) for _, t in scored[offset:offset+limit]]
        return {"items": items, "total": total, "next_offset": offset+limit if offset+limit < total else None}