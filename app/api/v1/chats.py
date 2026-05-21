from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.api.v1.deps import get_current_user
from app.services.chat_http_service import ChatHTTPService
from app.models.chat import Chat, ChatListResponse, ChatMessagesResponse, CreateChatRequest, CreateMessageRequest, \
    ChatMessage

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("", response_model=ChatListResponse)
async def get_user_chats(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Получить все чаты текущего пользователя"""
    return ChatHTTPService.get_user_chats(
        UUID(current_user["id"]),
        limit,
        offset
    )

@router.post("", response_model=Chat)
async def create_chat(
    data: CreateChatRequest,
    current_user = Depends(get_current_user)
):
    """Создать или получить существующий чат с пользователем"""
    chat = ChatHTTPService.create_chat(
        UUID(current_user["id"]),
        data.user_id
    )
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return chat

@router.get("/{chat_id}", response_model=Chat)
async def get_chat(
    chat_id: str,
    current_user = Depends(get_current_user)
):
    """Получить детали чата"""
    chat = ChatHTTPService.get_chat(UUID(chat_id), UUID(current_user["id"]))
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat

@router.get("/{chat_id}/messages", response_model=ChatMessagesResponse)
async def get_chat_messages(
    chat_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Получить сообщения чата"""
    return ChatHTTPService.get_messages(
        UUID(chat_id),
        UUID(current_user["id"]),
        limit,
        offset
    )

@router.post("/{chat_id}/messages", response_model=ChatMessage)
async def send_message(
    chat_id: str,
    data: CreateMessageRequest,
    current_user = Depends(get_current_user)
):
    """Отправить сообщение в чат (через HTTP)"""
    message = ChatHTTPService.send_message(
        UUID(chat_id),
        UUID(current_user["id"]),
        data.content
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return message