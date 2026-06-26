# IndoClaw Web Interface Documentation

## Overview

The IndoClaw Web Interface is a modern, responsive web application built with Next.js 14 and FastAPI that provides a dashboard for managing AI agents, chat interactions, configuration, and real-time event monitoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IndoClaw Web Interface                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐       WebSocket       ┌──────────────────┐    │
│  │   Frontend   │◄─────────────────────►│   FastAPI        │    │
│  │   (Next.js)  │                       │   Backend        │    │
│  │              │       REST API        │                  │    │
│  │  - Chat UI   │◄─────────────────────►│  - REST Routes   │    │
│  │  - Agents    │                       │  - WebSocket     │    │
│  │  - Config    │                       │  - Event Bus     │    │
│  │  - Events    │                       │                  │    │
│  └──────────────┘                       └──────────────────┘    │
│                                                   │             │
│                                           ┌───────▼───────┐     │
│                                           │  IndoClaw     │     │
│                                           │  Core (Python)│     │
│                                           └───────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Install IndoClaw with web interface dependencies
pip install -e .

# Or use the web interface installer
indoclaw web install
```

### Running the Web Interface

```bash
# Start the web interface server
indoclaw web start

# Start on a custom port
indoclaw web start --port 3000
```

The web interface will be available at `http://localhost:8000`

### Stopping the Server

```bash
# Stop the web interface
indoclaw web stop
```

## Directory Structure

```
docs/
├── README.md                     # This file
├── architecture.md               # System architecture details
├── frontend/                     # Frontend documentation
│   ├── README.md
│   ├── components.md
│   ├── pages.md
│   └── styling.md
├── backend/                      # Backend documentation
│   ├── README.md
│   ├── api.md
│   └── websocket.md
├── getting-started.md            # Getting started guide
└── developer-guide.md            # Development guide

src/interfaces/web/
├── client/                       # Next.js frontend
│   ├── app/                      # App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utility functions
│   └── public/                   # Static assets
└── server/                       # FastAPI backend
    ├── main.py                   # Application entry point
    ├── routers/                  # API route handlers
    │   ├── chat.py
    │   ├── agents.py
    │   ├── config.py
    │   └── events.py
    └── ws_handler.py             # WebSocket manager
```

## Features

### Dashboard
- Overview of active agents
- Quick navigation to all sections
- System health indicators

### Chat Interface
- Real-time conversation with agents
- Message history management
- Agent selection
- Loading states and response streaming

### Agent Management
- List and view all configured agents
- Agent status indicators
- Quick actions (chat, delete)

### Configuration
- LLM settings (model, URL, temperature)
- Memory configuration
- Agent-specific settings

### Event Viewer
- Real-time event streaming
- Event filtering by type
- Payload and metadata display

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State**: Zustand (for client-side state)
- **Icons**: Lucide React
- **Theme**: next-themes

### Backend
- **Framework**: FastAPI
- **WebSocket**: Built-in WebSocket support
- **Validation**: Pydantic
- **Server**: Uvicorn

## Configuration

The web interface reads configuration from the standard IndoClaw settings:

```python
# ~/.indoclaw/settings.json
{
  "default_agent": "IndoClaw",
  "agents": {
    "IndoClaw": {
      "llm_provider": "ollama",
      "llm_model": "gemma4:26b",
      "llm_base_url": "http://localhost:11434/v1",
      "max_iterations": 10,
      "verbose": true
    }
  }
}
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a message to an agent
- `GET /api/chat/history/{agent_id}` - Get chat history
- `DELETE /api/chat/history/{agent_id}` - Clear chat history

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{agent_id}` - Get agent details
- `POST /api/agents` - Create a new agent
- `DELETE /api/agents/{agent_id}` - Delete an agent

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration

### Events
- `GET /api/events` - Get event history
- `GET /api/events/types` - Get available event types
- `DELETE /api/events` - Clear event history

## WebSocket Events

### Subscribe to Events
```javascript
wsClient.subscribe(["task_start", "task_end", "tool_executed"])
```

### Event Types
- `task_start` - Agent started processing a task
- `task_end` - Agent completed a task
- `tool_executed` - A tool was executed
- `error` - An error occurred
- `plan_created` - A plan was generated
- `plan_approved` - A plan was approved

## Development

### Frontend Development

```bash
cd src/interfaces/web/client

# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Development

```bash
cd src/interfaces/web/server

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
indoclaw web start --port 8080
```

### Dependencies Missing
```bash
# Reinstall web interface
indoclaw web install
```

### Connection Issues
Ensure the IndoClaw core is properly configured with an LLM provider before starting the web interface.

## License

Apache 2.0 - See LICENSE file for details.
