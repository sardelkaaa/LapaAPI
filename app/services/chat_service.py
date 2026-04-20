from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.room_connections: Dict[UUID, Set[WebSocket]] = {}

    async def connect_user(self, user_id: UUID, websocket: WebSocket):
        """Подключить пользователя"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    async def disconnect_user(self, user_id: UUID, websocket: WebSocket):
        """Отключить пользователя"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def join_room(self, room_id: UUID, websocket: WebSocket):
        """Присоединиться к комнате"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(websocket)

    async def leave_room(self, room_id: UUID, websocket: WebSocket):
        """Покинуть комнату"""
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    async def broadcast_to_room(self, room_id: UUID, message: Dict):
        """Отправить сообщение всем в комнате"""
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def send_to_user(self, user_id: UUID, message: Dict):
        """Отправить сообщение конкретному пользователю"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


chat_manager = ConnectionManager()