"""
WebSocket handler for real-time agent events.
"""
import asyncio
import json
from typing import Dict, Set
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class AgentEvent(BaseModel):
    event_type: str
    timestamp: str
    agent_id: str
    payload: Dict = {}
    metadata: Dict = {}

    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "payload": self.payload,
            "metadata": self.metadata,
        }


class WebSocketConnection:
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscribed_events: Set[str] = set()

    async def send(self, data: dict):
        try:
            await self.websocket.send_json(data)
        except Exception:
            pass

    def subscribe(self, event_type: str):
        self.subscribed_events.add(event_type)

    def unsubscribe(self, event_type: str):
        self.subscribed_events.discard(event_type)


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self._event_queue = asyncio.Queue()
        self._broadcast_task = None

    async def connect(self, websocket: WebSocket, client_id: str) -> WebSocketConnection:
        await websocket.accept()
        connection = WebSocketConnection(websocket, client_id)
        self.connections[client_id] = connection
        return connection

    async def disconnect(self, client_id: str):
        if client_id in self.connections:
            del self.connections[client_id]

    async def broadcast(self, event: AgentEvent):
        data = {"type": "event", "event": event.to_dict()}
        for connection in self.connections.values():
            if not connection.subscribed_events or event.event_type in connection.subscribed_events:
                try:
                    await connection.send(data)
                except Exception:
                    pass

    def start_broadcasting(self):
        async def broadcast_loop():
            while True:
                try:
                    event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                    await self.broadcast(event)
                except asyncio.TimeoutError:
                    continue

        self._broadcast_task = asyncio.create_task(broadcast_loop())

    def stop_broadcasting(self):
        if self._broadcast_task:
            self._broadcast_task.cancel()


# Global instance
ws_manager = WebSocketManager()
