import socketio
from uuid import UUID
from typing import Dict, Set
from app.core.config import settings
from app.db.repositories.chat import ChatRepository
from app.db.repositories.users import UsersRepository

sio = socketio.AsyncServer(
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://lapa-frontend.amvera.io",
        "https://lapa-api-delderol.amvera.io"
    ],
    async_mode='asgi',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Хранилище активных пользователей
active_users: Dict[str, str] = {}  # user_id -> sid
user_rooms: Dict[str, Set[str]] = {}  # user_id -> set of room_ids


async def get_user_id_from_token(token: str) -> str | None:
    """Получить user_id из токена"""
    try:
        from supabase import create_client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        user = supabase.auth.get_user(token)
        if user and user.user:
            return str(user.user.id)
    except Exception as e:
        print(f"Token verification error: {e}")
    return None


@sio.event
async def connect(sid, environ, auth=None):
    """Пользователь подключился"""
    token = auth.get('token') if auth else None

    if not token:
        print(f"Connection refused: No token provided")
        return False

    user_id = await get_user_id_from_token(token)
    if not user_id:
        print(f"Connection refused: Invalid token for sid {sid}")
        return False

    active_users[user_id] = sid
    print(f"✅ User {user_id} connected with sid {sid}")
    return True


@sio.event
async def disconnect(sid):
    """Пользователь отключился"""
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

        if user_id:
            del active_users[user_id]
        if user_id in user_rooms:
            del user_rooms[user_id]
            print(f"User {user_id} disconnected")


@sio.event
async def chat_join(sid, data):
    """Присоединение к чату"""
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

    if not user_id:
        await sio.emit('error', {'message': 'Not authenticated'}, to=sid)
        return

    chat_id = data.get('chat_id')
    if not chat_id:
        return

    try:
        chat = ChatRepository.get_chat_by_id(UUID(chat_id), UUID(user_id))
        if not chat:
            await sio.emit('error', {'message': 'Chat not found'}, to=sid)
            return

        room_name = f"chat_{chat_id}"
        sio.enter_room(sid, room_name)

        if user_id not in user_rooms:
            user_rooms[user_id] = set()
        user_rooms[user_id].add(chat_id)

        print(f"✅ User {user_id} joined room {room_name}")

        # Отправляем историю
        messages = ChatRepository.get_chat_messages(UUID(chat_id), 50, 0)
        await sio.emit('chat:history', {
            'chat_id': chat_id,
            'messages': messages.get('items', [])
        }, to=sid)

    except Exception as e:
        print(f"Error in chat_join: {e}")
        await sio.emit('error', {'message': str(e)}, to=sid)

@sio.event
async def chat_leave(sid, data):
    """Выход из чата"""
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

    if not user_id:
        return

    chat_id = data.get('chat_id')
    if chat_id:
        room_name = f"chat_{chat_id}"
        sio.leave_room(sid, room_name)

        if user_id in user_rooms and chat_id in user_rooms[user_id]:
            user_rooms[user_id].discard(chat_id)

        print(f"User {user_id} left room {room_name}")


@sio.event
async def message_send(sid, data):
    """Отправка сообщения"""
    print(f"message_send CALLED with data: {data}")

    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

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
        # Проверяем чат
        chat = ChatRepository.get_chat_by_id(UUID(chat_id), UUID(user_id))
        if not chat:
            print(f"Chat {chat_id} not found")
            await sio.emit('error', {'message': 'Chat not found'}, to=sid)
            return

        # Создаем сообщение
        message = ChatRepository.create_message(UUID(chat_id), UUID(user_id), content)
        print(f"Message created: {message['id']}")

        message_data = {
            'id': str(message['id']),
            'chat_id': str(message['room_id']),
            'sender_id': str(message['sender_id']),
            'content': message['content'],
            'created_at': message['created_at'],
            'updated_at': message.get('updated_at', message['created_at'])
        }

        room_name = f"chat_{chat_id}"
        print(f"📨 Broadcasting to room {room_name}")

        # ПРЯМАЯ ОТПРАВКА - пробуем оба способа
        # Способ 1: Всем в комнате
        await sio.emit('chat:message', message_data, room=room_name)
        print(f"Sent to room {room_name}")

        # Способ 2: Напрямую отправителю (для теста)
        await sio.emit('chat:message', message_data, to=sid)
        print(f"Sent directly to {sid}")

        # Способ 3: Всем подключенным (для теста)
        await sio.emit('chat:message', message_data)
        print(f"Sent to all connected")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Создаем ASGI приложение
socket_app = socketio.ASGIApp(sio)