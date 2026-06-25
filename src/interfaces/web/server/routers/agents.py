"""
Agents API routes for IndoClaw Web Interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()


class AgentInfo(BaseModel):
    id: str
    name: str
    status: str
    role: Optional[str] = None
    last_active: Optional[str] = None


class AgentConfig(BaseModel):
    agent_name: str
    llm_model: str
    llm_base_url: str
    max_iterations: int
    verbose: bool


# In-memory agent info
agents: Dict[str, Dict] = {}


@router.get("/agents")
async def list_agents():
    """List all configured agents."""
    try:
        from src.config.settings import settings
        from src.core.workspace import list_agents as list_workspace_agents

        # Get workspace agents
        workspace_agents = list_workspace_agents()

        # Add default agent if not in workspace
        result = []
        for agent_id in workspace_agents:
            result.append(AgentInfo(
                id=agent_id,
                name=agent_id,
                status="idle",
                role="Autonomous AI Assistant"
            ))

        # Add default if empty
        if not result:
            result.append(AgentInfo(
                id="default",
                name=settings.agent.name,
                status="idle",
                role=settings.agent.role
            ))

        return {"agents": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details for a specific agent."""
    try:
        from src.config.settings import settings

        # Return default agent info
        return AgentInfo(
            id=agent_id,
            name=settings.agent.name,
            status="idle",
            role=settings.agent.role
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents")
async def create_agent(config: AgentConfig):
    """Create a new agent configuration."""
    try:
        from src.core.workspace import get_agent_config, ensure_agent_workspace

        # Save agent config
        workspace_config = get_agent_config(agent_name=config.agent_name)
        workspace_config.save(config.dict())

        # Ensure workspace files exist
        ensure_agent_workspace(config.agent_name)

        agents[config.agent_name] = config.dict()
        return {"status": "created", "agent_id": config.agent_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent configuration."""
    try:
        if agent_id in agents:
            del agents[agent_id]
        return {"status": "deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
