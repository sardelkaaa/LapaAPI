from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ArticleCategory(BaseModel):
    """Категория статьи"""
    id: str = Field(..., description="UUID категории", example="550e8400-e29b-41d4-a716-446655440000")
    name: str = Field(..., description="Название категории", example="Помощь животным")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Помощь животным"
            }
        }

class ArticleCategoryCreate(BaseModel):
    name: str = Field(..., description="Название категории", example="Помощь животным")
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Помощь животным"
            }
        }

class ArticleTag(BaseModel):
    """Тег статьи"""
    id: str = Field(..., description="UUID тега", example="660e8400-e29b-41d4-a716-446655440001")
    name: str = Field(..., description="Название тега", example="волонтёрство")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "волонтёрство"
            }
        }


class ArticleOut(BaseModel):
    """Полная информация о статье (ответ API)"""
    id: str = Field(..., description="UUID статьи", example="770e8400-e29b-41d4-a716-446655440002")
    title: str = Field(..., description="Заголовок статьи", example="Как помочь бездомным животным")
    content: Optional[str] = Field(
        None,
        description="Содержание статьи в формате HTML",
        example="<p>В этой статье мы расскажем, как можно помочь бездомным животным...</p><img src='https://storage.supabase.co/article-images/photo.jpg'/><p>Продолжение статьи...</p>"
    )
    cover_image: Optional[str] = Field(
        None,
        description="URL обложки статьи",
        example="https://storage.supabase.co/article-images/cover.jpg"
    )
    author_id: str = Field(..., description="UUID автора", example="880e8400-e29b-41d4-a716-446655440003")
    author_name: Optional[str] = Field(None, description="Имя автора", example="Анна Смирнова")
    author_avatar: Optional[str] = Field(None, description="Аватар автора",
                                         example="https://storage.supabase.co/avatars/anna.jpg")
    pub_time: datetime = Field(..., description="Дата публикации", example="2025-04-24T10:30:00Z")
    categories: List[ArticleCategory] = Field(default=[], description="Список категорий")
    tags: List[ArticleTag] = Field(default=[], description="Список тегов")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "title": "Как помочь бездомным животным",
                "content": "<p>В этой статье мы расскажем, как можно помочь бездомным животным...</p><img src='https://storage.supabase.co/article-images/photo.jpg'/><p>Продолжение статьи...</p>",
                "cover_image": "https://storage.supabase.co/article-images/cover.jpg",
                "author_id": "880e8400-e29b-41d4-a716-446655440003",
                "author_name": "Анна Смирнова",
                "author_avatar": "https://storage.supabase.co/avatars/anna.jpg",
                "pub_time": "2025-04-24T10:30:00Z",
                "categories": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Помощь животным"
                    }
                ],
                "tags": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "name": "волонтёрство"
                    },
                    {
                        "id": "990e8400-e29b-41d4-a716-446655440004",
                        "name": "приюты"
                    }
                ]
            }
        }


class ArticleCreate(BaseModel):
    """Создание новой статьи"""
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Заголовок статьи",
        example="Как помочь бездомным животным"
    )
    content: Optional[str] = Field(
        None,
        description="Содержание статьи в формате HTML",
        example="<p>В этой статье мы расскажем, как можно помочь бездомным животным...</p>"
    )
    cover_image: Optional[str] = Field(
        None,
        description="URL обложки статьи (полученный после загрузки)",
        example="https://storage.supabase.co/article-images/cover.jpg"
    )
    category_ids: List[str] = Field(
        default=[],
        description="Список UUID категорий",
        example=["550e8400-e29b-41d4-a716-446655440000"]
    )
    tag_ids: List[str] = Field(
        default=[],
        description="Список UUID тегов",
        example=["660e8400-e29b-41d4-a716-446655440001", "990e8400-e29b-41d4-a716-446655440004"]
    )

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Как помочь бездомным животным",
                "content": "<p>В этой статье мы расскажем, как можно помочь бездомным животным...</p><img src='https://storage.supabase.co/article-images/photo.jpg'/>",
                "cover_image": "https://storage.supabase.co/article-images/cover.jpg",
                "category_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "tag_ids": ["660e8400-e29b-41d4-a716-446655440001", "990e8400-e29b-41d4-a716-446655440004"]
            }
        }


class ArticleUpdate(BaseModel):
    """Обновление статьи"""
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Новый заголовок статьи",
        example="Обновлённый заголовок статьи"
    )
    content: Optional[str] = Field(
        None,
        description="Новое содержание статьи",
        example="<p>Обновлённое содержание статьи...</p>"
    )
    cover_image: Optional[str] = Field(
        None,
        description="Новый URL обложки",
        example="https://storage.supabase.co/article-images/new-cover.jpg"
    )
    category_ids: Optional[List[str]] = Field(
        None,
        description="Новый список UUID категорий",
        example=["550e8400-e29b-41d4-a716-446655440000", "aa0e8400-e29b-41d4-a716-446655440005"]
    )
    tag_ids: Optional[List[str]] = Field(
        None,
        description="Новый список UUID тегов",
        example=["660e8400-e29b-41d4-a716-446655440001"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Обновлённый заголовок статьи",
                "content": "<p>Обновлённое содержание статьи...</p>",
                "cover_image": "https://storage.supabase.co/article-images/new-cover.jpg",
                "category_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "tag_ids": ["660e8400-e29b-41d4-a716-446655440001"]
            }
        }


class ArticleListResponse(BaseModel):
    """Список статей с пагинацией"""
    items: List[ArticleOut] = Field(..., description="Список статей")
    total: int = Field(..., description="Общее количество статей", example=42)
    next_offset: Optional[int] = Field(
        None,
        description="Смещение для следующей страницы (null, если больше нет)",
        example=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440002",
                        "title": "Как помочь бездомным животным",
                        "content": "<p>В этой статье мы расскажем, как можно помочь...</p>",
                        "cover_image": "https://storage.supabase.co/article-images/cover.jpg",
                        "author_id": "880e8400-e29b-41d4-a716-446655440003",
                        "author_name": "Анна Смирнова",
                        "author_avatar": "https://storage.supabase.co/avatars/anna.jpg",
                        "pub_time": "2025-04-24T10:30:00Z",
                        "categories": [{"id": "cat1", "name": "Помощь животным"}],
                        "tags": [{"id": "tag1", "name": "волонтёрство"}]
                    }
                ],
                "total": 1,
                "next_offset": None
            }
        }


class ImageUploadResponse(BaseModel):
    """Ответ после загрузки изображения"""
    url: str = Field(
        ...,
        description="Публичный URL загруженного изображения",
        example="https://storage.supabase.co/article-images/550e8400-e29b-41d4-a716-446655440000.jpg"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://storage.supabase.co/article-images/550e8400-e29b-41d4-a716-446655440000.jpg"
            }
        }