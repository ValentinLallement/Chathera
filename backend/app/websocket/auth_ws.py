from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from app.dependencies import get_current_user_from_token
from app.utils.websocket_registry import register_websocket, unregister_websocket
from app.database import async_session
from typing import Optional
from app.db.models.models import User

async def get_user_from_websocket(websocket: WebSocket) -> Optional[User]:
    token = websocket.query_params.get("token")
    if token is None:
        print("Connexion WebSocket rejetée : aucun token fourni")
        return None

    async with async_session() as db:
        try:
            user = await get_current_user_from_token(token, db)
            print(f"Utilisateur {user.id} authentifié pour WebSocket")
            return user
        except Exception as e:
            print(f"Erreur d'authentification WebSocket : {e}")
            return None