from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.core.database import get_supabase_admin
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
                ChatHTTPService._enrich_chat_to_model(chat, user_id)
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
        return ChatHTTPService._enrich_chat_to_model(chat, user_id)

    @staticmethod
    def create_chat(user1_id: UUID, user2_id: UUID) -> Optional[Dict[str, Any]]:
        """Создать чат между пользователями"""
        if user1_id == user2_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create chat with yourself"
            )

        chat = ChatRepository.get_or_create_direct_chat(user1_id, user2_id)
        return ChatHTTPService._enrich_chat_to_model(chat, user1_id)

    @staticmethod
    def get_messages(chat_id: UUID, user_id: UUID, limit: int, offset: int) -> Dict[str, Any]:
        """Получить сообщения чата с проверкой доступа"""
        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )

        result = ChatRepository.get_chat_messages(chat_id, limit, offset)

        # Преобразуем сообщения в нужный формат
        messages = []
        for msg in result['items']:
            messages.append({
                'id': UUID(msg['id']),
                'chat_id': chat_id,
                'sender_id': UUID(msg['sender_id']),
                'content': msg['content'],
                'created_at': datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00')) if isinstance(
                    msg['created_at'], str) else msg['created_at'],
                'updated_at': datetime.fromisoformat(msg['updated_at'].replace('Z', '+00:00')) if msg.get(
                    'updated_at') and isinstance(msg['updated_at'], str) else msg.get('updated_at', msg['created_at'])
            })

        return {
            'items': messages,
            'total': result['total'],
            'next_offset': offset + limit if offset + limit < result['total'] else None
        }

    @staticmethod
    def _enrich_chat_to_model(chat: Dict, current_user_id: UUID) -> Dict:
        """Преобразовать данные чата в формат, ожидаемый Pydantic моделью Chat"""

        chat_id = chat.get('id')
        if not chat_id:
            raise ValueError("Chat ID is required")

        # Получаем ID другого участника
        other_user_id = chat.get('other_user_id')

        # Если нет, получаем из БД
        if not other_user_id:
            supabase = get_supabase_admin()
            members = supabase.table("chat_room_members") \
                .select("user_id") \
                .eq("room_id", str(chat_id)) \
                .execute()

            for member in members.data or []:
                user_id = member.get('user_id')
                if user_id and user_id != str(current_user_id):
                    other_user_id = user_id
                    break

        # Получаем данные текущего пользователя
        current_user_data = UsersRepository.get_user_by_id(str(current_user_id))
        if not current_user_data:
            raise HTTPException(status_code=404, detail="Current user not found")

        # Получаем данные другого пользователя
        other_user_data = None
        if other_user_id:
            other_user_data = UsersRepository.get_user_by_id(other_user_id)

        # Формируем user_1 и user_2 (текущий пользователь всегда user_1)
        user_1 = {
            'id': current_user_id,
            'name': current_user_data.get('name'),
            'avatar_url': current_user_data.get('avatar_url'),
            'role': current_user_data.get('role', 'volunteer')
        }

        user_2 = {
            'id': UUID(other_user_id) if other_user_id else None,
            'name': other_user_data.get('name') if other_user_data else None,
            'avatar_url': other_user_data.get('avatar_url') if other_user_data else None,
            'role': other_user_data.get('role', 'volunteer') if other_user_data else 'volunteer'
        }

        # Формируем последнее сообщение
        last_message = None
        last_message_at = chat.get('created_at')
        last_message_time = chat.get('last_message_time')

        if chat.get('last_message'):
            last_message_time = chat.get('last_message_time') or chat.get('created_at')
            last_message = {
                'id': UUID(chat.get('last_message_id')) if chat.get('last_message_id') else UUID(int=0),
                'chat_id': chat_id,
                'sender_id': UUID(chat.get('last_message_sender_id')) if chat.get(
                    'last_message_sender_id') else current_user_id,
                'content': chat.get('last_message'),
                'created_at': last_message_time or datetime.now(timezone.utc),
                'updated_at': last_message_time or datetime.now(timezone.utc)
            }
            last_message_at = last_message_time or chat.get('created_at')

        return {
            'id': chat_id,
            'user_1_id': current_user_id,
            'user_2_id': UUID(other_user_id) if other_user_id else None,
            'user_1': user_1,
            'user_2': user_2,
            'last_message': last_message,
            'last_message_at': last_message_at or chat.get('created_at'),
            'created_at': chat.get('created_at'),
            'updated_at': chat.get('updated_at') or chat.get('created_at')
        }