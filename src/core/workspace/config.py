"""
Workspace configuration for IndoClaw.
Handles agent configuration loaded from workspaces/<agent_name>/agent_config.json

Each agent has its own workspace folder with isolated configuration.
"""

import os
import json
from typing import Dict, Optional, Any, Tuple
from pathlib import Path


class AgentConfig:
    """
    Manages agent configuration loaded from workspaces/<agent_name>/agent_config.json.
    On first run, creates a default configuration file.
    
    Workspace structure:
    ~/IndoClaw/workspaces/
    └── <agent_name>/
        ├── agent_config.json
        ├── SOUL.md
        ├── AGENTS.md
        ├── IDENTITY.md
        └── ...
    """
    
    DEFAULT_CONFIG = {
        "agent_name": "IndoClaw",
        "llm_provider": "ollama",
        "llm_model": "gemma4:26b",
        "llm_base_url": "http://localhost:11434/v1",
        "llm_api_key": None,
        "default_channel": "console",
        "max_iterations": 10,
        "verbose": True,
        "thinking_enabled": True,
        "show_tool_calling": False,
        "show_thinking": False,
        "short_term_capacity": 10,
        "long_term_top_k": 5,
        "embedding_model": "text-embedding-3-small",
        "ollama_enabled": True
    }
    
    def __init__(self, workspace_dir: str = None, agent_name: str = None):
        """
        Initialize the agent config loader.
        
        Args:
            workspace_dir: Path to the workspaces directory.
                          Defaults to ~/IndoClaw/workspaces/
            agent_name: Name of the agent (used for workspace folder).
                       If None, uses default agent folder.
        """
        if workspace_dir is None:
            home_dir = Path.home()
            self.workspace_base_dir = home_dir / "IndoClaw" / "workspaces"
        else:
            self.workspace_base_dir = Path(workspace_dir)
        
        # Determine agent-specific workspace directory
        if agent_name:
            self.agent_name = agent_name
            self.workspace_dir = self.workspace_base_dir / agent_name
        else:
            self.agent_name = "default"
            self.workspace_dir = self.workspace_base_dir / "default"
        
        self.config_file = self.workspace_dir / "agent_config.json"
        self.config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """
        Load agent configuration from agent_config.json.
        Returns empty dict if not found (no auto-creation).
        
        Returns:
            Dictionary containing agent configuration
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Merge with defaults for any missing keys
            for key, value in self.DEFAULT_CONFIG.items():
                if key not in self.config:
                    self.config[key] = value
                    self._save()
            
            return self.config
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.config_file}: {e}")
            return {}
    
    def save(self, config: Dict[str, Any]) -> None:
        """
        Save agent configuration to agent_config.json.
        
        Args:
            config: Dictionary containing configuration to save
        """
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        self.config = config
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.DEFAULT_CONFIG, f, indent=2)
        self.config = self.DEFAULT_CONFIG.copy()
    
    def _save(self) -> None:
        """Save current config to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration values
        """
        return self.config.copy()

    @staticmethod
    def get_default_workspace_dir() -> Path:
        """
        Get the default workspaces directory path.
        
        Returns:
            Path to the workspaces directory
        """
        home_dir = Path.home()
        return home_dir / "IndoClaw" / "workspaces"


def get_agent_config(workspace_dir: str = None, agent_name: str = None) -> AgentConfig:
    """
    Get an agent config instance.
    
    Args:
        workspace_dir: Path to workspaces directory
        agent_name: Name of the agent (used for workspace folder)
    
    Returns:
        AgentConfig instance
    """
    return AgentConfig(workspace_dir=workspace_dir, agent_name=agent_name)


def list_agents(workspace_dir: str = None) -> list:
    """
    List all available agents.
    
    Args:
        workspace_dir: Path to workspaces directory
    
    Returns:
        List of agent names
    """
    if workspace_dir is None:
        home_dir = Path.home()
        workspace_base = home_dir / "IndoClaw" / "workspaces"
    else:
        workspace_base = Path(workspace_dir)
    
    if not workspace_base.exists():
        return []
    
    agents = []
    for item in workspace_base.iterdir():
        if item.is_dir() and (item / "agent_config.json").exists():
            agents.append(item.name)
    
    return agents


def ensure_agent_workspace(agent_name: str, workspace_dir: str = None) -> Path:
    """
    Ensure workspace folder and files exist for an agent.
    Only creates the workspace if it doesn't exist (on first run).
    Does NOT create workspace files - these should be created by the user.
    
    Args:
        agent_name: Name of the agent
        workspace_dir: Path to workspaces directory
    
    Returns:
        Path to the agent's workspace directory
    """
    if workspace_dir is None:
        home_dir = Path.home()
        workspace_base = home_dir / "IndoClaw" / "workspaces"
    else:
        workspace_base = Path(workspace_dir)
    
    agent_workspace = workspace_base / agent_name
    
    # Create agent workspace directory if it doesn't exist
    if not agent_workspace.exists():
        agent_workspace.mkdir(parents=True, exist_ok=True)
    
    return agent_workspace


def _create_agent_workspace_files(workspace_dir: Path) -> None:
    """Create default workspace files for an agent."""
    default_files = {
        "SOUL.md": """# SOUL.md - Agent Soul & Mission

## Purpose
The core identity and mission of this agent.

## Vision
Long-term goals and aspirations.

## Values
Core principles guiding the agent's behavior.
""",
        "AGENTS.md": """# AGENTS.md - Agent Specifications

## Agent Name
Agent

## Description
Autonomous AI agent operating system.

## Capabilities
- Task execution
- Memory management
- Tool usage

## Personality
- Helpful
- Efficient
- Adaptive
""",
        "HEARTBEAT.md": """# HEARTBEAT.md - Agent Status

## Status
Active

## Last Update
YYYY-MM-DD HH:MM:SS

## Health Metrics
- CPU: N/A
- Memory: N/A
- Uptime: N/A
""",
        "IDENTITY.md": """# IDENTITY.md - Agent Identity

## Agent Name
Agent

## Role
Autonomous AI Assistant

## Persona
- Compassionate
- Wise
- Guiding

## Tone
- Professional
- Clear
- Helpful
""",
        "USER.md": """# USER.md - User Interaction

## User Profile
- Name: Admin
- Role: System Administrator

## Interaction Guidelines
- Provide clear, actionable guidance
- Maintain consistency
- Support user decision-making

## Preferences
- Direct communication
- Actionable insights
- Values-aligned suggestions
""",
        "MEMORY.md": """# MEMORY.md - Memory Configuration

## Short-term Memory
- Current session context
- Recent interactions
- Active tasks

## Long-term Memory
- Historical patterns
- Learned behaviors
- Key insights

## Memory Persistence
- Enable: Yes
- Storage: Local
- TTL: Session-based
""",
        "TOOLS.md": """# TOOLS.md - Available Tools

## Available Tools
- File system operations
- Data analysis
- Code generation
- Web browsing
- Database operations

## Tool Preferences
- Use most efficient method
- Prefer local operations when possible
- Cross-validate critical operations

## Tool Limitations
- Memory constraints
- Processing time
- API rate limits
"""
    }
    
    for filename, content in default_files.items():
        file_path = workspace_dir / filename
        file_path.write_text(content, encoding="utf-8")
