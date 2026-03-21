from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(tags=["WebSockets"])

# A simple Connection Manager for the Hackathon
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/live-tracking")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive GPS coordinates from a Volunteer's Flutter app
            data = await websocket.receive_text()
            # Broadcast those coordinates instantly to the Authority Dashboard
            await manager.broadcast(f"Live Update: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)