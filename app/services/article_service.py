from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status, UploadFile
from datetime import datetime, timezone
import uuid
import re
from app.core.database import get_supabase_admin
from app.core.config import settings
from app.db.repositories.articles import ArticlesRepository


class ArticleService:
    @staticmethod
    def _enrich_article(article: Dict[str, Any]) -> Dict[str, Any]:
        author = article.get("author") or {}

        categories = []
        for cat in article.get("categories", []):
            category = cat.get("category")
            if category:
                categories.append({"id": category.get("id"), "name": category.get("name")})

        tags = []
        for tag in article.get("tags", []):
            t = tag.get("tag")
            if t:
                tags.append({"id": t.get("id"), "name": t.get("name")})

        return {
            "id": article.get("id"),
            "title": article.get("title"),
            "content": article.get("content"),
            "cover_image": article.get("cover_image"),
            "author_id": article.get("author_id"),
            "author_name": author.get("name"),
            "author_avatar": author.get("avatar_url"),
            "pub_time": article.get("pub_time"),
            "categories": categories,
            "tags": tags,
        }

    @staticmethod
    async def upload_image(file: UploadFile) -> Dict[str, Any]:
        """Загрузить изображение для статьи (обложка или внутри текста)"""
        supabase_admin = get_supabase_admin()

        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG, PNG, WEBP, GIF are allowed"
            )

        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Max 10MB"
            )

        extension = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{extension}"
        path = f"articles/{filename}"

        try:
            supabase_admin.storage.from_(settings.ARTICLE_IMAGES_BUCKET).upload(
                path,
                file_bytes,
                {"content-type": file.content_type}
            )
            public_url = supabase_admin.storage.from_(settings.ARTICLE_IMAGES_BUCKET).get_public_url(path)

            return {"url": public_url}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(e)}"
            )

    @staticmethod
    def create_article(user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        if user.get("role") not in ["organization", "curator", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations, curators and admins can create articles"
            )

        article_data = {
            "id": str(uuid.uuid4()),
            "title": payload["title"],
            "content": payload.get("content"),
            "cover_image": payload.get("cover_image"),
            "author_id": user["id"],
            "pub_time": datetime.now(timezone.utc).isoformat(),
        }

        article = ArticlesRepository.create_article(article_data)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create article"
            )

        if payload.get("category_ids"):
            ArticlesRepository.add_categories(article["id"], payload["category_ids"])
        if payload.get("tag_ids"):
            ArticlesRepository.add_tags(article["id"], payload["tag_ids"])

        created_article = ArticlesRepository.get_article_with_details(article["id"])
        return ArticleService._enrich_article(created_article)

    @staticmethod
    def get_article(article_id: str) -> Dict[str, Any]:
        article = ArticlesRepository.get_article_with_details(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        return ArticleService._enrich_article(article)

    @staticmethod
    def update_article(article_id: str, user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        article = ArticlesRepository.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

        if article["author_id"] != user["id"] and user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own articles"
            )

        update_data = {}
        if "title" in payload:
            update_data["title"] = payload["title"]
        if "content" in payload:
            update_data["content"] = payload["content"]
        if "cover_image" in payload:
            update_data["cover_image"] = payload["cover_image"]

        if update_data:
            ArticlesRepository.update_article(article_id, update_data)

        if "category_ids" in payload:
            ArticlesRepository.add_categories(article_id, payload["category_ids"])
        if "tag_ids" in payload:
            ArticlesRepository.add_tags(article_id, payload["tag_ids"])

        updated_article = ArticlesRepository.get_article_with_details(article_id)
        return ArticleService._enrich_article(updated_article)

    @staticmethod
    def delete_article(article_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        article = ArticlesRepository.get_article_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )

        if article["author_id"] != user["id"] and user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own articles"
            )

        deleted = ArticlesRepository.delete_article(article_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete article"
            )

        return {"success": True, "message": "Article deleted successfully"}

    @staticmethod
    def list_articles(params: Dict[str, Any], limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        filters = {}

        if "search" in params and params["search"]:
            filters["search"] = params["search"]
        if "author_id" in params and params["author_id"]:
            filters["author_id"] = params["author_id"]
        if "category_id" in params and params["category_id"]:
            filters["category_id"] = params["category_id"]
        if "tag_id" in params and params["tag_id"]:
            filters["tag_id"] = params["tag_id"]

        articles = ArticlesRepository.list_articles(filters, limit, offset)
        total = ArticlesRepository.get_articles_count(filters)

        enriched_articles = []
        for article in articles:
            detailed = ArticlesRepository.get_article_with_details(article["id"])
            if detailed:
                enriched_articles.append(ArticleService._enrich_article(detailed))

        return {
            "items": enriched_articles,
            "total": total,
            "next_offset": offset + limit if offset + limit < total else None
        }

    @staticmethod
    def get_my_articles(user: Dict[str, Any], limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        filters = {"author_id": user["id"]}
        articles = ArticlesRepository.list_articles(filters, limit, offset)
        total = ArticlesRepository.get_articles_count(filters)

        enriched_articles = []
        for article in articles:
            detailed = ArticlesRepository.get_article_with_details(article["id"])
            if detailed:
                enriched_articles.append(ArticleService._enrich_article(detailed))

        return {
            "items": enriched_articles,
            "total": total,
            "next_offset": offset + limit if offset + limit < total else None
        }

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        return ArticlesRepository.get_categories()

    @staticmethod
    def create_category(name: str) -> Dict[str, Any]:
        category_data = {
            "id": str(uuid.uuid4()),
            "name": name
        }
        return ArticlesRepository.create_category(category_data)

    @staticmethod
    def get_tags() -> List[Dict[str, Any]]:
        return ArticlesRepository.get_tags()