# Все настройки из переменных окружения
"""
Конфигурационный файл приложения.
Загружает все настройки из переменных окружения.
Использует Pydantic для валидации типов.
"""
import os

from pydantic_settings import BaseSettings  # Новый пакет для настроек
from typing import Optional

class Settings(BaseSettings):
    """
    Класс настроек. Pydantic автоматически загрузит значения из .env.
    """

    supabase_url: str
    supabase_key: str
    code_expiry_minutes: int = 2
    supabase_service_key: Optional[str]

    # JWT настройки
    secret_key: str = os.getenv('JWT_SECRET_KEY')
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # База данных
    database_url: str = os.getenv('DATABASE_URL')

    class Config:
        """
        Внутренний класс конфигурации Pydantic.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()