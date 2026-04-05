from typing import List

from fastapi import HTTPException

from app.db.repositories.users import UsersRepository
from app.db.repositories.volunteer_competencies import VolunteerCompetenciesRepository


class VolunteerService:

    @staticmethod
    def get_all_skills():
        skills = VolunteerCompetenciesRepository.get_all_skills()
        return [{"id": s["id"], "name": s["name"]} for s in skills]

    @staticmethod
    def get_all_preferences():
        preferences = VolunteerCompetenciesRepository.get_all_preferences()
        return [{"id": p["id"], "name": p["name"]} for p in preferences]

    @staticmethod
    def get_all_animal_types():
        types = VolunteerCompetenciesRepository.get_all_animal_types()
        return [{"id": t["id"], "name": t["name"]} for t in types]

    @staticmethod
    def get_volunteer_competencies(user_id: str):
        user = UsersRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        schedule = VolunteerCompetenciesRepository.get_schedule(user_id)

        schedule_list = []
        for day in schedule:
            schedule_list.append({
                "day_of_week": day["day_of_week"],
                "start_time": day["start_time"],
                "end_time": day["end_time"],
                "is_working": day.get("is_working", True)
            })

        return {
            "skills": VolunteerCompetenciesRepository.get_volunteer_skills(user_id),
            "preferences": VolunteerCompetenciesRepository.get_volunteer_preferences(user_id),
            "animal_preferences": VolunteerCompetenciesRepository.get_volunteer_animal_preferences(user_id),
            "interaction_preferences": VolunteerCompetenciesRepository.get_volunteer_interaction_preferences(user_id),
            "availability": {
                "schedule": schedule_list,
                "timezone": user.get("timezone", "UTC")
            },
        }

    @staticmethod
    def update_skills(user_id: str, skill_ids: List[str]):
        all_skills = {s["id"] for s in VolunteerCompetenciesRepository.get_all_skills()}
        invalid = [sid for sid in skill_ids if sid not in all_skills]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid skill IDs: {invalid}")

        skills = VolunteerCompetenciesRepository.set_volunteer_skills(user_id, skill_ids)
        return {"skills": skills, "message": "Skills updated"}

    @staticmethod
    def update_preferences(user_id: str, preference_ids: List[str]):
        all_prefs = {p["id"] for p in VolunteerCompetenciesRepository.get_all_preferences()}
        invalid = [pid for pid in preference_ids if pid not in all_prefs]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid preference IDs: {invalid}")

        preferences = VolunteerCompetenciesRepository.set_volunteer_preferences(user_id, preference_ids)
        return {"preferences": preferences, "message": "Preferences updated"}

    @staticmethod
    def update_animal_preferences(user_id: str, animal_type_ids: List[int]):
        all_animals = {t["id"] for t in VolunteerCompetenciesRepository.get_all_animal_types()}
        invalid = [tid for tid in animal_type_ids if tid not in all_animals]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid animal type IDs: {invalid}")

        animals = VolunteerCompetenciesRepository.set_volunteer_animal_preferences(user_id, animal_type_ids)
        return {"animal_preferences": animals, "message": "Animal preferences updated"}

    @staticmethod
    def update_interaction_preferences(user_id: str, interaction_types: List[str]):
        valid = {"shelter", "foster", "street"}
        invalid = [it for it in interaction_types if it not in valid]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid interaction types: {invalid}")

        interactions = VolunteerCompetenciesRepository.set_volunteer_interaction_preferences(user_id, interaction_types)
        return {"interaction_preferences": interactions, "message": "Interaction preferences updated"}

    @staticmethod
    def update_schedule(user_id: str, schedule: List[dict]):
        """Полностью заменить расписание"""
        for day in schedule:
            if day["day_of_week"] < 0 or day["day_of_week"] > 6:
                raise HTTPException(status_code=400, detail="day_of_week must be between 0 and 6")
            if day["start_time"] >= day["end_time"]:
                raise HTTPException(status_code=400, detail="start_time must be less than end_time")

        new_schedule = VolunteerCompetenciesRepository.set_schedule(user_id, schedule)
        return {"schedule": new_schedule, "message": "Schedule updated"}