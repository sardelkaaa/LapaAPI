from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["volunteer", "curator", "user", "organization"]
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    message: str
    user_id: str
    email: EmailStr
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_active: bool

class RefreshToken(BaseModel):
    refresh_token: str