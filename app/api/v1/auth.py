from fastapi import APIRouter, Depends

from app.core.config import settings
from app.db.repositories.users import UsersRepository
from app.models.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from app.models.user import UserOut
from app.services.auth_service import AuthService
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    return AuthService.register(
        email=payload.email,
        password=payload.password,
        role=payload.role,
        name=payload.name,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return AuthService.login(
        email=payload.email,
        password=payload.password,
    )


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user