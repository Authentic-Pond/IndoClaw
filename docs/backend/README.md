# IndoClaw Web Interface - Backend Documentation

## Overview

The backend is built with FastAPI providing REST API endpoints and WebSocket support for real-time event streaming. It acts as a bridge between the frontend and the IndoClaw core.

## Project Structure

```
src/interfaces/web/server/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── ws_handler.py                # WebSocket handler and manager
├── routers/                     # API route handlers
│   ├── __init__.py
│   ├── chat.py                  # Chat endpoints
│   ├── agents.py                # Agent management endpoints
│   ├── config.py                # Configuration endpoints
│   └── events.py                # Event endpoints
└── static/                      # Static assets (for production)
    └── index.html
```

## FastAPI Application

### Main Application

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IndoClaw Web API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(events.router, prefix="/api", tags=["events"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket handling
    pass
```

### WebSocket Handler

```python
# ws_handler.py
class WebSocketConnection:
    """Represents a WebSocket connection."""
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscribed_events: Set[str] = set()

class WebSocketManager:
    """Manages WebSocket connections and event broadcasting."""
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self._event_queue = asyncio.Queue()
        self._broadcast_task = None
    
    async def connect(self, websocket: WebSocket, client_id: str) -> WebSocketConnection:
        await websocket.accept()
        connection = WebSocketConnection(websocket, client_id)
        self.connections[client_id] = connection
        return connection
    
    async def broadcast(self, event: AgentEvent):
        """Broadcast event to all connected clients."""
        data = {"type": "event", "event": event.to_dict()}
        for connection in self.connections.values():
            try:
                await connection.send(data)
            except Exception:
                pass
```

## API Endpoints

### Chat Endpoints

```python
# POST /api/chat
# Request: {"message": "Hello", "agent_id": "default"}
# Response: {"response": "Hi there!", "agent_id": "default", "messages": [...]}

# GET /api/chat/history/{agent_id}
# Response: {"messages": [...]}

# DELETE /api/chat/history/{agent_id}
# Response: {"status": "cleared"}
```

### Agent Endpoints

```python
# GET /api/agents
# Response: {"agents": [{"id": "default", "name": "IndoClaw", "status": "idle"}]}

# GET /api/agents/{agent_id}
# Response: {"id": "default", "name": "IndoClaw", "status": "idle", "role": "..."}

# POST /api/agents
# Request: {"agent_name": "new_agent", ...}
# Response: {"status": "created", "agent_id": "new_agent"}

# DELETE /api/agents/{agent_id}
# Response: {"status": "deleted"}
```

### Configuration Endpoints

```python
# GET /api/config
# Response: {"llm": {...}, "memory": {...}, "agent": {...}}

# POST /api/config
# Request: {"llm": {...}, "memory": {...}, "agent": {...}}
# Response: {"status": "updated"}
```

### Event Endpoints

```python
# GET /api/events
# Query: ?event_type=task_start&limit=100
# Response: {"events": [...]}

# GET /api/events/types
# Response: {"types": ["task_start", "task_end", "tool_executed", ...]}

# DELETE /api/events
# Response: {"status": "cleared"}
```

## WebSocket Protocol

### Connection

```javascript
// Client connects to /ws
const socket = io('http://localhost:8000');
socket.on('connect', () => {
  console.log('Connected to WebSocket');
});
```

### Subscribing to Events

```javascript
// Subscribe to specific event types
socket.emit('subscribe', {
  events: ['task_start', 'task_end', 'tool_executed']
});
```

### Receiving Events

```javascript
// Server broadcasts events to all connected clients
socket.on('event', (data) => {
  console.log('Event received:', data);
  // data = {
  //   type: 'event',
  //   event: {
  //     event_type: 'task_start',
  //     timestamp: '...',
  //     agent_id: 'default',
  //     payload: {...}
  //   }
  // }
});
```

### Unsubscribing

```javascript
// Unsubscribe from event types
socket.emit('unsubscribe', {
  events: ['task_start']
});
```

## Data Models

### AgentEvent

```python
# Pydantic model for events
class AgentEvent(BaseModel):
    event_type: str
    timestamp: str
    agent_id: str
    payload: Dict = {}
    metadata: Dict = {}
```

### Chat Request/Response

```python
class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_id: str
    messages: List[ChatMessage]
```

### Agent Models

```python
class AgentInfo(BaseModel):
    id: str
    name: str
    status: str
    role: Optional[str] = None
```

## Error Handling

### HTTP Errors

```python
from fastapi import HTTPException

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    try:
        # ... logic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### WebSocket Errors

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
```

## Event Flow

```
1. IndoClaw Agent performs action
2. EventPublisher.publish(event)
3. WebSocketCallback.notify(event)
4. WebSocketManager._event_queue.put(event)
5. Broadcast loop picks up event
6. WebSocketManager.broadcast(event)
7. All connected clients receive event
```

## Running the Backend

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with specific settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production

```bash
# Build static assets first
# Then run with gunicorn (recommended)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Security Considerations

1. **CORS**: Currently allows all origins (configure for production)
2. **Input Validation**: All endpoints validate input with Pydantic
3. **Error Messages**: Generic errors don't expose internal details
4. **Rate Limiting**: Consider adding for production

## Performance Tuning

```python
# Use background tasks for non-essential operations
from fastapi import BackgroundTasks

@app.post("/api/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    # Process immediately
    result = process_chat(request)
    
    # Schedule logging for later
    background_tasks.add_task(log_chat, request, result)
    
    return result
```

## Testing

```bash
# Run tests
pytest tests/test_api.py

# Test WebSocket
python -m pytest tests/test_websocket.py
```
