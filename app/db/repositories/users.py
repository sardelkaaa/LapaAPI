from typing import Optional
from app.core.database import supabase_admin


class UsersRepository:
    @staticmethod
    def create_user_profile(
        user_id: str,
        email: str,
        role: str,
        name: Optional[str] = None,
    ):
        payload = {
            "id": user_id,
            "email": email,
            "role": role,
            "name": name,
            "is_active": False,  # до подтверждения email
        }

        result = (
            supabase_admin.table("users")
            .insert(payload)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def get_user_by_id(user_id: str):
        result = (
            supabase_admin.table("users")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return result.data

    @staticmethod
    def get_user_by_email(email: str):
        result = (
            supabase_admin.table("users")
            .select("*")
            .eq("email", email)
            .single()
            .execute()
        )
        return result.data

    @staticmethod
    def update_is_active(user_id: str, is_active: bool):
        result = (
            supabase_admin.table("users")
            .update({"is_active": is_active})
            .eq("id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None