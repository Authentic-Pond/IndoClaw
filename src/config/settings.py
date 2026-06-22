"""
Configuration settings for IndoClaw AI Agent OS.
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Get the directory where this file is located
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from config directory
load_dotenv(os.path.join(CONFIG_DIR, '.env'))


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    model_name: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    api_base: Optional[str] = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    base_url: Optional[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"


@dataclass
class MemoryConfig:
    """Configuration for memory system."""
    short_term_capacity: int = int(os.getenv("SHORT_TERM_CAPACITY", "10"))
    long_term_top_k: int = int(os.getenv("LONG_TERM_TOP_K", "5"))
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/chroma")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


@dataclass
class ToolConfig:
    """Configuration for tools."""
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    max_web_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    file_operation_timeout: int = int(os.getenv("FILE_OPERATION_TIMEOUT", "30"))


@dataclass
class AgentConfig:
    """Configuration for the agent."""
    name: str = os.getenv("AGENT_NAME", "IndoClaw")
    role: str = os.getenv("AGENT_ROLE", "Autonomous AI Assistant")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
    verbose: bool = os.getenv("VERBOSE", "true").lower() == "true"


@dataclass
class Settings:
    """Main settings class."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    tool: ToolConfig = field(default_factory=ToolConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    
    # Global settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: str = os.getenv("DATA_DIR", "./data")
    cache_dir: str = os.getenv("CACHE_DIR", "./data/cache")


# Global settings instance
settings = Settings()