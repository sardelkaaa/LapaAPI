# Подключение к Supabase/БД
"""
Настройка подключения к Supabase.
Supabase предоставляет не только базу данных, но и:
- Аутентификацию (встроенную)
- Хранилище файлов
- Realtime подписки
"""

from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)

supabase_admin: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_supabase() -> Client:
    """
    Dependency для FastAPI.

    Зачем нужна функция-обертка, если у нас уже есть supabase?
    - Для инъекции зависимостей (dependency injection)
    - FastAPI будет автоматически управлять жизненным циклом
    - Легче подменять на мок-объекты при тестировании
    """
    return supabase

def get_supabase_admin() -> Client:
    return supabase_admin