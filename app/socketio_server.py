import socketio
from uuid import UUID
from typing import Dict, Set
from app.core.config import settings
from app.db.repositories.chat import ChatRepository

# Создаем Socket.IO сервер
sio = socketio.AsyncServer(
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://lapa-frontend.amvera.io",
        "https://lapa-api-delderol.amvera.io"
    ],
    async_mode='asgi',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Хранилище активных пользователей: user_id -> sid
active_users: Dict[str, str] = {}
# Хранилище комнат пользователя: user_id -> set of room_ids
user_rooms: Dict[str, Set[str]] = {}


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

    # Сохраняем связь sid <-> user_id
    active_users[user_id] = sid
    print(f"User {user_id} connected with sid {sid}")

    # Отправляем подтверждение
    await sio.emit('connect', {'status': 'connected', 'user_id': user_id}, to=sid)
    return True


@sio.event
async def disconnect(sid):
    """Пользователь отключился"""
    # Находим user_id по sid
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

    if user_id:
        del active_users[user_id]
        print(f"User {user_id} disconnected")

        # Оповещаем другие чаты о дисконнекте
        await sio.emit('user:status_changed', {
            'user_id': user_id,
            'status': 'offline'
        })


@sio.event
async def chat_join(sid, data):
    """Присоединение к чату"""
    # Находим user_id по sid
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

    if not user_id:
        await sio.emit('error', {'message': 'User not authenticated'}, to=sid)
        return

    chat_id = data.get('chat_id')
    if not chat_id:
        return

    # Проверяем доступ к чату
    try:
        chat = ChatRepository.get_chat_by_id(UUID(chat_id), UUID(user_id))
        if not chat:
            await sio.emit('error', {'message': 'Chat not found or access denied'}, to=sid)
            return
    except Exception as e:
        await sio.emit('error', {'message': f'Invalid chat_id: {str(e)}'}, to=sid)
        return

    # Присоединяемся к комнате
    room_name = f"chat_{chat_id}"
    sio.enter_room(sid, room_name)

    # Сохраняем информацию о комнате
    if user_id not in user_rooms:
        user_rooms[user_id] = set()
    user_rooms[user_id].add(chat_id)

    print(f"User {user_id} joined room {room_name}")

    # Отправляем историю сообщений
    messages_data = ChatRepository.get_chat_messages(UUID(chat_id), 50, 0)
    await sio.emit('chat:history', {
        'chat_id': chat_id,
        'messages': messages_data.get('items', [])
    }, to=sid)


@sio.event
async def chat_leave(sid, data):
    """Выход из чата"""
    # Находим user_id по sid
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
    # Находим user_id по sid
    user_id = None
    for uid, s in active_users.items():
        if s == sid:
            user_id = uid
            break

    if not user_id:
        await sio.emit('error', {'message': 'User not authenticated'}, to=sid)
        return

    chat_id = data.get('chat_id')
    content = data.get('content')

    if not chat_id or not content:
        return

    # Проверяем доступ к чату
    try:
        chat = ChatRepository.get_chat_by_id(UUID(chat_id), UUID(user_id))
        if not chat:
            await sio.emit('error', {'message': 'Chat not found or access denied'}, to=sid)
            return
    except Exception as e:
        await sio.emit('error', {'message': f'Invalid chat_id: {str(e)}'}, to=sid)
        return

    # Создаем сообщение
    try:
        message = ChatRepository.create_message(UUID(chat_id), UUID(user_id), content)
    except Exception as e:
        await sio.emit('error', {'message': f'Failed to send message: {str(e)}'}, to=sid)
        return

    message_data = {
        'id': str(message['id']),
        'chat_id': str(message['room_id']),
        'sender_id': str(message['sender_id']),
        'content': message['content'],
        'created_at': message['created_at'],
        'updated_at': message.get('updated_at', message['created_at'])
    }

    room_name = f"chat_{chat_id}"
    print(f"Broadcasting message to room {room_name}: {message_data}")

    # Отправляем сообщение всем в комнате
    await sio.emit(f'chat:{chat_id}:message', message_data, room=room_name)

    # Оповещаем об обновлении чата для другого участника
    other_user_id = None
    if str(chat.get('user_1_id')) == user_id:
        other_user_id = str(chat.get('user_2_id'))
    else:
        other_user_id = str(chat.get('user_1_id'))

    if other_user_id and other_user_id in active_users:
        await sio.emit('chats:updated', {
            'chat_id': chat_id
        }, to=active_users[other_user_id])


@sio.event
async def typing_start(sid, data):
    """Пользователь начал печатать"""
    # Находим user_id по sid
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
        await sio.emit('typing:status', {
            'user_id': user_id,
            'is_typing': True
        }, room=room_name, skip_sid=sid)


@sio.event
async def typing_stop(sid, data):
    """Пользователь перестал печатать"""
    # Находим user_id по sid
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
        await sio.emit('typing:status', {
            'user_id': user_id,
            'is_typing': False
        }, room=room_name, skip_sid=sid)


# Создаем ASGI приложение
socket_app = socketio.ASGIApp(sio)