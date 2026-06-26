# IndoClaw Web Interface - API Documentation

## Overview

The web interface provides a REST API and WebSocket endpoint for communication between the frontend and backend.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required (development mode). In production, implement JWT or session-based authentication.

## Common Response Formats

### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

## REST API Endpoints

### Chat Endpoints

#### Send Message

```http
POST /api/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "agent_id": "default"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you!",
  "agent_id": "default",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you!",
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ]
}
```

**Errors:**
- `400` - Invalid request body
- `500` - Agent processing error

#### Get Chat History

```http
GET /api/chat/history/{agent_id}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Errors:**
- `404` - Agent not found

#### Clear Chat History

```http
DELETE /api/chat/history/{agent_id}
```

**Response:**
```json
{
  "status": "cleared"
}
```

### Agent Endpoints

#### List Agents

```http
GET /api/agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "default",
      "name": "IndoClaw",
      "status": "idle",
      "role": "Autonomous AI Assistant"
    }
  ]
}
```

#### Get Agent Details

```http
GET /api/agents/{agent_id}
```

**Response:**
```json
{
  "id": "default",
  "name": "IndoClaw",
  "status": "idle",
  "role": "Autonomous AI Assistant"
}
```

**Errors:**
- `404` - Agent not found

#### Create Agent

```http
POST /api/agents
Content-Type: application/json
```

**Request Body:**
```json
{
  "agent_name": "new_agent",
  "llm_model": "gemma4:26b",
  "llm_base_url": "http://localhost:11434/v1",
  "max_iterations": 10,
  "verbose": true
}
```

**Response:**
```json
{
  "status": "created",
  "agent_id": "new_agent"
}
```

**Errors:**
- `400` - Invalid request body
- `409` - Agent already exists

#### Delete Agent

```http
DELETE /api/agents/{agent_id}
```

**Response:**
```json
{
  "status": "deleted"
}
```

**Errors:**
- `404` - Agent not found

### Configuration Endpoints

#### Get Configuration

```http
GET /api/config
```

**Response:**
```json
{
  "llm": {
    "model_name": "gemma4:26b",
    "base_url": "http://localhost:11434/v1",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "memory": {
    "short_term_capacity": 10,
    "long_term_top_k": 5,
    "embedding_model": "text-embedding-3-small"
  },
  "agent": {
    "name": "IndoClaw",
    "role": "Autonomous AI Assistant",
    "max_iterations": 10,
    "verbose": true
  }
}
```

#### Update Configuration

```http
POST /api/config
Content-Type: application/json
```

**Request Body:**
```json
{
  "llm": {
    "model_name": "llama3:8b"
  },
  "agent": {
    "name": "New Agent Name"
  }
}
```

**Response:**
```json
{
  "status": "updated"
}
```

### Event Endpoints

#### Get Events

```http
GET /api/events
Query: ?event_type=task_start&limit=100
```

**Query Parameters:**
- `event_type` - Filter by event type
- `limit` - Number of events to return (default: 100)

**Response:**
```json
{
  "events": [
    {
      "event_type": "task_start",
      "timestamp": "2024-01-01T00:00:00Z",
      "agent_id": "default",
      "payload": {
        "task": "What is 25 * 17?"
      },
      "metadata": {}
    }
  ]
}
```

#### Get Event Types

```http
GET /api/events/types
```

**Response:**
```json
{
  "types": [
    "task_start",
    "task_end",
    "tool_executed",
    "tool_approval_needed",
    "error",
    "plan_created",
    "plan_approved",
    "input_requested",
    "input_received",
    "agent_thought",
    "memory_updated"
  ]
}
```

#### Clear Events

```http
DELETE /api/events
```

**Response:**
```json
{
  "status": "cleared"
}
```

## WebSocket API

### Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8000/ws
```

### Events

#### subscribe

Subscribe to event types.

```json
{
  "type": "subscribe",
  "events": ["task_start", "task_end", "tool_executed"]
}
```

#### unsubscribe

Unsubscribe from event types.

```json
{
  "type": "unsubscribe",
  "events": ["task_start"]
}
```

#### event

Server broadcasts events to subscribed clients.

```json
{
  "type": "event",
  "event": {
    "event_type": "task_start",
    "timestamp": "2024-01-01T00:00:00Z",
    "agent_id": "default",
    "payload": {
      "task": "What is 25 * 17?"
    },
    "metadata": {}
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Backend error |
| 503 | Service Unavailable - Backend unavailable |

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing in production:
- 100 requests per minute per IP
- 10 WebSocket connections per IP

## CORS

Currently allows all origins (`*`). Configure for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)
```
