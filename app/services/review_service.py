from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from datetime import datetime, timezone
import uuid

from app.core.database import get_supabase_admin
from app.db.repositories.review import ReviewRepository
from app.db.repositories.tasks import TasksRepository
from app.db.repositories.users import UsersRepository


class ReviewService:
    @staticmethod
    def _enrich_review(review: Dict[str, Any]) -> Dict[str, Any]:
        """Обогатить отзыв дополнительными данными"""
        volunteer = review.get("volunteer") or {}
        reviewer = review.get("reviewer") or {}
        task = review.get("task") or {}

        return {
            "id": review.get("id"),
            "volunteer_id": review.get("volunteer_id"),
            "volunteer_name": volunteer.get("name"),
            "reviewer_id": review.get("reviewer_id"),
            "reviewer_name": reviewer.get("name"),
            "task_id": review.get("task_id"),
            "task_title": task.get("title"),
            "rating": review.get("rating"),
            "comment": review.get("comment"),
            "created_at": review.get("created_at"),
        }

    @staticmethod
    def _check_can_review(user: Dict[str, Any], task: Dict[str, Any]) -> None:
        """Проверить, может ли пользователь оставить отзыв"""
        # Только куратор или организация могут оставлять отзывы
        if user.get("role") not in ["curator", "organization", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only curator, organization or admin can leave reviews"
            )

        # Проверяем, что задача завершена
        if task.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed tasks"
            )

        # Проверяем, что пользователь связан с задачей (создатель или администратор)
        if user.get("role") != "admin" and task.get("creator_id") != user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review tasks you created"
            )

    @staticmethod
    def create_review(user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Создать отзыв на волонтёра"""
        # Проверяем существование задачи
        task = TasksRepository.get_task_by_id(payload["task_id"])
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Проверяем права на создание отзыва
        ReviewService._check_can_review(user, task)

        # Проверяем, что волонтёр существует
        volunteer = UsersRepository.get_user_by_id(payload["volunteer_id"])
        if not volunteer or volunteer.get("role") != "volunteer":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )

        # Проверяем, что волонтёр действительно был назначен на задачу
        if task.get("assignee_id") != payload["volunteer_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This volunteer was not assigned to this task"
            )

        # Проверяем, что отзыв на эту задачу ещё не оставлен
        existing_review = ReviewRepository.get_reviews_by_task(payload["task_id"])
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review for this task already exists"
            )

        # Создаём отзыв
        review_data = {
            "id": str(uuid.uuid4()),
            "volunteer_id": payload["volunteer_id"],
            "reviewer_id": user["id"],
            "task_id": payload["task_id"],
            "rating": payload["rating"],
            "comment": payload.get("comment"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        review = ReviewRepository.create_review(review_data)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create review"
            )

        # Обновляем статистику волонтёра
        ReviewRepository.update_volunteer_stats(payload["volunteer_id"])

        # Получаем созданный отзыв с деталями
        created_review = ReviewRepository.get_review_with_details(review["id"])

        return ReviewService._enrich_review(created_review)

    @staticmethod
    def get_volunteer_reviews(
            volunteer_id: str,
            limit: int = 20,
            offset: int = 0
    ) -> Dict[str, Any]:
        """Получить все отзывы о волонтёре"""
        # Проверяем существование волонтёра
        volunteer = UsersRepository.get_user_by_id(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )

        reviews = ReviewRepository.get_volunteer_reviews(volunteer_id, limit, offset)
        total = ReviewRepository.get_volunteer_reviews_count(volunteer_id)

        enriched_reviews = [ReviewService._enrich_review(review) for review in reviews]

        return {
            "items": enriched_reviews,
            "total": total,
            "next_offset": offset + limit if offset + limit < total else None
        }

    @staticmethod
    def get_volunteer_stats(volunteer_id: str) -> Dict[str, Any]:
        """Получить статистику волонтёра"""
        # Проверяем существование волонтёра
        volunteer = UsersRepository.get_user_by_id(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volunteer not found"
            )

        stats = ReviewRepository.get_volunteer_stats(volunteer_id)
        if not stats:
            # Если статистики нет, создаём
            stats = ReviewRepository.update_volunteer_stats(volunteer_id)

        return {
            "user_id": stats["user_id"],
            "tasks_count": stats["tasks_count"],
            "rating_avg": float(stats["rating_avg"]),
            "reviews_count": stats["reviews_count"]
        }

    @staticmethod
    def get_volunteer_detailed_stats(volunteer_id: str) -> Dict[str, Any]:
        """Получить детальную статистику волонтёра"""
        # Получаем базовую статистику
        basic_stats = ReviewService.get_volunteer_stats(volunteer_id)

        # Получаем распределение оценок
        distribution = ReviewRepository.get_rating_distribution(volunteer_id)

        # Получаем последние 5 отзывов
        recent_reviews_data = ReviewRepository.get_volunteer_reviews(volunteer_id, limit=5, offset=0)
        recent_reviews = [ReviewService._enrich_review(review) for review in recent_reviews_data]

        return {
            "basic": basic_stats,
            "rating_distribution": distribution,
            "recent_reviews": recent_reviews
        }

    @staticmethod
    def update_review(review_id: str, user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить отзыв (только для администратора)"""
        # Только администратор может обновлять отзывы
        if user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can update reviews"
            )

        review = ReviewRepository.get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        update_data = {}
        if "rating" in payload:
            update_data["rating"] = payload["rating"]
        if "comment" in payload:
            update_data["comment"] = payload["comment"]

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )

        updated_review = ReviewRepository.update_review(review_id, update_data)
        if not updated_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update review"
            )

        # Обновляем статистику волонтёра
        ReviewRepository.update_volunteer_stats(review["volunteer_id"])

        # Получаем обновлённый отзыв с деталями
        review_with_details = ReviewRepository.get_review_with_details(review_id)

        return ReviewService._enrich_review(review_with_details)

    @staticmethod
    def delete_review(review_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Удалить отзыв (только для администратора)"""
        # Только администратор может удалять отзывы
        if user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can delete reviews"
            )

        review = ReviewRepository.get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        volunteer_id = review["volunteer_id"]

        deleted = ReviewRepository.delete_review(review_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete review"
            )

        # Обновляем статистику волонтёра
        ReviewRepository.update_volunteer_stats(volunteer_id)

        return {
            "success": True,
            "message": "Review deleted successfully"
        }

    @staticmethod
    def get_review_by_id(review_id: str) -> Dict[str, Any]:
        """Получить отзыв по ID"""
        review = ReviewRepository.get_review_with_details(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        return ReviewService._enrich_review(review)

    @staticmethod
    def get_top_volunteers(limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ волонтёров по рейтингу"""
        supabase = get_supabase_admin()

        result = supabase.table("volunteer_stats").select("""
            *,
            user:user_id (id, name, avatar_url)
        """).gt("reviews_count", 0).order("rating_avg", desc=True).limit(limit).execute()

        top_volunteers = []
        for item in result.data or []:
            user = item.get("user") or {}
            top_volunteers.append({
                "user_id": item["user_id"],
                "name": user.get("name"),
                "avatar_url": user.get("avatar_url"),
                "tasks_count": item["tasks_count"],
                "rating_avg": float(item["rating_avg"]),
                "reviews_count": item["reviews_count"]
            })

        return top_volunteers