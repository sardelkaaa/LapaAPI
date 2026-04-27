from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from app.api.v1.deps import get_current_user, require_roles
from app.services.article_service import ArticleService
from app.models.article import (
    ArticleOut, ArticleCreate, ArticleUpdate, ArticleListResponse, ImageUploadResponse, ArticleCategory,
    ArticleCategoryCreate
)
from typing import Optional

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
        file: UploadFile = File(...),
):
    """
    Загрузить изображение для статьи (обложка или внутри текста)

    Изображение сохраняется в Supabase Storage.
    Возвращает URL для вставки в редактор.
    """
    return await ArticleService.upload_image(file)

@router.get("", response_model=ArticleListResponse)
def list_articles(
        search: Optional[str] = Query(None),
        category_id: Optional[str] = Query(None),
        tag_id: Optional[str] = Query(None),
        author_id: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
):
    return ArticleService.list_articles({
        "search": search,
        "category_id": category_id,
        "tag_id": tag_id,
        "author_id": author_id
    }, limit, offset)


@router.get("/categories", response_model=list)
def get_categories():
    return ArticleService.get_categories()

@router.post("/categories", response_model=ArticleCategory)
def create_category(payload: ArticleCategoryCreate):
    return ArticleService.create_category(payload.name)

@router.get("/tags", response_model=list)
def get_tags():
    return ArticleService.get_tags()

@router.get("/me", response_model=ArticleListResponse)
def get_my_articles(
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user=Depends(get_current_user)
):
    return ArticleService.get_my_articles(current_user, limit, offset)


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: str):
    return ArticleService.get_article(article_id)

@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(
        payload: ArticleCreate,
        current_user=Depends(require_roles("admin"))
):
    return ArticleService.create_article(current_user, payload.model_dump())


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
        article_id: str,
        payload: ArticleUpdate,
        current_user=Depends(get_current_user)
):
    return ArticleService.update_article(article_id, current_user, payload.model_dump(exclude_unset=True))


@router.delete("/{article_id}")
def delete_article(
        article_id: str,
        current_user=Depends(get_current_user)
):
    return ArticleService.delete_article(article_id, current_user)