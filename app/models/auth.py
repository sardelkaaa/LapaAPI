from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class RegisterRequest(BaseModel):
    """Данные регистрации"""
    email: EmailStr = Field(..., example="new.user@example.com")
    password: str = Field(min_length=8, max_length=128, example="SecurePass123!")
    role: Literal["volunteer", "curator", "user", "organization"] = Field(..., example="volunteer")
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="Анна Смирнова")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "anna.smirnova@example.com",
                "password": "StrongP@ssw0rd123",
                "role": "volunteer",
                "name": "Анна Смирнова"
            }
        }


class LoginRequest(BaseModel):
    """Данные для входа"""
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePass123!")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "ivan.volunteer@example.com",
                "password": "MySecretPassword123"
            }
        }


class RegisterResponse(BaseModel):
    """Ответ на регистрацию"""
    message: str = Field(..., example="User registered successfully")
    user_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    email: EmailStr = Field(..., example="new.user@example.com")
    is_active: bool = Field(..., example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "anna.smirnova@example.com",
                "is_active": True
            }
        }


class TokenResponse(BaseModel):
    """Ответ на вход"""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6InJlZnJlc2giLCJpYXQiOjE1MTYyMzkwMjJ9.nPGZ3x3fQ8XqMqY6fZKJ2YQxR5lKQpC5uJk7aKcR8tA")
    token_type: str = Field("bearer", example="bearer")
    is_active: bool = Field(..., example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6Iml2YW4udm9sdW50ZWVyQGV4YW1wbGUuY29tIiwicm9sZSI6InZvbHVudGVlciIsImV4cCI6MTczNzIzNDU2N30.xKj8QnR5VpL2MqW9YfZKJ2YQxR5lKQpC5uJk7aKcR8tA",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzMyMDk2N30.qW9YfZKJ2YQxR5lKQpC5uJk7aKcR8tA",
                "token_type": "bearer",
                "is_active": True
            }
        }
class RefreshToken(BaseModel):
    """Данные для обновления токена"""
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzMyMDk2N30.qW9YfZKJ2YQxR5lKQpC5uJk7aKcR8tA")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzMyMDk2N30.qW9YfZKJ2YQxR5lKQpC5uJk7aKcR8tA"
            }
        }