from typing import Optional

from fastapi import APIRouter, Depends, status, UploadFile, File

from app.api.v1.deps import get_current_user
from app.models.animal import (
    AnimalCreate,
    AnimalListResponse,
    AnimalOut,
    AnimalUpdate,
    AnimalDeleteResponse, AnimalPhotoUploadResponse,
)
from app.services.animal_service import AnimalService


router = APIRouter(prefix="/animals", tags=["Animals"])


@router.post("", response_model=AnimalOut, status_code=status.HTTP_201_CREATED)
def create_animal(
    payload: AnimalCreate,
    current_user: dict = Depends(get_current_user),
):
    """Создать животное. Может только организация, куратор и админ"""
    return AnimalService.create_animal(
        current_user=current_user,
        payload=payload.model_dump(exclude_none=True),
    )


@router.get("/me", response_model=AnimalListResponse)
def get_my_animals(
    current_user: dict = Depends(get_current_user),
):
    """Получить список животных текущего пользователя"""
    return AnimalService.list_my_animals(current_user)

@router.get("", response_model=AnimalListResponse)
def list_animals(
    type_id: Optional[int] = None,
    curator_id: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    """Получить список всех животных"""
    return AnimalService.list_animals(
        type_id=type_id,
        curator_id=curator_id,
        is_active=is_active,
    )


@router.get("/{animal_id}", response_model=AnimalOut)
def get_animal(animal_id: str):
    """Получить животное по id"""
    return AnimalService.get_animal(animal_id)


@router.put("/{animal_id}", response_model=AnimalOut)
def update_animal(
    animal_id: str,
    payload: AnimalUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Обновить данные у животного"""
    return AnimalService.update_animal(
        current_user=current_user,
        animal_id=animal_id,
        payload=payload.model_dump(exclude_unset=True, exclude_none=True),
    )


@router.delete("/{animal_id}", response_model=AnimalDeleteResponse)
def delete_animal(
    animal_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Удалить животное"""
    return AnimalService.delete_animal(
        current_user=current_user,
        animal_id=animal_id,
    )

@router.post("/{animal_id}/photo", response_model=AnimalPhotoUploadResponse)
async def upload_animal_photo(
    animal_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """Изменить фото животного"""
    return await AnimalService.upload_animal_photo(animal_id, current_user, file)