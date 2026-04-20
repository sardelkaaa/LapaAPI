from typing import Optional, Dict, Any

from fastapi import HTTPException, UploadFile, status
from app.core.database import get_supabase_admin, supabase
from app.db.repositories.users import UsersRepository
import uuid
from app.core.config import settings


class UserService:
    @staticmethod
    def get_me(current_user: dict):
        return current_user

    @staticmethod
    def update_me(user_id: str, payload: dict):
        allowed_fields = {
            "name",
            "description",
            "phone",
            "location_text",
            "location_lat",
            "location_lng",
            "radius_preference",
            "is_urgent_available",
        }

        update_data = {k: v for k, v in payload.items() if k in allowed_fields and v is not None}

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update",
            )

        updated_user = UsersRepository.update_user_profile(user_id, update_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return updated_user

    @staticmethod
    def delete_me(user_id: str):
        supabase_admin = get_supabase_admin()

        UsersRepository.delete_user_profile(user_id)

        try:
            supabase_admin.auth.admin.delete_user(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete auth user: {str(e)}",
            )

        return {"message": "Account deleted successfully"}

    @staticmethod
    async def upload_avatar(user_id: str, file: UploadFile):
        supabase_admin = get_supabase_admin()

        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG, PNG, WEBP are allowed",
            )

        file_bytes = await file.read()
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Max 5MB",
            )

        extension = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        path = f"{user_id}/{uuid.uuid4()}.{extension}"

        try:
            supabase_admin.storage.from_(settings.AVATAR_BUCKET).upload(
                path,
                file_bytes,
                {"content-type": file.content_type}
            )

            public_url = supabase_admin.storage.from_(settings.AVATAR_BUCKET).get_public_url(path)

            updated_user = UsersRepository.update_user_profile(user_id, {"avatar_url": public_url})

            return {
                "message": "Avatar uploaded successfully",
                "avatar_url": public_url,
                "user": updated_user,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Avatar upload failed: {str(e)}",
            )

    @staticmethod
    def get_organizations(limit: int, offset: int, search: Optional[str] = None) -> Dict[str, Any]:
        """Получить список организаций с пагинацией"""
        supabase = get_supabase_admin()

        query = supabase.table("users").select("*", count="exact").eq("role", "organization")

        if search:
            query = query.ilike("name", f"%{search}%")

        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)

        result = query.execute()

        return {
            "items": result.data or [],
            "total": result.count or 0,
            "next_offset": offset + limit if offset + limit < (result.count or 0) else None
        }

    @staticmethod
    def get_user_by_id(user_id: str, current_user: dict):
        if current_user["id"] == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use /users/me to get your own profile",
            )

        user = UsersRepository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user