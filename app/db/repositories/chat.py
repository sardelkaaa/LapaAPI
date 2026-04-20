from typing import Optional, List, Dict, Any
from uuid import UUID
from app.core.database import get_supabase_admin
from datetime import datetime


class ChatRepository:

    @staticmethod
    def get_or_create_direct_chat(user1_id: UUID, user2_id: UUID) -> Dict[str, Any]:
        """Получить или создать прямой чат между двумя пользователями"""
        supabase = get_supabase_admin()

        result = supabase.rpc(
            'get_direct_chat',
            {'p_user1_id': str(user1_id), 'p_user2_id': str(user2_id)}
        ).execute()

        if result.data:
            return result.data[0]

        room_result = supabase.table('chat_rooms').insert({
            'title': None 
        }).execute()

        if not room_result.data:
            raise Exception("Failed to create chat room")

        room_id = room_result.data[0]['id']

        supabase.table('chat_room_members').insert([
            {'room_id': room_id, 'user_id': str(user1_id)},
            {'room_id': room_id, 'user_id': str(user2_id)}
        ]).execute()

        return ChatRepository.get_chat_by_id(room_id, user1_id)

    @staticmethod
    def get_user_chats(user_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Получить все чаты пользователя"""
        supabase = get_supabase_admin()

        result = supabase.rpc(
            'get_user_chats',
            {'p_user_id': str(user_id), 'p_limit': limit, 'p_offset': offset}
        ).execute()

        total_result = supabase.rpc(
            'get_user_chats_count',
            {'p_user_id': str(user_id)}
        ).execute()

        return {
            'items': result.data or [],
            'total': total_result.data[0] if total_result.data else 0
        }

    @staticmethod
    def get_chat_by_id(chat_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить чат по ID с проверкой доступа"""
        supabase = get_supabase_admin()

        member_check = supabase.table('chat_room_members') \
            .select('user_id') \
            .eq('room_id', str(chat_id)) \
            .eq('user_id', str(user_id)) \
            .execute()

        if not member_check.data:
            return None

        result = supabase.rpc(
            'get_chat_details',
            {'p_chat_id': str(chat_id), 'p_user_id': str(user_id)}
        ).execute()

        return result.data[0] if result.data else None

    @staticmethod
    def get_chat_messages(chat_id: UUID, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Получить сообщения чата"""
        supabase = get_supabase_admin()

        result = supabase.table('chat_messages') \
            .select('*', count='exact') \
            .eq('room_id', str(chat_id)) \
            .eq('is_deleted', False) \
            .order('created_at', desc=False) \
            .range(offset, offset + limit - 1) \
            .execute()

        return {
            'items': result.data or [],
            'total': result.count or 0
        }

    @staticmethod
    def create_message(chat_id: UUID, sender_id: UUID, content: str) -> Dict[str, Any]:
        """Создать сообщение"""
        supabase = get_supabase_admin()

        result = supabase.table('chat_messages').insert({
            'room_id': str(chat_id),
            'sender_id': str(sender_id),
            'content': content,
            'message_type': 'text'
        }).execute()

        if not result.data:
            raise Exception("Failed to create message")

        supabase.table('chat_rooms').update({
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', str(chat_id)).execute()

        return result.data[0]