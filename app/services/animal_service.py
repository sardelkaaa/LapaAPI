import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.core.database import get_supabase_admin
from app.db.repositories.animals import AnimalsRepository


ALLOWED_ANIMAL_MANAGER_ROLES = {"organization", "curator"}


class AnimalService:
    @staticmethod
    def _ensure_manager_role(current_user: Dict[str, Any]) -> None:
        role = current_user.get("role")
        if role not in ALLOWED_ANIMAL_MANAGER_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization or curator can create/update/delete animals",
            )

    @staticmethod
    def _ensure_owner(current_user: Dict[str, Any], animal: Dict[str, Any]) -> None:
        if not animal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Animal not found",
            )

        if animal.get("curator_id") != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can manage only your own animals",
            )

    @staticmethod
    def _map_animal(animal: Dict[str, Any]) -> Dict[str, Any]:
        animal_type = animal.get("animals_type")

        return {
            "id": animal.get("id"),
            "name": animal.get("name"),
            "age": animal.get("age"),
            "description": animal.get("description"),

            "type_id": animal.get("type_id"),
            "type_name": animal_type.get("name") if animal_type else None,

            "curator_id": animal.get("curator_id"),

            "location_text": animal.get("location_text"),
            "location_lat": float(animal["location_lat"]) if animal.get("location_lat") is not None else None,
            "location_lng": float(animal["location_lng"]) if animal.get("location_lng") is not None else None,

            "photo_url": animal.get("photo_url"),

            "is_active": animal.get("is_active", True),

            "created_at": animal.get("created_at"),
            "updated_at": animal.get("updated_at"),
            "deleted_at": animal.get("deleted_at"),
        }

    @staticmethod
    def create_animal(current_user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        AnimalService._ensure_manager_role(current_user)

        data = payload.copy()
        data["curator_id"] = current_user["id"]

        created = AnimalsRepository.create_animal(data)
        if not created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create animal",
            )

        animal = AnimalsRepository.get_animal_by_id(created["id"])
        if not animal:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Animal created but cannot be fetched",
            )

        return AnimalService._map_animal(animal)

    @staticmethod
    def get_animal(animal_id: str) -> Dict[str, Any]:
        animal = AnimalsRepository.get_animal_by_id(animal_id)
        if not animal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Animal not found",
            )

        return AnimalService._map_animal(animal)

    @staticmethod
    def update_animal(current_user: Dict[str, Any], animal_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        AnimalService._ensure_manager_role(current_user)

        existing = AnimalsRepository.get_animal_raw(animal_id)
        AnimalService._ensure_owner(current_user, existing)

        if existing.get("deleted_at") is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Animal not found",
            )

        # Нельзя менять владельца руками
        payload.pop("curator_id", None)
        payload.pop("id", None)
        payload.pop("created_at", None)
        payload.pop("updated_at", None)
        payload.pop("deleted_at", None)

        updated = AnimalsRepository.update_animal(animal_id, payload)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update animal",
            )

        animal = AnimalsRepository.get_animal_by_id(animal_id)
        if not animal:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Animal updated but cannot be fetched",
            )

        return AnimalService._map_animal(animal)

    @staticmethod
    def delete_animal(current_user: Dict[str, Any], animal_id: str) -> Dict[str, Any]:
        AnimalService._ensure_manager_role(current_user)

        existing = AnimalsRepository.get_animal_raw(animal_id)
        AnimalService._ensure_owner(current_user, existing)

        if existing.get("deleted_at") is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Animal already deleted",
            )

        deleted = AnimalsRepository.soft_delete_animal(animal_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete animal",
            )

        return {
            "success": True,
            "message": "Animal deleted",
        }

    @staticmethod
    def list_my_animals(current_user: Dict[str, Any]) -> Dict[str, Any]:
        AnimalService._ensure_manager_role(current_user)

        items = AnimalsRepository.list_my_animals(current_user["id"])
        mapped = [AnimalService._map_animal(item) for item in items]

        return {
            "items": mapped,
            "total": len(mapped),
        }

    @staticmethod
    def list_animals(
        type_id: Optional[int] = None,
        curator_id: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> Dict[str, Any]:
        items = AnimalsRepository.list_animals(
            type_id=type_id,
            curator_id=curator_id,
            is_active=is_active,
        )
        mapped = [AnimalService._map_animal(item) for item in items]

        return {
            "items": mapped,
            "total": len(mapped),
        }

    @staticmethod
    async def upload_animal_photo(animal_id: str, current_user: dict, file: UploadFile):
        AnimalService._ensure_manager_role(current_user)

        animal = AnimalsRepository.get_animal_by_id(animal_id)
        if not animal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Animal not found"
            )

        AnimalService._ensure_owner(current_user, animal)

        supabase_admin = get_supabase_admin()

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG, PNG, WEBP are allowed"
            )

        file_bytes = await file.read()
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Max 5MB"
            )

        extension = file.filename.split(".")[-1].lower() if file.filename and "." in file.filename else "jpg"

        path = f"{current_user['id']}/{animal_id}/{uuid.uuid4()}.{extension}"

        try:
            supabase_admin.storage.from_(settings.ANIMAL_PHOTOS_BUCKET).upload(
                path,
                file_bytes,
                {"content-type": file.content_type}
            )

            public_url = supabase_admin.storage.from_(settings.ANIMAL_PHOTOS_BUCKET).get_public_url(path)

            updated = AnimalsRepository.update_animal(animal_id, {"photo_url": public_url})

            return {
                "message": "Animal photo uploaded successfully",
                "photo_url": public_url,
                "animal": updated,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Animal photo upload failed: {str(e)}"
            )