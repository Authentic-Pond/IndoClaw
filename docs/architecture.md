# IndoClaw Web Interface - Architecture

## System Overview

The IndoClaw Web Interface consists of three main components:

1. **Frontend (Next.js 14)** - Single Page Application with routing and components
2. **Backend (FastAPI)** - REST API and WebSocket server for real-time communication
3. **Core (Python)** - Existing IndoClaw agent framework

### Component Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Browser                               │
│                          │                                      │
│                          ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Frontend (Next.js)                    │  │
│  │  - Pages (App Router)                                    │  │
│  │  - Components (React)                                    │  │
│  │  - State Management (Zustand)                           │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │ REST API & WebSocket                     │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────┐  │
│  │  REST API   │  │ WebSocket   │  │  Event Publisher      │  │
│  │  Routes     │  │ Handler     │  │  & Event Bus          │  │
│  └─────────────┘  └─────────────┘  └───────────────────────┘  │
│                     │                                          │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  IndoClaw Core (Python)                        │
│  - Agent Engine                                                │
│  - Tool Registry                                               │
│  - Memory System                                               │
│  - Event Publisher                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### App Router Structure

```
app/
├── layout.tsx               # Root layout with theme provider
├── page.tsx                 # Dashboard/home page
├── chat/                    # Chat interface
│   └── page.tsx
├── agents/                  # Agent management
│   └── page.tsx
├── config/                  # Configuration panel
│   └── page.tsx
├── events/                  # Event viewer
│   └── page.tsx
├── globals.css              # Global styles
├── layout.tsx               # Nested layout (if needed)
└── page.tsx                 # Page content
```

### Component Structure

```
components/
├── layout/
│   ├── Sidebar.tsx          # Sidebar with navigation
│   └── MainLayout.tsx       # Main layout wrapper
└── ui/                      # Reusable UI components
    ├── Button.tsx
    ├── Input.tsx
    ├── Card.tsx
    └── ...
```

### State Management

The frontend uses **Zustand** for client-side state management:

```typescript
// Example: Chat state
const useChatStore = create((set) => ({
  messages: [],
  loading: false,
  agentId: 'default',
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  clearMessages: () => set({ messages: [] })
}));
```

## Backend Architecture

### API Routes

```
routers/
├── chat.py       # Chat-related endpoints
├── agents.py     # Agent management endpoints
├── config.py     # Configuration endpoints
└── events.py     # Event retrieval endpoints
```

### WebSocket Handler

```
ws_handler.py
├── WebSocketConnection    # Individual client connection
├── WebSocketManager       # Connection management
│   ├── connections       # Active connections
│   ├── event_queue       # Event broadcasting queue
│   └── broadcast()       # Broadcast to all clients
```

### Event Flow

```
Agent Event (Python) → EventPublisher → WebSocketManager → WebSocket → Frontend
```

## Data Flow

### Chat Interaction Flow

```
User Input → Frontend → POST /api/chat → Backend → IndoClaw Agent → Response → Frontend
```

1. User types message in chat UI
2. Frontend sends POST to `/api/chat`
3. Backend routes to `chat.py` handler
4. Handler creates IndoClaw agent
5. Agent processes message
6. Response sent back to frontend
7. Frontend displays response

### Real-time Event Flow

```
Agent Action → EventPublisher → WebSocketManager → Broadcast → All Connected Clients
```

1. Agent performs action (task_start, tool_executed, etc.)
2. EventPublisher publishes event
3. WebSocketManager queues event
4. Broadcast to all connected WebSocket clients
5. Frontend receives and displays event

## Styling Architecture

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        // ... theme colors
      }
    }
  }
}
```

### CSS Variables

```css
/* globals.css */
:root {
  --background: #ffffff;
  --foreground: #16161a;
  --primary: #6366f1;
  --secondary: #f3f4f6;
  --border: #e4e4e7;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
    --primary: #818cf8;
    --secondary: #171717;
    --border: #262626;
  }
}
```

## Security Considerations

1. **CORS**: Configured to allow all origins (dev only)
2. **Input Validation**: Pydantic models validate all API inputs
3. **Agent Isolation**: Each agent runs in its own context
4. **Error Handling**: Comprehensive error handling with proper status codes

## Performance Optimization

1. **Static Generation**: Next.js pre-renders pages
2. **Client-side Routing**: No page reloads on navigation
3. **WebSocket Reuse**: Single WebSocket connection for all events
4. **Event Filtering**: Client-side filtering of event types

## Error Handling

```typescript
// Frontend error handling
try {
  const response = await fetch("/api/chat", {...});
  if (!response.ok) throw new Error(response.statusText);
  const data = await response.json();
} catch (error) {
  console.error("API Error:", error);
  // Display error to user
}
```

```python
# Backend error handling
@app.get("/api/agents")
async def list_agents():
    try:
        # ... logic
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
