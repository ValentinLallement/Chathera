from typing import Dict
from uuid import UUID

from fastapi import WebSocket

active_websockets: Dict[UUID, WebSocket] = {}

def register_websocket(user_id: UUID, websocket: WebSocket):
    active_websockets[user_id] = websocket

def unregister_websocket(user_id: UUID):
    active_websockets.pop(user_id, None)

def get_active_websockets():
    return active_websockets
