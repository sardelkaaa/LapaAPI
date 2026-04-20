from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.v1.deps import get_current_user
from app.models.chat import (
    Chat, ChatListResponse, ChatMessagesResponse,
    CreateChatRequest, CreateMessageRequest
)
from app.services.chat_http_service import ChatHTTPService

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("", response_model=ChatListResponse)
def get_user_chats(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Получить все чаты текущего пользователя"""
    return ChatHTTPService.get_user_chats(
        user_id=current_user['id'],
        limit=limit,
        offset=offset
    )

@router.get("/{chat_id}", response_model=Chat)
def get_chat(
    chat_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Получить детали чата по ID"""
    chat = ChatHTTPService.get_chat(chat_id, current_user['id'])
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat

@router.post("", response_model=Chat)
def create_chat(
    data: CreateChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Создать новый чат с пользователем"""
    chat = ChatHTTPService.create_chat(current_user['id'], data.user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create chat with yourself"
        )
    return chat

@router.get("/{chat_id}/messages", response_model=ChatMessagesResponse)
def get_chat_messages(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Получить сообщения чата"""
    return ChatHTTPService.get_messages(chat_id, current_user['id'], limit, offset)

@router.delete("/{chat_id}")
def delete_chat(
    chat_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Удалить чат"""
    success = ChatHTTPService.delete_chat(chat_id, current_user['id'])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return {"message": "Chat deleted successfully"}