from typing import Optional
from app.core.database import get_supabase_admin


class UsersRepository:
    @staticmethod
    def create_user_profile(
        user_id: str,
        email: str,
        role: str,
        name: Optional[str] = None,
    ):
        supabase_admin = get_supabase_admin()

        payload = {
            "id": user_id,
            "email": email,
            "role": role,
            "name": name,
            "is_active": False,
        }

        result = (
            supabase_admin.table("users")
            .insert(payload)
            .execute()
        )

        return result.data[0] if result.data else None

    @staticmethod
    def get_user_by_id(user_id: str):
        supabase_admin = get_supabase_admin()  # новый клиент с service_role

        result = (
            supabase_admin.table("users")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    @staticmethod
    def get_user_by_email(email: str):
        supabase_admin = get_supabase_admin()

        result = (
            supabase_admin.table("users")
            .select("*")
            .eq("email", email)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0]

        return None

    @staticmethod
    def update_is_active(user_id: str, is_active: bool):
        supabase_admin = get_supabase_admin()

        result = (
            supabase_admin.table("users")
            .update({"is_active": is_active})
            .eq("id", user_id)
            .execute()
        )

        return result.data[0] if result.data else None