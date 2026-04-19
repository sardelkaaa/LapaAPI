from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.v1.deps import get_current_user, require_roles
from app.services.review_service import ReviewService
from app.models.review import (
    ReviewOut,
    ReviewCreate,
    ReviewUpdate,
    ReviewListResponse,
    VolunteerStatsOut,
    VolunteerDetailedStats
)
from typing import List

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
        payload: ReviewCreate,
        current_user=Depends(require_roles("curator", "organization", "admin"))
):
    """
    Создать отзыв на волонтёра

    Только куратор, организация или администратор могут оставлять отзывы.
    Отзыв можно оставить только на завершённую задачу.
    """
    return ReviewService.create_review(current_user, payload.model_dump())


@router.get("/volunteer/{volunteer_id}", response_model=ReviewListResponse)
def get_volunteer_reviews(
        volunteer_id: str,
        limit: int = Query(20, ge=1, le=100, description="Количество отзывов на странице"),
        offset: int = Query(0, ge=0, description="Смещение для пагинации")
):
    """Получить все отзывы о волонтёре"""
    return ReviewService.get_volunteer_reviews(volunteer_id, limit, offset)


@router.get("/volunteer/{volunteer_id}/stats", response_model=VolunteerStatsOut)
def get_volunteer_stats(
        volunteer_id: str
):
    """Получить базовую статистику волонтёра"""
    return ReviewService.get_volunteer_stats(volunteer_id)


@router.get("/volunteer/{volunteer_id}/detailed-stats", response_model=VolunteerDetailedStats)
def get_volunteer_detailed_stats(
        volunteer_id: str
):
    """
    Получить детальную статистику волонтёра

    Включает базовую статистику, распределение оценок и последние отзывы.
    """
    return ReviewService.get_volunteer_detailed_stats(volunteer_id)


@router.get("/me", response_model=ReviewListResponse)
def get_my_reviews(
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user=Depends(require_roles("volunteer"))
):
    """Получить отзывы о текущем волонтёре"""
    return ReviewService.get_volunteer_reviews(current_user["id"], limit, offset)


@router.get("/me/stats", response_model=VolunteerStatsOut)
def get_my_stats(
        current_user=Depends(require_roles("volunteer"))
):
    """Получить статистику текущего волонтёра"""
    return ReviewService.get_volunteer_stats(current_user["id"])


@router.get("/me/detailed-stats", response_model=VolunteerDetailedStats)
def get_my_detailed_stats(
        current_user=Depends(require_roles("volunteer"))
):
    """Получить детальную статистику текущего волонтёра"""
    return ReviewService.get_volunteer_detailed_stats(current_user["id"])


@router.get("/top-volunteers", response_model=List[dict])
def get_top_volunteers(
        limit: int = Query(10, ge=1, le=50, description="Количество волонтёров"),
):
    """Получить топ волонтёров по рейтингу"""
    return ReviewService.get_top_volunteers(limit)


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(
        review_id: str,
):
    """Получить отзыв по ID"""
    return ReviewService.get_review_by_id(review_id)


@router.put("/{review_id}", response_model=ReviewOut)
def update_review(
        review_id: str,
        payload: ReviewUpdate,
        current_user=Depends(require_roles("admin"))
):
    """
    Обновить отзыв

    Только администратор может обновлять отзывы.
    """
    return ReviewService.update_review(review_id, current_user, payload.model_dump(exclude_unset=True))


@router.delete("/{review_id}")
def delete_review(
        review_id: str,
        current_user=Depends(require_roles("admin"))
):
    """
    Удалить отзыв

    Только администратор может удалять отзывы.
    """
    return ReviewService.delete_review(review_id, current_user)