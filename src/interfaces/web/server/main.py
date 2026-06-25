"""
FastAPI server for IndoClaw Web Interface.
Provides REST API and WebSocket support for real-time events.
"""
import os
import sys
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ws_handler import ws_manager
from routers import chat, agents, config, events

# Create FastAPI app
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    client_id = websocket.headers.get("x-client-id", "unknown")
    connection = await ws_manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")
                continue

            # Handle subscription messages
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    for event_type in message.get("events", []):
                        connection.subscribe(event_type)
                elif message.get("type") == "unsubscribe":
                    for event_type in message.get("events", []):
                        connection.unsubscribe(event_type)
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    try:
        from src.config.settings import settings
        return {
            "llm": {
                "model_name": settings.llm.model_name,
                "base_url": settings.llm.base_url,
                "temperature": settings.llm.temperature,
                "max_tokens": settings.llm.max_tokens,
            },
            "agent": {
                "name": settings.agent.name,
                "role": settings.agent.role,
                "max_iterations": settings.agent.max_iterations,
            },
            "memory": {
                "short_term_capacity": settings.memory.short_term_capacity,
                "long_term_top_k": settings.memory.long_term_top_k,
            },
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Serve static files (for production builds)
@app.get("/{full_path:path}")
async def serve_static(request: Request, full_path: str):
    """Serve static files or index.html for SPA routing."""
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"

    if not full_path or full_path == "":
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Not found"}

    file_path = static_dir / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    # For SPA, return index.html for any unknown paths
    if index_file.exists():
        return FileResponse(index_file)

    return JSONResponse(status_code=404, content={"error": "Not found"})


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    import uvicorn
    ws_manager.start_broadcasting()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()
