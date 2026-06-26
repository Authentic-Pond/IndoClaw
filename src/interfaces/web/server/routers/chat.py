"""
Chat API routes for IndoClaw Web Interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent_id: str
    messages: List[ChatMessage]


# In-memory chat history
chat_history: dict = {}


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Send a message to the agent and get a response."""
    try:
        from src.core.agent import create_agent
        from src.config.settings import settings

        agent_id = request.agent_id or "default"

        # Get or create agent
        if agent_id not in chat_history:
            chat_history[agent_id] = []

        # Create agent
        agent = create_agent(verbose=False)

        # Run agent with message
        result = agent.run(request.message)

        # Update history
        chat_history[agent_id].extend([
            ChatMessage(role="user", content=request.message, timestamp=""),
            ChatMessage(role="assistant", content=result.response, timestamp=""),
        ])

        return ChatResponse(
            response=result.response,
            agent_id=agent_id,
            messages=chat_history[agent_id],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{agent_id}")
async def get_chat_history(agent_id: str):
    """Get chat history for a specific agent."""
    if agent_id not in chat_history:
        return {"messages": []}
    return {"messages": chat_history[agent_id]}


@router.delete("/chat/history/{agent_id}")
async def clear_chat_history(agent_id: str):
    """Clear chat history for a specific agent."""
    if agent_id in chat_history:
        chat_history[agent_id] = []
    return {"status": "cleared"}
