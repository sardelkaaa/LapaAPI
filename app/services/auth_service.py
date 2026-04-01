from fastapi import HTTPException, status
from app.core.database import supabase, supabase_admin
from app.db.repositories.users import UsersRepository


class AuthService:
    from fastapi import HTTPException, status
    from app.core.database import supabase

    class AuthService:
        @staticmethod
        def register(email: str, password: str, role: str, name: str | None = None):
            if role not in ["volunteer", "curator"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role"
                )

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

            user = auth_response.user
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )

            return {
                "message": "Registration successful. Please confirm your email.",
                "user_id": user.id,
                "email": email,
                "is_active": False,
            }

    @staticmethod
    def login(email: str, password: str):
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        session = auth_response.session
        user = auth_response.user

        if not session or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Проверяем подтверждён ли email
        email_confirmed = getattr(user, "email_confirmed_at", None) is not None

        # Синхронизируем public.users.is_active
        db_user = UsersRepository.get_user_by_id(user.id)
        if not db_user:
            # если профиль вдруг не создан — создадим
            # роль здесь уже не знаем -> можно взять из user_metadata или поставить default
            UsersRepository.create_user_profile(
                user_id=user.id,
                email=user.email,
                role="volunteer",
                name=None,
            )
            db_user = UsersRepository.get_user_by_id(user.id)

        if email_confirmed and not db_user["is_active"]:
            UsersRepository.update_is_active(user.id, True)
            db_user["is_active"] = True

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "is_active": db_user["is_active"],
        }