from typing import Dict
from uuid import UUID
from fastapi import WebSocket
from app.db.repositories.chat import ChatRepository
from app.services.chat_service import chat_manager


class ChatWebSocketHandler:

    @staticmethod
    async def handle_join(websocket: WebSocket, data: Dict, user_id: UUID):
        """Обработка присоединения к чату"""
        chat_id = UUID(data.get('chat_id'))

        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            await websocket.send_json({
                'type': 'error',
                'message': 'Chat not found or access denied'
            })
            return

        await chat_manager.join_room(chat_id, websocket)

        messages = ChatRepository.get_chat_messages(chat_id, 50, 0)
        await websocket.send_json({
            'type': 'chat:history',
            'data': messages
        })

    @staticmethod
    async def handle_leave(websocket: WebSocket, data: Dict, user_id: UUID):
        """Обработка выхода из чата"""
        chat_id = UUID(data.get('chat_id'))
        await chat_manager.leave_room(chat_id, websocket)

    @staticmethod
    async def handle_send_message(websocket: WebSocket, data: Dict, user_id: UUID):
        """Обработка отправки сообщения"""
        chat_id = UUID(data.get('chat_id'))
        content = data.get('content')

        if not content or not content.strip():
            return

        chat = ChatRepository.get_chat_by_id(chat_id, user_id)
        if not chat:
            await websocket.send_json({
                'type': 'error',
                'message': 'Chat not found or access denied'
            })
            return

        message = ChatRepository.create_message(chat_id, user_id, content)

        await chat_manager.broadcast_to_room(chat_id, {
            'type': 'chat:message',
            'data': message
        })

        for participant_id in [chat['user_1_id'], chat['user_2_id']]:
            await chat_manager.send_to_user(participant_id, {
                'type': 'chats:updated',
                'data': {'chat_id': str(chat_id)}
            })