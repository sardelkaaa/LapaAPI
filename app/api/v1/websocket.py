from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.api.v1.deps import get_current_user
from app.services.chat_service import chat_manager
from app.websocket.handlers import ChatWebSocketHandler


async def websocket_endpoint(
        websocket: WebSocket,
        user_id=Depends(get_current_user)
):
    """WebSocket эндпоинт для чата"""
    await chat_manager.connect_user(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get('type')

            if event_type == 'chat:join':
                await ChatWebSocketHandler.handle_join(websocket, data, user_id)
            elif event_type == 'chat:leave':
                await ChatWebSocketHandler.handle_leave(websocket, data, user_id)
            elif event_type == 'message:send':
                await ChatWebSocketHandler.handle_send_message(websocket, data, user_id)

    except WebSocketDisconnect:
        await chat_manager.disconnect_user(user_id, websocket)