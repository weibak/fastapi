from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws/chat")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: str, room_id: int, sender_id: int):
        if room_id not in self.active_connections:
            return

        for user_id, connection in self.active_connections[room_id].items():
            await connection.send_json({
                "text": message,
                "is_self": user_id == sender_id,
            })


manager = ConnectionManager()


@router.websocket("/{room_id}/{user_id}")
async def chat_websocket(websocket: WebSocket, room_id: int, user_id: int):
    await manager.connect(websocket, room_id, user_id)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(message, room_id, user_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)
        await manager.broadcast(f"Пользователь {user_id} покинул чат", room_id, user_id)
