# IndoClaw Web Interface - WebSocket Documentation

## Overview

The WebSocket endpoint provides real-time event streaming from the IndoClaw agent system to connected clients.

## Endpoint

```
ws://localhost:8000/ws
```

## Connection Management

### Connecting

```javascript
const socket = io('http://localhost:8000', {
  transports: ['websocket'],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});

socket.on('connect', () => {
  console.log('Connected to WebSocket');
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket');
});

socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
});
```

### Client ID

Each connection is assigned a unique client ID:

```javascript
const clientId = socket.id;
console.log('Client ID:', clientId);
```

## Events

### Client to Server

#### subscribe

Subscribe to specific event types.

```javascript
socket.emit('subscribe', {
  events: ['task_start', 'task_end', 'tool_executed']
});
```

**Response:** None (acknowledgment handled internally)

#### unsubscribe

Unsubscribe from event types.

```javascript
socket.emit('unsubscribe', {
  events: ['task_start']
});
```

**Response:** None (acknowledgment handled internally)

#### ping

Ping the server to keep connection alive.

```javascript
socket.emit('ping');
```

**Response:** `pong`

### Server to Client

#### event

Broadcasts agent events to subscribed clients.

```javascript
socket.on('event', (data) => {
  console.log('Received event:', data);
  // data = {
  //   type: 'event',
  //   event: {
  //     event_type: 'task_start',
  //     timestamp: '2024-01-01T00:00:00Z',
  //     agent_id: 'default',
  //     payload: { task: 'What is 25 * 17?' },
  //     metadata: {}
  //   }
  // }
});
```

## Event Types

| Event Type | Description |
|------------|-------------|
| `task_start` | Agent started processing a task |
| `task_end` | Agent completed a task |
| `tool_executed` | A tool was executed |
| `tool_approval_needed` | Tool requires user approval |
| `error` | An error occurred |
| `plan_created` | A plan was generated |
| `plan_approved` | A plan was approved |
| `input_requested` | Agent requested user input |
| `input_received` | User provided input |
| `agent_thought` | Agent generated a thought |
| `memory_updated` | Agent updated memory |

## Event Structure

```typescript
interface Event {
  type: 'event';  // Message type
  event: {
    event_type: string;        // The type of event
    timestamp: string;         // ISO 8601 timestamp
    agent_id: string;          // ID of the agent
    payload: Record<string, any>;  // Event payload
    metadata: Record<string, string>;  // Event metadata
  }
}
```

## Message Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Event Flow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Agent performs action (e.g., starts a task)               │
│     ↓                                                           │
│  2. EventPublisher.publish(event)                             │
│     ↓                                                           │
│  3. WebSocketManager._event_queue.put(event)                  │
│     ↓                                                           │
│  4. Broadcast loop picks up event                             │
│     ↓                                                           │
│  5. WebSocketManager.broadcast(event)                         │
│     ↓                                                           │
│  6. Event sent to all connected clients                       │
│     ↓                                                           │
│  7. Clients receive 'event' message                           │
│     ↓                                                           │
│  8. Frontend updates UI                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Subscription Management

### Subscribing to All Events

```javascript
socket.emit('subscribe', {
  events: ['task_start', 'task_end', 'tool_executed', 'error']
});
```

### Subscribing to Specific Agent Events

```javascript
// Get list of agents first
fetch('/api/agents')
  .then(res => res.json())
  .then(data => {
    const agentIds = data.agents.map(a => a.id);
    socket.emit('subscribe', { events: agentIds });
  });
```

### Unsubscribing from Events

```javascript
socket.emit('unsubscribe', {
  events: ['task_start']
});
```

### Unsubscribing from All

```javascript
// Close the connection to unsubscribe from all
socket.disconnect();
```

## Connection Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   Connection States                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  disconnected → connecting → connected → disconnecting        │
│        ↓               ↓              ↓               ↓        │
│        └───────────────┴──────────────┴───────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling

### Connection Errors

```javascript
socket.on('connect_error', (error) => {
  console.error('Connection error:', error.message);
  
  // Retry after delay
  setTimeout(() => {
    socket.connect();
  }, 5000);
});
```

### Authentication Errors

```javascript
socket.on('error', (error) => {
  if (error.message === 'Authentication required') {
    // Redirect to login or show auth modal
    router.push('/login');
  }
});
```

### Network Errors

```javascript
socket.on('disconnect', (reason) => {
  if (reason === 'transport error') {
    // Network error - show offline indicator
    setOffline(true);
  }
});
```

## Performance Considerations

### Message Throttling

To prevent overwhelming clients, events are throttled:

```python
# ws_handler.py
class WebSocketManager:
    async def broadcast(self, event: AgentEvent):
        # Throttle to 10 events per second per client
        data = {"type": "event", "event": event.to_dict()}
        
        for connection in self.connections.values():
            try:
                await asyncio.wait_for(
                    connection.send(data),
                    timeout=0.1  # 100ms timeout
                )
            except asyncio.TimeoutError:
                # Skip slow clients
                pass
```

### Event Buffering

Events are buffered to prevent loss during high traffic:

```python
# ws_handler.py
class WebSocketManager:
    def __init__(self):
        self._event_queue = asyncio.Queue(maxsize=1000)
    # Queue size limit prevents memory exhaustion
```

## Security

### Origin Validation

```python
# main.py
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
)
````

### Client ID Validation

```python
# ws_handler.py
async def connect(self, websocket: WebSocket, client_id: str):
    # Validate client ID format
    if not client_id.match(r'^[a-zA-Z0-9_-]+$'):
        await websocket.close(code=4003, reason="Invalid client ID")
        return
    # ...
```

## Testing WebSocket

### Using wscat

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8000/ws

# Subscribe to events
>{"type":"subscribe","events":["task_start","task_end"]}

# Send ping
>{"type":"ping"}
```

### Using Python

```python
import asyncio
import websockets

async def test_websocket():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # Subscribe to events
        await ws.send('{"type": "subscribe", "events": ["task_start"]}')
        
        # Receive events
        while True:
            message = await ws.recv()
            print(message)

asyncio.run(test_websocket())
```

## Troubleshooting

### Connection Refused

- Ensure the backend is running
- Check port 8000 is not blocked
- Verify CORS settings

### Connection Closed

- Check network connectivity
- Verify WebSocket endpoint is configured
- Review server logs

### Events Not Received

- Verify event subscription
- Check event types match
- Review event publisher configuration
