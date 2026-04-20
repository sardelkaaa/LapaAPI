from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from app.db.repositories.chat import ChatRepository
from app.db.repositories.users import UsersRepository


class ChatHTTPService:

    @staticmethod
    def get_user_chats(user_id: UUID, limit: int, offset: int) -> Dict[str, Any]:
        """Получить чаты пользователя с обогащенными данными"""
        result = ChatRepository.get_user_chats(user_id, limit, offset)

        enriched_items = []
        for chat in result['items']:
            enriched_items.append(
                ChatHTTPService._enrich_chat_with_users(chat, user_id)
            )

        return {
            'items': enriched_items,
            'total': result['total'],
            'next_offset': offset + limit if offset + limit < result['total'] else None
        }

    @staticmethod
    def get_chat(chat_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Получить детали чата"""
        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            return None
        return ChatHTTPService._enrich_chat_with_users(chat, user_id)

    @staticmethod
    def create_chat(user1_id: UUID, user2_id: UUID) -> Optional[Dict[str, Any]]:
        """Создать чат между пользователями"""
        if user1_id == user2_id:
            return None

        chat = ChatRepository.get_or_create_direct_chat(user1_id, user2_id)
        return ChatHTTPService._enrich_chat_with_users(chat, user1_id)

    @staticmethod
    def get_messages(chat_id: UUID, user_id: UUID, limit: int, offset: int) -> Dict[str, Any]:
        """Получить сообщения чата с проверкой доступа"""
        # Проверяем доступ
        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )

        result = ChatRepository.get_chat_messages(chat_id, limit, offset)

        return {
            'items': result['items'],
            'total': result['total'],
            'next_offset': offset + limit if offset + limit < result['total'] else None
        }

    @staticmethod
    def delete_chat(chat_id: UUID, user_id: UUID) -> bool:
        """Удалить чат (пометить как удаленный для пользователя)"""
        # Проверяем доступ
        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            return False

        # В вашей схеме нет поля для мягкого удаления для пользователя
        # Можно добавить таблицу deleted_chats или просто удалить участника
        supabase = get_supabase_admin()
        result = supabase.table('chat_room_members') \
            .delete() \
            .eq('room_id', str(chat_id)) \
            .eq('user_id', str(user_id)) \
            .execute()

        return len(result.data) > 0

    @staticmethod
    def _enrich_chat_with_users(chat: Dict, current_user_id: UUID) -> Dict:
        """Обогатить чат данными пользователей"""
        user1_id = chat['user_1_id']
        user2_id = chat['user_2_id']

        user1 = UsersRepository.get_user_by_id(user1_id)
        user2 = UsersRepository.get_user_by_id(user2_id)

        chat['user_1'] = {
            'id': user1['id'],
            'name': user1.get('name'),
            'avatar_url': user1.get('avatar_url'),
            'role': user1.get('role')
        }

        chat['user_2'] = {
            'id': user2['id'],
            'name': user2.get('name'),
            'avatar_url': user2.get('avatar_url'),
            'role': user2.get('role')
        }

        return chat