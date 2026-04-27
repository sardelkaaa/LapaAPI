from app.core.database import get_supabase_admin, supabase, supabase_admin
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid


class ArticlesRepository:
    @staticmethod
    def create_article(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("articles").insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_article_by_id(article_id: str) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_article_with_details(article_id: str) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()

        result = supabase.table("articles").select("""
            *,
            author:author_id (id, name, avatar_url)
        """).eq("id", article_id).limit(1).execute()

        if not result.data:
            return None

        article = result.data[0]

        categories_result = supabase.table("articles_category").select("""
            category_id,
            category:category_id (id, name)
        """).eq("articles_id", article_id).execute()
        article["categories"] = categories_result.data or []

        tags_result = supabase.table("articles_tags").select("""
            tags_id,
            tag:tags_id (id, name)
        """).eq("articles_id", article_id).execute()
        article["tags"] = tags_result.data or []

        return article

    @staticmethod
    def update_article(article_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("articles").update(data).eq("id", article_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def delete_article(article_id: str) -> bool:
        supabase = get_supabase_admin()
        result = supabase.table("articles").delete().eq("id", article_id).execute()
        return len(result.data or []) > 0

    @staticmethod
    def list_articles(filters: Dict[str, Any], limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        supabase = get_supabase_admin()
        query = supabase.table("articles").select("*", count="exact")

        if "author_id" in filters:
            query = query.eq("author_id", filters["author_id"])

        if "search" in filters and filters["search"]:
            query = query.ilike("title", f"%{filters['search']}%")

        if "category_id" in filters and filters["category_id"]:
            cat_articles = supabase.table("articles_category").select("articles_id").eq("category_id", filters[
                "category_id"]).execute()
            article_ids = [item["articles_id"] for item in cat_articles.data] if cat_articles.data else []
            if article_ids:
                query = query.in_("id", article_ids)
            else:
                return []

        if "tag_id" in filters and filters["tag_id"]:
            tag_articles = supabase.table("articles_tags").select("articles_id").eq("tags_id",
                                                                                    filters["tag_id"]).execute()
            article_ids = [item["articles_id"] for item in tag_articles.data] if tag_articles.data else []
            if article_ids:
                query = query.in_("id", article_ids)
            else:
                return []

        query = query.order("pub_time", desc=True)
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []

    @staticmethod
    def get_articles_count(filters: Dict[str, Any]) -> int:
        supabase = get_supabase_admin()
        query = supabase.table("articles").select("*", count="exact")

        if "author_id" in filters:
            query = query.eq("author_id", filters["author_id"])

        if "category_id" in filters and filters["category_id"]:
            cat_articles = supabase.table("articles_category").select("articles_id").eq("category_id", filters[
                "category_id"]).execute()
            article_ids = [item["articles_id"] for item in cat_articles.data] if cat_articles.data else []
            if article_ids:
                query = query.in_("id", article_ids)
            else:
                return 0

        if "tag_id" in filters and filters["tag_id"]:
            tag_articles = supabase.table("articles_tags").select("articles_id").eq("tags_id",
                                                                                    filters["tag_id"]).execute()
            article_ids = [item["articles_id"] for item in tag_articles.data] if tag_articles.data else []
            if article_ids:
                query = query.in_("id", article_ids)
            else:
                return 0

        result = query.execute()
        return result.count or 0

    @staticmethod
    def add_categories(article_id: str, category_ids: List[str]) -> None:
        supabase = get_supabase_admin()
        if not category_ids:
            return
        supabase.table("articles_category").delete().eq("articles_id", article_id).execute()
        records = [{"articles_id": article_id, "category_id": cid} for cid in category_ids]
        supabase.table("articles_category").insert(records).execute()

    @staticmethod
    def add_tags(article_id: str, tag_ids: List[str]) -> None:
        supabase = get_supabase_admin()
        if not tag_ids:
            return
        supabase.table("articles_tags").delete().eq("articles_id", article_id).execute()
        records = [{"articles_id": article_id, "tags_id": tid} for tid in tag_ids]
        supabase.table("articles_tags").insert(records).execute()

    @staticmethod
    def create_category(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("categories").insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("categories").select("*").order("name").execute()
        return result.data or []

    @staticmethod
    def get_tags() -> List[Dict[str, Any]]:
        supabase = get_supabase_admin()
        result = supabase.table("tags").select("*").order("name").execute()
        return result.data or []