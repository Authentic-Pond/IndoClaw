# IndoClaw Web Interface - API Reference

## Frontend API

### WebSocket Client

```typescript
import { wsClient } from '@/lib/ws-client';

// Connect
await wsClient.connect();

// Subscribe to events
wsClient.subscribe(['task_start', 'task_end']);

// Listen for events
wsClient.on('event', (data) => {
  console.log('Event:', data);
});

// Unsubscribe
wsClient.unsubscribe(['task_start']);

// Disconnect
wsClient.disconnect();
```

### API Client

```typescript
import { apiClient } from '@/lib/api-client';

// GET
const data = await apiClient.get('/agents');

// POST
const response = await apiClient.post('/chat', {
  message: 'Hello',
  agent_id: 'default'
});

// DELETE
await apiClient.delete('/chat/history/default');
```

## Backend API

### Python Imports

```python
from src.interfaces.web.server.ws_handler import ws_manager
from src.interfaces.web.server.main import app
from src.interfaces.web.server.routers.chat import router
```

### Event Publisher Integration

```python
from src.core.events.publisher import EventPublisher, EventType

# Publish an event
EventPublisher().publish(
    event_type=EventType.TASK_START,
    agent_id='default',
    payload={'task': 'What is 25 * 17?'}
)
```

## Configuration

### Frontend Configuration

```typescript
// lib/config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  websocketUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
};
```

### Backend Configuration

```python
# .env
INDOCLAW_CONFIG_PATH=~/.indoclaw/settings.json
LOG_LEVEL=INFO
```

## Environment Variables

### Frontend

| Variable | Description | Default |
|--|-----------|--|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |
| NEXT_PUBLIC_WS_URL | WebSocket URL | ws://localhost:8000 |

### Backend

| Variable | Description | Default |
|--|-----------|--|
| INDOCLAW_CONFIG_PATH | Path to IndoClaw settings | ~/.indoclaw/settings.json |
| LOG_LEVEL | Log level (DEBUG, INFO, WARNING, ERROR) | INFO |
| PORT | Server port | 8000 |

## CLI Commands

```bash
# Start the web interface
indoclaw web start

# Start on custom port
indoclaw web start --port 8080

# Install web interface dependencies
indoclaw web install

# Stop the web interface
indoclaw web stop
```

## Error Codes

### Frontend

| Code | Description |
|--|-----------|
| 0 | WebSocket connection closed |
| 1001 | WebSocket server is going away |
| 1002 | WebSocket protocol error |
| 1003 | WebSocket unsupported data |
| 1006 | WebSocket connection closed abnormally |

### Backend

| Code | Description |
|--|-----------|
| 4000-4999 | Custom WebSocket errors |
| 1000 | Normal closure |
| 1001 | Server shutting down |
| 1002 | Protocol error |
| 1003 | Unsupported data |
