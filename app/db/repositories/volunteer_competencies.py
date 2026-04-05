from typing import List
from app.core.database import get_supabase_admin


class VolunteerCompetenciesRepository:

    @staticmethod
    def get_all_skills() -> List[dict]:
        supabase = get_supabase_admin()
        result = supabase.table("skills").select("*").execute()
        return result.data if result.data else []

    @staticmethod
    def get_volunteer_skills(user_id: str) -> List[dict]:
        supabase = get_supabase_admin()
        result = (
            supabase.table("volunteers_skills")
            .select("skill_id, skills(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return [item["skills"] for item in result.data if item.get("skills")] if result.data else []

    @staticmethod
    def set_volunteer_skills(user_id: str, skill_ids: List[str]):
        supabase = get_supabase_admin()
        supabase.table("volunteers_skills").delete().eq("user_id", user_id).execute()
        if skill_ids:
            records = [{"user_id": user_id, "skill_id": sid} for sid in skill_ids]
            supabase.table("volunteers_skills").insert(records).execute()
        return VolunteerCompetenciesRepository.get_volunteer_skills(user_id)

    @staticmethod
    def get_all_preferences() -> List[dict]:
        supabase = get_supabase_admin()
        result = supabase.table("preferences").select("*").execute()
        return result.data if result.data else []

    @staticmethod
    def get_volunteer_preferences(user_id: str) -> List[dict]:
        supabase = get_supabase_admin()
        result = (
            supabase.table("volunteers_preferences")
            .select("preference_id, preferences(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return [item["preferences"] for item in result.data if item.get("preferences")] if result.data else []

    @staticmethod
    def set_volunteer_preferences(user_id: str, preference_ids: List[str]):
        supabase = get_supabase_admin()
        supabase.table("volunteers_preferences").delete().eq("user_id", user_id).execute()
        if preference_ids:
            records = [{"user_id": user_id, "preference_id": pid} for pid in preference_ids]
            supabase.table("volunteers_preferences").insert(records).execute()
        return VolunteerCompetenciesRepository.get_volunteer_preferences(user_id)

    @staticmethod
    def get_all_animal_types() -> List[dict]:
        supabase = get_supabase_admin()
        result = supabase.table("animals_type").select("*").execute()
        return result.data if result.data else []

    @staticmethod
    def get_volunteer_animal_preferences(user_id: str) -> List[dict]:
        supabase = get_supabase_admin()
        result = (
            supabase.table("volunteer_animal_preferences")
            .select("animal_type_id, animals_type(*)")
            .eq("user_id", user_id)
            .execute()
        )
        return [item["animals_type"] for item in result.data if item.get("animals_type")] if result.data else []

    @staticmethod
    def set_volunteer_animal_preferences(user_id: str, animal_type_ids: List[int]):
        supabase = get_supabase_admin()
        supabase.table("volunteer_animal_preferences").delete().eq("user_id", user_id).execute()
        if animal_type_ids:
            records = [{"user_id": user_id, "animal_type_id": tid} for tid in animal_type_ids]
            supabase.table("volunteer_animal_preferences").insert(records).execute()
        return VolunteerCompetenciesRepository.get_volunteer_animal_preferences(user_id)

    @staticmethod
    def get_volunteer_interaction_preferences(user_id: str) -> List[str]:
        supabase = get_supabase_admin()
        result = (
            supabase.table("volunteer_interaction_preferences")
            .select("interaction_type")
            .eq("user_id", user_id)
            .execute()
        )
        return [item["interaction_type"] for item in result.data] if result.data else []

    @staticmethod
    def set_volunteer_interaction_preferences(user_id: str, interaction_types: List[str]):
        supabase = get_supabase_admin()
        supabase.table("volunteer_interaction_preferences").delete().eq("user_id", user_id).execute()
        if interaction_types:
            records = [{"user_id": user_id, "interaction_type": it} for it in interaction_types]
            supabase.table("volunteer_interaction_preferences").insert(records).execute()
        return VolunteerCompetenciesRepository.get_volunteer_interaction_preferences(user_id)

    @staticmethod
    def get_schedule(user_id: str) -> List[dict]:
        """Получить всё расписание волонтёра"""
        supabase = get_supabase_admin()
        result = (
            supabase.table("volunteer_schedules")
            .select("*")
            .eq("user_id", user_id)
            .order("day_of_week")
            .execute()
        )
        return result.data if result.data else []

    @staticmethod
    def set_schedule(user_id: str, schedule: List[dict]):
        """Полностью заменить расписание волонтёра"""
        supabase = get_supabase_admin()

        supabase.table("volunteer_schedules").delete().eq("user_id", user_id).execute()

        if schedule:
            records = []
            for day in schedule:
                start_time = day["start_time"]
                end_time = day["end_time"]
                if hasattr(start_time, 'strftime'):
                    start_time = start_time.strftime("%H:%M:%S")
                if hasattr(end_time, 'strftime'):
                    end_time = end_time.strftime("%H:%M:%S")

                records.append({
                    "user_id": user_id,
                    "day_of_week": day["day_of_week"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "is_working": day.get("is_working", True)
                })

        return VolunteerCompetenciesRepository.get_schedule(user_id)

    @staticmethod
    def update_single_day(user_id: str, day_of_week: int, start_time: str, end_time: str, is_working: bool = True):
        """Обновить расписание на конкретный день"""
        supabase = get_supabase_admin()

        supabase.table("volunteer_schedules").delete().eq("user_id", user_id).eq("day_of_week", day_of_week).execute()

        if is_working:
            supabase.table("volunteer_schedules").insert({
                "user_id": user_id,
                "day_of_week": day_of_week,
                "start_time": start_time,
                "end_time": end_time,
                "is_working": True
            }).execute()

        return VolunteerCompetenciesRepository.get_schedule(user_id)