from fastapi import HTTPException, status
from app.core.database import supabase
from app.db.repositories.users import UsersRepository


class AuthService:
    @staticmethod
    def register(email: str, password: str, role: str, name: str | None = None):
        if role not in ["volunteer", "curator"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )

        # 1. Регистрация в Supabase Auth
        try:
            print("[REGISTER] START")

            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "role": role,
                        "name": name,
                    }
                }
            })

            print("[REGISTER] AUTH RESPONSE:", auth_response)

        except Exception as e:
            print("[REGISTER] SUPABASE SIGN_UP ERROR:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Supabase sign_up failed: {str(e)}",
            )

        user = auth_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed",
            )

        # 2. Создание профиля в public.users
        try:
            existing_user = UsersRepository.get_user_by_id(user.id)

            if not existing_user:
                UsersRepository.create_user_profile(
                    user_id=user.id,
                    email=email,
                    role=role,
                    name=name,
                )

        except Exception as e:
            print("[REGISTER] CREATE USER PROFILE ERROR:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User profile creation failed: {str(e)}",
            )

        return {
            "message": "Registration successful. Please confirm your email.",
            "user_id": user.id,
            "email": email,
            "is_active": False,
        }

    @staticmethod
    def login(email: str, password: str):
        # 1. Логин через Supabase Auth
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception as e:
            print("[LOGIN] SUPABASE SIGN_IN ERROR:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {str(e)}",
            )

        session = auth_response.session
        user = auth_response.user

        if not session or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # 2. Проверяем, есть ли профиль в public.users
        print("[LOGIN] auth user.id =", user.id)
        print("[LOGIN] auth user.email =", user.email)

        db_user = UsersRepository.get_user_by_id(user.id)

        print("[LOGIN] db_user =", db_user)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        # 3. Проверяем подтверждение email
        email_confirmed = getattr(user, "email_confirmed_at", None) is not None

        # 4. Синхронизируем is_active после подтверждения email
        if email_confirmed and not db_user["is_active"]:
            updated = UsersRepository.update_is_active(user.id, True)
            if updated:
                db_user["is_active"] = True
            else:
                db_user["is_active"] = True  # локально на случай пустого ответа

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "is_active": db_user["is_active"],
        }