from fastapi import WebSocket

from app.dependencies import get_current_user_from_token
from app.utils.websocket_registry import register_websocket, unregister_websocket

async def get_user_from_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if token is None:
        await websocket.close(code=1008)
        unregister_websocket(user.id)
        return

    try:
        user = get_current_user_from_token(token)
        return user
    except Exception:
        await websocket.close(code=1008)
        unregister_websocket(user.id)
