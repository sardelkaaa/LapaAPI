from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.database import get_supabase


class AnimalsRepository:
    @staticmethod
    def create_animal(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase_client = get_supabase()
        result = supabase_client.table("animals").insert(data).execute()
        if not result.data:
            return None
        return result.data[0]

    @staticmethod
    def get_animal_by_id(animal_id: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        supabase_client = get_supabase()
        query = (
            supabase_client.table("animals")
            .select("""
                id,
                name,
                age,
                description,
                type_id,
                curator_id,
                location_text,
                location_lat,
                location_lng,
                photo_url,
                created_at,
                updated_at,
                deleted_at,
                is_active,
                animals_type (
                    id,
                    name
                )
            """)
            .eq("id", animal_id)
            .limit(1)
        )

        if not include_deleted:
            query = query.is_("deleted_at", "null")

        result = query.execute()

        if not result.data:
            return None

        return result.data[0]

    @staticmethod
    def get_animal_raw(animal_id: str) -> Optional[Dict[str, Any]]:
        supabase_client = get_supabase()
        result = (
            supabase_client.table("animals")
            .select("*")
            .eq("id", animal_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]

    @staticmethod
    def update_animal(animal_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase_client = get_supabase()
        result = (
            supabase_client.table("animals")
            .update(data)
            .eq("id", animal_id)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]

    @staticmethod
    def soft_delete_animal(animal_id: str) -> Optional[Dict[str, Any]]:
        supabase_client = get_supabase()
        result = (
            supabase_client.table("animals")
            .update({
                "deleted_at": datetime.now(timezone.utc).isoformat(),
                "is_active": False,
            })
            .eq("id", animal_id)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]

    @staticmethod
    def list_my_animals(user_id: str) -> List[Dict[str, Any]]:
        supabase_client = get_supabase()
        result = (
            supabase_client.table("animals")
            .select("""
                id,
                name,
                age,
                description,
                type_id,
                curator_id,
                location_text,
                location_lat,
                location_lng,
                photo_url,
                created_at,
                updated_at,
                deleted_at,
                is_active,
                animals_type (
                    id,
                    name
                )
            """)
            .eq("curator_id", user_id)
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )

        return result.data or []

    @staticmethod
    def list_animals(
        type_id: Optional[int] = None,
        curator_id: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> List[Dict[str, Any]]:
        supabase_client = get_supabase()
        query = (
            supabase_client.table("animals")
            .select("""
                id,
                name,
                age,
                description,
                type_id,
                curator_id,
                location_text,
                location_lat,
                location_lng,
                photo_url,
                created_at,
                updated_at,
                deleted_at,
                is_active,
                animals_type (
                    id,
                    name
                )
            """)
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
        )

        if type_id is not None:
            query = query.eq("type_id", type_id)

        if curator_id is not None:
            query = query.eq("curator_id", curator_id)

        if is_active is not None:
            query = query.eq("is_active", is_active)

        result = query.execute()
        return result.data or []