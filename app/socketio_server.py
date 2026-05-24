import asyncio
import socketio
from uuid import UUID
from typing import Dict
from app.core.config import settings
from app.db.repositories.chat import ChatRepository
from app.db.repositories.users import UsersRepository

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "https://lapa-frontend.amvera.io",
    "https://lapa-api-delderol.amvera.io",
    "https://lapafrontend.onrender.com/"
]

sio = socketio.AsyncServer(
    cors_allowed_origins=ALLOWED_ORIGINS,
    async_mode='asgi',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    allow_upgrades=True,
    transports=['websocket', 'polling']
)

# Хранилище активных пользователей
active_users: Dict[str, str] = {}  # user_id -> sid


def _serialize(value):
    """Привести значение к JSON-совместимому типу"""
    if value is None:
        return None
    return str(value)


async def get_user_id_from_token(token: str) -> str | None:
    try:
        from supabase import create_client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        user = await asyncio.to_thread(supabase.auth.get_user, token)
        if user and user.user:
            return str(user.user.id)
    except Exception as e:
        print(f"Token verification error: {e}")
    return None


def _get_user_id_by_sid(sid: str) -> str | None:
    for uid, s in active_users.items():
        if s == sid:
            return uid
    return None


@sio.event
async def connect(sid, environ, auth=None):
    """Пользователь подключился"""
    origin = environ.get('HTTP_ORIGIN', 'unknown')
    print(f"Connection attempt from {origin}")

    token = auth.get('token') if auth else None
    if not token:
        print(f"Connection refused: No token from {origin}")
        return False

    user_id = await get_user_id_from_token(token)
    if not user_id:
        print(f"Connection refused: Invalid token from {origin}")
        return False

    active_users[user_id] = sid
    print(f"✅ User {user_id} connected with sid {sid}")
    print(f"Active users: {list(active_users.keys())}")
    return True


@sio.event
async def disconnect(sid):
    user_id = _get_user_id_by_sid(sid)
    if user_id:
        del active_users[user_id]
        print(f"User {user_id} disconnected")
        print(f"Active users: {list(active_users.keys())}")


@sio.event
async def chat_join(sid, data):
    print(f"chat_join: {data} from {sid}")

    user_id = _get_user_id_by_sid(sid)
    if not user_id:
        await sio.emit('error', {'message': 'Not authenticated'}, to=sid)
        return

    chat_id = data.get('chat_id')
    if not chat_id:
        return

    try:
        chat = await asyncio.to_thread(
            ChatRepository.get_chat_by_id, UUID(chat_id), UUID(user_id)
        )
        if not chat:
            await sio.emit('error', {'message': 'Chat not found'}, to=sid)
            return

        room_name = f"chat_{chat_id}"
        await sio.enter_room(sid, room_name)
        print(f"✅ User {user_id} joined room {room_name}")

        # Отправляем историю
        messages = await asyncio.to_thread(
            ChatRepository.get_chat_messages, UUID(chat_id), 50, 0
        )

        serialized_messages = [
            {
                'id': _serialize(msg.get('id')),
                'chat_id': _serialize(msg.get('room_id')),
                'sender_id': _serialize(msg.get('sender_id')),
                'sender_name': msg.get('sender_name'),
                'sender_avatar': msg.get('sender_avatar'),
                'content': msg.get('content'),
                'message_type': msg.get('message_type', 'text'),
                'created_at': _serialize(msg.get('created_at')),
                'updated_at': _serialize(msg.get('updated_at') or msg.get('created_at')),
                'is_deleted': msg.get('is_deleted', False),
            }
            for msg in messages.get('items', [])
        ]

        await sio.emit('chat:history', {
            'chat_id': chat_id,
            'messages': serialized_messages
        }, to=sid)

    except Exception as e:
        print(f"Error in chat_join: {e}")
        import traceback
        traceback.print_exc()


@sio.event
async def message_send(sid, data):
    print(f"🔴 message_send: {data}")

    user_id = _get_user_id_by_sid(sid)
    if not user_id:
        print(f"User not found for sid {sid}")
        await sio.emit('error', {'message': 'Not authenticated'}, to=sid)
        return

    chat_id = data.get('chat_id')
    content = data.get('content')
    if not chat_id or not content:
        print(f"Invalid data: chat_id={chat_id}, content={content}")
        return

    try:
        chat = await asyncio.to_thread(
            ChatRepository.get_chat_by_id, UUID(chat_id), UUID(user_id)
        )
        if not chat:
            print(f"Chat {chat_id} not found")
            await sio.emit('error', {'message': 'Chat not found'}, to=sid)
            return

        message = await asyncio.to_thread(
            ChatRepository.create_message, UUID(chat_id), UUID(user_id), content
        )
        print(f"Message created: {message['id']}")

        sender_data = await asyncio.to_thread(UsersRepository.get_user_by_id, user_id)

        message_data = {
            'id': _serialize(message['id']),
            'chat_id': _serialize(message['room_id']),
            'sender_id': _serialize(message['sender_id']),
            'sender_name': sender_data.get('name') if sender_data else None,
            'content': message['content'],
            'created_at': _serialize(message['created_at']),
            'updated_at': _serialize(message.get('updated_at') or message['created_at']),
        }

        room_name = f"chat_{chat_id}"
        await sio.enter_room(sid, room_name)  # гарантируем что отправитель в комнате
        print(f"📨 Broadcasting to room {room_name}")

        await sio.emit('chat:message', message_data, room=room_name)
        print(f"✅ Sent to room {room_name}")

    except Exception as e:
        print(f"Error in message_send: {e}")
        import traceback
        traceback.print_exc()


@sio.event
async def test(sid, data):
    """Тестовое событие"""
    print(f"Test event from {sid}: {data}")
    await sio.emit('test_response', {'status': 'ok', 'data': data}, to=sid)


socket_app = socketio.ASGIApp(sio)