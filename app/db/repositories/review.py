from app.core.database import get_supabase_admin
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid


class ReviewRepository:
    @staticmethod
    def create_review(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создать отзыв"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_review_by_id(review_id: str) -> Optional[Dict[str, Any]]:
        """Получить отзыв по ID"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").select("*").eq("id", review_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_review_with_details(review_id: str) -> Optional[Dict[str, Any]]:
        """Получить отзыв с деталями (имена, задача)"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").select("""
            *,
            volunteer:volunteer_id (id, name),
            reviewer:reviewer_id (id, name),
            task:task_id (id, title)
        """).eq("id", review_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_volunteer_reviews(
            volunteer_id: str,
            limit: int = 20,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить все отзывы о волонтёре"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").select("""
            *,
            volunteer:volunteer_id (id, name),
            reviewer:reviewer_id (id, name),
            task:task_id (id, title)
        """).eq("volunteer_id", volunteer_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return result.data or []

    @staticmethod
    def get_volunteer_reviews_count(volunteer_id: str) -> int:
        """Получить количество отзывов о волонтёре"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").select("*", count="exact").eq("volunteer_id",
                                                                                   volunteer_id).execute()
        return result.count or 0

    @staticmethod
    def get_volunteer_stats(volunteer_id: str) -> Optional[Dict[str, Any]]:
        """Получить статистику волонтёра"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_stats").select("*").eq("user_id", volunteer_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_volunteer_stats(volunteer_id: str) -> Dict[str, Any]:
        """Обновить статистику волонтёра (пересчитать)"""
        supabase = get_supabase_admin()

        # Получаем все отзывы
        reviews = supabase.table("volunteer_reviews").select("rating").eq("volunteer_id", volunteer_id).execute()
        reviews_data = reviews.data or []

        if reviews_data:
            avg_rating = sum(r["rating"] for r in reviews_data) / len(reviews_data)
            reviews_count = len(reviews_data)
        else:
            avg_rating = 0
            reviews_count = 0

        # Получаем количество выполненных задач
        tasks = supabase.table("tasks").select("id", count="exact").eq("assignee_id", volunteer_id).eq("status",
                                                                                                       "completed").execute()
        tasks_count = tasks.count or 0

        # Обновляем или создаём статистику
        existing = ReviewRepository.get_volunteer_stats(volunteer_id)

        stats_data = {
            "user_id": volunteer_id,
            "tasks_count": tasks_count,
            "rating_avg": round(avg_rating, 2),
            "reviews_count": reviews_count
        }

        if existing:
            supabase.table("volunteer_stats").update(stats_data).eq("user_id", volunteer_id).execute()
        else:
            supabase.table("volunteer_stats").insert(stats_data).execute()

        return stats_data

    @staticmethod
    def update_review(review_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить отзыв (только для администратора)"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").update(data).eq("id", review_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def delete_review(review_id: str) -> bool:
        """Удалить отзыв (только для администратора)"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").delete().eq("id", review_id).execute()
        return len(result.data or []) > 0

    @staticmethod
    def get_reviews_by_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Проверить, есть ли отзыв на задачу"""
        supabase = get_supabase_admin()
        result = supabase.table("volunteer_reviews").select("*").eq("task_id", task_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_rating_distribution(volunteer_id: str) -> Dict[str, int]:
        """Получить распределение оценок"""
        supabase = get_supabase_admin()

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for rating in range(1, 6):
            result = supabase.table("volunteer_reviews").select("*", count="exact").eq("volunteer_id", volunteer_id).eq(
                "rating", rating).execute()
            distribution[rating] = result.count or 0

        return {
            "rating_1": distribution[1],
            "rating_2": distribution[2],
            "rating_3": distribution[3],
            "rating_4": distribution[4],
            "rating_5": distribution[5]
        }