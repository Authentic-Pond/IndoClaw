"""
Config API routes for IndoClaw Web Interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()


class LLMConfig(BaseModel):
    model_name: str
    base_url: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class MemoryConfig(BaseModel):
    short_term_capacity: int = 10
    long_term_top_k: int = 5
    embedding_model: Optional[str] = None


class AgentConfig(BaseModel):
    name: str
    role: str
    max_iterations: int = 10
    verbose: bool = True


class ConfigUpdate(BaseModel):
    llm: Optional[LLMConfig] = None
    memory: Optional[MemoryConfig] = None
    agent: Optional[AgentConfig] = None


@router.get("/config")
async def get_config():
    """Get current configuration."""
    try:
        from src.config.settings import settings

        return {
            "llm": {
                "model_name": settings.llm.model_name,
                "base_url": settings.llm.base_url,
                "api_key": settings.llm.api_key is not None,
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
            settings.llm.model_name = config_update.llm.model_name
            settings.llm.base_url = config_update.llm.base_url
            settings.llm.temperature = config_update.llm.temperature
            settings.llm.max_tokens = config_update.llm.max_tokens

        if config_update.memory:
            settings.memory.short_term_capacity = config_update.memory.short_term_capacity
            settings.memory.long_term_top_k = config_update.memory.long_term_top_k

        if config_update.agent:
            settings.agent.name = config_update.agent.name
            settings.agent.role = config_update.agent.role
            settings.agent.max_iterations = config_update.agent.max_iterations
            settings.agent.verbose = config_update.agent.verbose

        return {"status": "updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
