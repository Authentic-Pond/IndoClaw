"""
Base class for all IndoClaw tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    content: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """Base class for all tools."""
    
    name: str = "BaseTool"
    description: str = "Base tool class"
    
    def __init__(self):
        self.enabled = True
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def enable(self) -> None:
        """Enable the tool."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the tool."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if tool is enabled."""
        return self.enabled
    
    def get_info(self) -> Dict[str, str]:
        """Get tool information."""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": str(self.enabled)
        }