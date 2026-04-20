from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

class ChatUser(BaseModel):
    """Пользователь в чате"""
    id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str

class ChatMessage(BaseModel):
    """Сообщение чата"""
    id: UUID
    chat_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

class Chat(BaseModel):
    """Чат (диалог между двумя пользователями)"""
    id: UUID
    user_1_id: UUID
    user_2_id: UUID
    user_1: ChatUser
    user_2: ChatUser
    last_message: Optional[ChatMessage] = None
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime

class ChatListResponse(BaseModel):
    """Ответ со списком чатов"""
    items: List[Chat]
    total: int
    next_offset: Optional[int] = None

class ChatMessagesResponse(BaseModel):
    """Ответ с сообщениями"""
    items: List[ChatMessage]
    total: int
    next_offset: Optional[int] = None

class CreateChatRequest(BaseModel):
    """Запрос на создание чата"""
    user_id: UUID

class CreateMessageRequest(BaseModel):
    """Запрос на отправку сообщения"""
    content: str = Field(..., min_length=1, max_length=5000)