from fastapi import HTTPException, status
from app.core.database import get_supabase, supabase
from app.db.repositories.users import UsersRepository
from app.models.user import PasswordResetRequest


class AuthService:
    @staticmethod
    def register(email: str, password: str, role: str, name: str | None = None):
        if role not in ["volunteer", "curator", "organization", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role",
            )
        supabase_client = get_supabase()
        try:
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "role": role,
                        "name": name,
                    }
                }
            })

        except Exception as e:
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
        supabase_client = get_supabase()
        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception as e:
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

        db_user = UsersRepository.get_user_by_id(user.id)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        email_confirmed = getattr(user, "email_confirmed_at", None) is not None

        if email_confirmed and not db_user["is_active"]:
            updated = UsersRepository.update_is_active(user.id, True)
            if updated:
                db_user["is_active"] = True
            else:
                db_user["is_active"] = True

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "is_active": db_user["is_active"],
        }

    @staticmethod
    def sign_out():
        supabase_client = get_supabase()
        try:
            supabase_client.auth.sign_out()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}",
            )

        return {"message": "Sign out successfully"}

    @staticmethod
    def refresh_token(refresh_token: str):
        supabase_client = get_supabase()
        try:
            session = supabase_client.auth.refresh_session(refresh_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
            )
        if not session or not session.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to refresh session",
            )

        new_access_token = session.session.access_token
        new_refresh_token = session.session.refresh_token
        user = session.user

        db_user = UsersRepository.get_user_by_id(user.id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "is_active": db_user["is_active"],
        }


    # @staticmethod
    # def request_password_reset(email: str):
    #     supabase_client = get_supabase()
    #     try:
    #         response = supabase_client.auth.api.reset_password_for_email(
    #             email=email,
    #             redirect_to="https://your-frontend.com/reset-password"  # ссылка на фронтенд
    #         )
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Password reset request failed: {str(e)}",
    #         )
    #     return {"message": "Password reset email sent if user exists"}
    #
    #
    # @staticmethod
    # def update_password(access_token: str, new_password: str):
    #     supabase_client = get_supabase()
    #     try:
    #         supabase_client.auth.api.update_user(
    #             jwt=access_token,
    #             password=new_password
    #         )
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Password update failed: {str(e)}",
    #         )
    #     return {"message": "Password updated successfully"}