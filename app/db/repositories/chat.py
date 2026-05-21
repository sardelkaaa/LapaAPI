from typing import Optional, List, Dict, Any
from uuid import UUID
from app.core.database import get_supabase_admin
from datetime import datetime, timezone


class ChatRepository:

    @staticmethod
    def get_or_create_direct_chat(user1_id: UUID, user2_id: UUID) -> Dict[str, Any]:
        """Получить или создать прямой чат между двумя пользователями"""
        supabase = get_supabase_admin()

        # Ищем существующий чат
        rooms_result = supabase.table("chat_room_members") \
            .select("room_id") \
            .eq("user_id", str(user1_id)) \
            .execute()

        if rooms_result.data:
            room_ids = [r["room_id"] for r in rooms_result.data]

            for room_id in room_ids:
                members = supabase.table("chat_room_members") \
                    .select("user_id") \
                    .eq("room_id", room_id) \
                    .execute()
                member_ids = [m["user_id"] for m in members.data]
                if str(user2_id) in member_ids:
                    return ChatRepository.get_chat_by_id(UUID(room_id), user1_id)

        # Создаём новый чат
        room_result = supabase.table("chat_rooms").insert({
            'title': None
        }).execute()

        if not room_result.data:
            raise Exception("Failed to create chat room")

        room_id = room_result.data[0]['id']

        supabase.table("chat_room_members").insert([
            {'room_id': room_id, 'user_id': str(user1_id)},
            {'room_id': room_id, 'user_id': str(user2_id)}
        ]).execute()

        return ChatRepository.get_chat_by_id(UUID(room_id), user1_id)

    @staticmethod
    def get_user_chats(user_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Получить все чаты пользователя"""
        supabase = get_supabase_admin()

        # Получаем комнаты пользователя
        rooms_result = supabase.table("chat_room_members") \
            .select("room_id, last_read_at, chat_rooms!inner(id, title, created_at)") \
            .eq("user_id", str(user_id)) \
            .execute()

        if not rooms_result.data:
            return {'items': [], 'total': 0}

        chats = []
        for room in rooms_result.data:
            chat_room = room.get("chat_rooms", {})
            if not chat_room:
                continue

            room_id = chat_room.get("id")

            # Получаем другого участника
            other_member = supabase.table("chat_room_members") \
                .select("user_id, users!inner(id, name, avatar_url)") \
                .eq("room_id", room_id) \
                .neq("user_id", str(user_id)) \
                .limit(1) \
                .execute()

            other_user_data = None
            other_user_id = None
            other_user_name = None
            other_user_avatar = None

            if other_member.data:
                other = other_member.data[0]
                other_user_id = other.get("user_id")
                user_info = other.get("users", {})
                other_user_name = user_info.get("name")
                other_user_avatar = user_info.get("avatar_url")

            # Получаем последнее сообщение
            last_msg = supabase.table("chat_messages") \
                .select("*") \
                .eq("room_id", room_id) \
                .eq("is_deleted", False) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()

            last_message = last_msg.data[0] if last_msg.data else None

            # Считаем непрочитанные
            last_read_at = room.get("last_read_at")
            unread_query = supabase.table("chat_messages") \
                .select("*", count="exact") \
                .eq("room_id", room_id) \
                .eq("is_deleted", False) \
                .neq("sender_id", str(user_id))

            if last_read_at:
                unread_query = unread_query.gt("created_at", last_read_at)

            unread_result = unread_query.execute()
            unread_count = unread_result.count or 0

            chats.append({
                "id": room_id,
                "title": chat_room.get("title"),
                "created_at": chat_room.get("created_at"),
                "other_user_id": other_user_id,
                "other_user_name": other_user_name,
                "other_user_avatar": other_user_avatar,
                "last_message": last_message.get("content") if last_message else None,
                "last_message_time": last_message.get("created_at") if last_message else None,
                "unread_count": unread_count
            })

        # Сортируем по последнему сообщению
        chats.sort(key=lambda x: x.get("last_message_time") or x.get("created_at") or "", reverse=True)

        # Пагинация
        total = len(chats)
        paginated = chats[offset:offset + limit]

        return {
            'items': paginated,
            'total': total
        }

    @staticmethod
    def get_chat_by_id(chat_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить чат по ID с проверкой доступа"""
        supabase = get_supabase_admin()

        # Проверяем, что пользователь участник комнаты
        member_check = supabase.table("chat_room_members") \
            .select("user_id, last_read_at") \
            .eq("room_id", str(chat_id)) \
            .eq("user_id", str(user_id)) \
            .limit(1) \
            .execute()

        if not member_check.data:
            return None

        user_last_read = member_check.data[0].get("last_read_at")

        # Получаем информацию о комнате
        room_result = supabase.table("chat_rooms") \
            .select("*") \
            .eq("id", str(chat_id)) \
            .limit(1) \
            .execute()

        if not room_result.data:
            return None

        room = room_result.data[0]

        # Получаем другого участника
        other_member = supabase.table("chat_room_members") \
            .select("user_id, users!inner(id, name, avatar_url)") \
            .eq("room_id", str(chat_id)) \
            .neq("user_id", str(user_id)) \
            .limit(1) \
            .execute()

        other_user_id = None
        other_user_name = None
        other_user_avatar = None

        if other_member.data:
            other = other_member.data[0]
            other_user_id = other.get("user_id")
            user_info = other.get("users", {})
            other_user_name = user_info.get("name")
            other_user_avatar = user_info.get("avatar_url")

        # Получаем последнее сообщение
        last_msg = supabase.table("chat_messages") \
            .select("*") \
            .eq("room_id", str(chat_id)) \
            .eq("is_deleted", False) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        last_message = last_msg.data[0] if last_msg.data else None

        # Считаем непрочитанные
        unread_query = supabase.table("chat_messages") \
            .select("*", count="exact") \
            .eq("room_id", str(chat_id)) \
            .eq("is_deleted", False) \
            .neq("sender_id", str(user_id))

        if user_last_read:
            unread_query = unread_query.gt("created_at", user_last_read)

        unread_result = unread_query.execute()
        unread_count = unread_result.count or 0

        return {
            "id": room.get("id"),
            "title": room.get("title"),
            "created_at": room.get("created_at"),
            "other_user_id": other_user_id,
            "other_user_name": other_user_name,
            "other_user_avatar": other_user_avatar,
            "last_message": last_message.get("content") if last_message else None,
            "last_message_time": last_message.get("created_at") if last_message else None,
            "unread_count": unread_count
        }

    @staticmethod
    def get_chat_messages(chat_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Получить сообщения чата"""
        supabase = get_supabase_admin()

        result = supabase.table("chat_messages") \
            .select("*, sender:sender_id(id, name, avatar_url)") \
            .eq("room_id", str(chat_id)) \
            .eq("is_deleted", False) \
            .order("created_at", desc=False) \
            .range(offset, offset + limit - 1) \
            .execute()

        items = []
        for msg in result.data or []:
            sender = msg.get("sender", {})
            items.append({
                "id": msg.get("id"),
                "room_id": msg.get("room_id"),
                "sender_id": msg.get("sender_id"),
                "sender_name": sender.get("name"),
                "sender_avatar": sender.get("avatar_url"),
                "content": msg.get("content"),
                "message_type": msg.get("message_type", "text"),
                "attachment_url": msg.get("attachment_url"),
                "created_at": msg.get("created_at"),
                "updated_at": msg.get("updated_at", msg.get("created_at")),
                "is_deleted": msg.get("is_deleted", False),
            })

        return {
            'items': items,
            'total': result.count or 0
        }

    @staticmethod
    def create_message(chat_id: UUID, sender_id: UUID, content: str) -> Dict[str, Any]:
        """Создать сообщение"""
        supabase = get_supabase_admin()

        result = supabase.table("chat_messages").insert({
            'room_id': str(chat_id),
            'sender_id': str(sender_id),
            'content': content,
            'message_type': 'text'
        }).execute()

        if not result.data:
            raise Exception("Failed to create message")

        return result.data[0]

    @staticmethod
    def mark_messages_as_read(chat_id: UUID, user_id: UUID) -> None:
        """Отметить сообщения как прочитанные"""
        supabase = get_supabase_admin()

        supabase.table("chat_room_members").update({
            'last_read_at': datetime.now(timezone.utc).isoformat()
        }).eq("room_id", str(chat_id)).eq("user_id", str(user_id)).execute()