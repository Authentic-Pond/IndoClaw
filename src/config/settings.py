"""
Configuration settings for IndoClaw AI Agent OS.
Uses workspace config (agent_config.json) as the single source of truth.
"""

from typing import Optional
from dataclasses import dataclass, field

# Import workspace config
try:
    from ..core.workspace.config import get_agent_config, AgentConfig as WorkspaceAgentConfig
    WORKSPACE_CONFIG_AVAILABLE = True
except ImportError:
    WORKSPACE_CONFIG_AVAILABLE = False


# Default configuration values (used when workspace config is not available)
DEFAULT_LLM_MODEL = "gemma4:26b"
DEFAULT_LLM_BASE_URL = "http://localhost:11434/v1"
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 4096
DEFAULT_SHORT_TERM_CAPACITY = 10
DEFAULT_LONG_TERM_TOP_K = 5
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_SHOW_TOOL_CALLING = False
DEFAULT_SHOW_THINKING = False
DEFAULT_THINKING_ENABLED = True
DEFAULT_MAX_SEARCH_RESULTS = 5
DEFAULT_FILE_OPERATION_TIMEOUT = 30
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_DATA_DIR = "./data"
DEFAULT_CACHE_DIR = "./data/cache"
DEFAULT_AGENT_NAME = "IndoClaw"
DEFAULT_AGENT_ROLE = "Autonomous AI Assistant"
DEFAULT_MAX_ITERATIONS = 10
DEFAULT_VERBOSE = True


def _get_workspace_config(agent_name: str = None) -> dict:
    """
    Get workspace configuration for an agent.
    
    Args:
        agent_name: Name of the agent. If None, uses default.
    
    Returns:
        Configuration dictionary from workspace
    """
    if not WORKSPACE_CONFIG_AVAILABLE:
        return {}
    
    try:
        config = get_agent_config(agent_name=agent_name).load()
        return config
    except Exception:
        return {}


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    
    def __post_init__(self):
        config = _get_workspace_config()
        self.model_name = config.get("llm_model", DEFAULT_LLM_MODEL)
        self.base_url = config.get("llm_base_url", DEFAULT_LLM_BASE_URL)
        self.api_key = config.get("llm_api_key")
        self.ollama_enabled = config.get("ollama_enabled", True)
        
        self.temperature = config.get("llm_temperature", DEFAULT_LLM_TEMPERATURE)
        self.max_tokens = config.get("llm_max_tokens", DEFAULT_LLM_MAX_TOKENS)
        self.api_base = "https://api.openai.com/v1"  # Default OpenAI API base


@dataclass
class MemoryConfig:
    """Configuration for memory system."""
    
    def __post_init__(self):
        config = _get_workspace_config()
        self.short_term_capacity = config.get("short_term_capacity", DEFAULT_SHORT_TERM_CAPACITY)
        self.long_term_top_k = config.get("long_term_top_k", DEFAULT_LONG_TERM_TOP_K)
        self.embedding_model = config.get("embedding_model", DEFAULT_EMBEDDING_MODEL)
        
        self.vector_db_path = config.get("vector_db_path", DEFAULT_DATA_DIR + "/chroma")


@dataclass
class ToolConfig:
    """Configuration for tools."""
    
    def __post_init__(self):
        config = _get_workspace_config()
        self.show_tool_calling = config.get("show_tool_calling", DEFAULT_SHOW_TOOL_CALLING)
        self.show_thinking = config.get("show_thinking", DEFAULT_SHOW_THINKING)
        self.thinking_enabled = config.get("thinking_enabled", DEFAULT_THINKING_ENABLED)
        
        self.max_web_search_results = config.get("max_web_search_results", DEFAULT_MAX_SEARCH_RESULTS)
        self.file_operation_timeout = config.get("file_operation_timeout", DEFAULT_FILE_OPERATION_TIMEOUT)


@dataclass(frozen=False)
class AgentConfig:
    """Configuration for the agent."""
    
    def __post_init__(self):
        config = _get_workspace_config()
        self.name = config.get("agent_name", DEFAULT_AGENT_NAME)
        self.role = config.get("agent_role", DEFAULT_AGENT_ROLE)
        self.max_iterations = config.get("max_iterations", DEFAULT_MAX_ITERATIONS)
        self.verbose = config.get("verbose", DEFAULT_VERBOSE)


@dataclass(frozen=False)
class Settings:
    """Main settings class."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    tool: ToolConfig = field(default_factory=ToolConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    
    # Global settings
    log_level: str = DEFAULT_LOG_LEVEL
    data_dir: str = DEFAULT_DATA_DIR
    cache_dir: str = DEFAULT_CACHE_DIR
    
    def set_agent_name(self, name: str) -> None:
        """Set the agent name and reload the agent config."""
        self.agent.name = name


# Global settings instance
settings = Settings()
