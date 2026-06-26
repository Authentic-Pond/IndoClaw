"""Config API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

router = APIRouter()


class ConfigUpdate(BaseModel):
    llm: Optional[Dict] = None
    memory: Optional[Dict] = None
    agent: Optional[Dict] = None


@router.get("/config")
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
            "memory": {
                "short_term_capacity": settings.memory.short_term_capacity,
                "long_term_top_k": settings.memory.long_term_top_k,
                "embedding_model": settings.memory.embedding_model,
            },
            "agent": {
                "name": settings.agent.name,
                "role": settings.agent.role,
                "max_iterations": settings.agent.max_iterations,
                "verbose": settings.agent.verbose,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration."""
    try:
        from src.config.settings import settings

        if config_update.llm:
            settings.llm.model_name = config_update.llm.get("model_name", settings.llm.model_name)
            settings.llm.base_url = config_update.llm.get("base_url", settings.llm.base_url)
            settings.llm.temperature = config_update.llm.get("temperature", settings.llm.temperature)
            settings.llm.max_tokens = config_update.llm.get("max_tokens", settings.llm.max_tokens)

        if config_update.memory:
            settings.memory.short_term_capacity = config_update.memory.get("short_term_capacity", settings.memory.short_term_capacity)
            settings.memory.long_term_top_k = config_update.memory.get("long_term_top_k", settings.memory.long_term_top_k)

        if config_update.agent:
            settings.agent.name = config_update.agent.get("name", settings.agent.name)
            settings.agent.role = config_update.agent.get("role", settings.agent.role)
            settings.agent.max_iterations = config_update.agent.get("max_iterations", settings.agent.max_iterations)
            settings.agent.verbose = config_update.agent.get("verbose", settings.agent.verbose)

        return {"status": "updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
