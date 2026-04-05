from fastapi import APIRouter, Depends, Body
from app.api.v1.deps import require_roles
from app.services.volunteer_service import VolunteerService
from app.models.competencies import (
    SkillOut, PreferenceOut, AnimalTypeOut,
    UpdateVolunteerSkillsRequest, UpdateVolunteerPreferencesRequest,
    UpdateVolunteerAnimalPreferencesRequest, UpdateVolunteerInteractionPreferencesRequest,
    VolunteerCompetenciesResponse, UpdateScheduleRequest
)
from typing import List

router = APIRouter(prefix="/volunteer", tags=["Volunteer Competencies"])

@router.get("/skills", response_model=List[SkillOut])
def get_all_skills():
    """Получить все возможные навыки"""
    return VolunteerService.get_all_skills()


@router.get("/preferences", response_model=List[PreferenceOut])
def get_all_preferences():
    """Получить все возможные предпочтения"""
    return VolunteerService.get_all_preferences()


@router.get("/animal-types", response_model=List[AnimalTypeOut])
def get_all_animal_types():
    """Получить все типы животных"""
    return VolunteerService.get_all_animal_types()

@router.get("/me/competencies", response_model=VolunteerCompetenciesResponse)
def get_my_competencies(current_user=Depends(require_roles("volunteer"))):
    """Получить полный профиль компетенций"""
    return VolunteerService.get_volunteer_competencies(current_user["id"])


@router.put("/me/skills")
def update_my_skills(
    payload: UpdateVolunteerSkillsRequest,
    current_user=Depends(require_roles("volunteer"))
):
    """Обновить навыки"""
    return VolunteerService.update_skills(current_user["id"], payload.skill_ids)


@router.put("/me/preferences")
def update_my_preferences(
    payload: UpdateVolunteerPreferencesRequest,
    current_user=Depends(require_roles("volunteer", "curator", "admin"))
):
    """Обновить предпочтения"""
    return VolunteerService.update_preferences(current_user["id"], payload.preference_ids)


@router.put("/me/animal-preferences")
def update_my_animal_preferences(
    payload: UpdateVolunteerAnimalPreferencesRequest,
    current_user=Depends(require_roles("volunteer", "curator", "admin"))
):
    """Обновить предпочтения по животным"""
    return VolunteerService.update_animal_preferences(current_user["id"], payload.animal_type_ids)


@router.put("/me/interaction-preferences")
def update_my_interaction_preferences(
    payload: UpdateVolunteerInteractionPreferencesRequest,
    current_user=Depends(require_roles("volunteer", "curator", "admin"))
):
    """Обновить предпочтения по типу взаимодействия"""
    return VolunteerService.update_interaction_preferences(current_user["id"], payload.interaction_types)

@router.put("/me/schedule")
def update_my_schedule(
    payload: UpdateScheduleRequest,
    current_user=Depends(require_roles("volunteer", "curator", "admin"))
):
    """Обновить расписание (полная замена)"""
    return VolunteerService.update_schedule(current_user["id"], [day.model_dump() for day in payload.schedule])

@router.get("/{user_id}/competencies", response_model=VolunteerCompetenciesResponse)
def get_user_competencies(
    user_id: str,
):
    """Получить компетенции любого волонтёра"""
    return VolunteerService.get_volunteer_competencies(user_id)
