"""
Workspace loader for IndoClaw.
Loads agent workspace files and injects them into prompts.

Each agent has its own workspace folder at ~/IndoClaw/workspaces/<agent_name>/
"""

import os
import sys
from typing import Dict, Optional, List
from pathlib import Path


class WorkspaceLoader:
    """
    Loads agent workspace files from the agent-specific workspace directory.
    Workspace structure:
    ~/IndoClaw/workspaces/
    └── <agent_name>/
        ├── SOUL.md
        ├── AGENTS.md
        ├── IDENTITY.md
        └── ...
    """
    
    def __init__(self, workspace_dir: str = None, agent_name: str = None):
        """
        Initialize the workspace loader.
        
        Args:
            workspace_dir: Path to the workspaces directory.
                          Defaults to ~/IndoClaw/workspaces/
            agent_name: Name of the agent (used to find agent's workspace folder).
                       If None, uses 'default' agent.
        """
        if workspace_dir is None:
            # Try to find workspaces in user's home directory first
            home_dir = Path.home()
            indo_claw_dir = home_dir / "IndoClaw"
            self.workspace_base_dir = indo_claw_dir / "workspaces"
            
            # If not found in home, try project root
            if not self.workspace_base_dir.exists():
                try:
                    project_root = Path(__file__).parent.parent.parent
                    self.workspace_base_dir = project_root / "workspaces"
                except:
                    # Fallback to current directory
                    self.workspace_base_dir = Path.cwd() / "workspaces"
        else:
            self.workspace_base_dir = Path(workspace_dir)
        
        # Set agent-specific workspace directory
        if agent_name:
            self.agent_name = agent_name
        else:
            self.agent_name = "default"
        
        # Start with agent-specific workspace, will fall back to base if needed
        self.workspace_dir = self.workspace_base_dir / self.agent_name
        
        self.loaded_files: Dict[str, str] = {}
    
    def load_agent_files(self, agent_name: str = None) -> Dict[str, str]:
        """
        Load all workspace files for an agent.
        First checks agent-specific folder for .md files, then falls back to common workspace.
        
        Args:
            agent_name: Name of the agent. If provided, updates the agent name.
        
        Returns:
            Dictionary mapping file names to their content
        """
        # Update agent name if provided
        if agent_name:
            self.agent_name = agent_name
        
        # Check agent-specific workspace folder first
        agent_workspace_dir = self.workspace_base_dir / self.agent_name
        
        # Start with agent workspace
        self.workspace_dir = agent_workspace_dir
        
        files = {}
        
        # Try agent-specific folder first
        if not self._load_files_from_dir(files):
            # Fall back to common workspace if agent folder doesn't have .md files
            self.workspace_dir = self.workspace_base_dir
            self._load_files_from_dir(files)
        
        return files
    
    def _load_files_from_dir(self, files: Dict[str, str]) -> bool:
        """
        Load workspace files from current workspace_dir.
        
        Args:
            files: Dictionary to populate with loaded files
        
        Returns:
            True if files were found, False otherwise
        """
        if not self.workspace_dir.exists():
            return False
        
        # Common workspace file names to load
        common_files = [
            "SOUL.md",
            "AGENTS.md", 
            "HEARTBEAT.md",
            "IDENTITY.md",
            "USER.md",
            "MEMORY.md",
            "TOOLS.md"
        ]
        
        files_found = False
        for filename in common_files:
            file_path = self.workspace_dir / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    files[filename] = content
                    self.loaded_files[filename] = content
                    files_found = True
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        return files_found
    
    def load_file(self, filename: str) -> Optional[str]:
        """
        Load a specific workspace file.
        
        Args:
            filename: Name of the file to load
        
        Returns:
            Content of the file, or None if not found
        """
        file_path = self.workspace_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding="utf-8")
            self.loaded_files[filename] = content
            return content
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def get_loaded_files(self) -> Dict[str, str]:
        """
        Get all currently loaded files.
        
        Returns:
            Dictionary of loaded file paths to content
        """
        return self.loaded_files
    
    def list_available_files(self) -> List[str]:
        """
        List all available workspace files.
        
        Returns:
            List of available file names
        """
        if not self.workspace_dir.exists():
            return []
        
        common_files = [
            "SOUL.md", "AGENTS.md", "HEARTBEAT.md",
            "IDENTITY.md", "USER.md", "MEMORY.md", "TOOLS.md"
        ]
        
        return [f for f in common_files if (self.workspace_dir / f).exists()]
    
    def clear_cache(self) -> None:
        """Clear the loaded files cache."""
        self.loaded_files.clear()


def create_workspace_loader(workspace_dir: str = None, agent_name: str = None) -> WorkspaceLoader:
    """Create a workspace loader with default settings."""
    return WorkspaceLoader(workspace_dir=workspace_dir, agent_name=agent_name)


def ensure_workspaces_exists() -> Path:
    """
    Ensure the workspaces directory exists. Creates it if it doesn't exist.
    
    Returns:
        Path to the workspaces directory
    """
    home_dir = Path.home()
    indo_claw_dir = home_dir / "IndoClaw"
    workspaces_dir = indo_claw_dir / "workspaces"
    
    # Create IndoClaw directory if it doesn't exist
    if not indo_claw_dir.exists():
        indo_claw_dir.mkdir(parents=True, exist_ok=True)
    
    # Create workspaces directory if it doesn't exist
    if not workspaces_dir.exists():
        workspaces_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default workspace files
        _create_default_workspace_files(workspaces_dir)
    
    return workspaces_dir


def _create_default_workspace_files(workspaces_dir: Path) -> None:
    """Create default workspace files if they don't exist."""
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
IndoClaw

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
IndoClaw

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
        file_path = workspaces_dir / filename
        file_path.write_text(content, encoding="utf-8")