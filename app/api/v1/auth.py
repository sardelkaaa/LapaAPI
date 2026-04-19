from fastapi import APIRouter

from app.models.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, RefreshToken
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    """Регистрация"""
    return AuthService.register(
        email=payload.email,
        password=payload.password,
        role=payload.role,
        name=payload.name,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Авторизация"""
    return AuthService.login(
        email=payload.email,
        password=payload.password,
    )

@router.post("/sign_out")
def sign_out():
    """Выход"""
    return AuthService.sign_out()

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshToken):
    """Получение нового refresh-токена"""
    return AuthService.refresh_token(
        refresh_token=payload.refresh_token
    )


# @router.post("/reset-password")
# def request_reset_password(payload: PasswordResetRequest):
#     return AuthService.request_password_reset(payload.email)