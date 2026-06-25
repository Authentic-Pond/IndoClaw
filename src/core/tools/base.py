"""
Base class for all IndoClaw tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

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
    """Base class for all tools with P/dantic-based input validation."""

    name: str = "BaseTool"
    description: str = "Base tool class"
    input_schema: Optional[Type[BaseModel]] = None

    def __init__(self):
        self.enabled = True

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
            "enabled": str(self.enabled),
            "has_schema": self.input_schema is not None
        }

    def execute(self, **kwargs) -> ToolResult:
        """
        The entry point for executing a tool.
        Handles parameter validation using the input_schema if provided.
        """
        if not self.is_enabled():
            return ToolResult(success=False, error=f"Tool '{self.name}' is disabled.")

        # Validate parameters if schema is present
        if self.input_schema:
            try:
                self.input_schema(**kwargs)
            except ValidationError as e:
                return ToolResult(success=False, error=f"Validation Error: {str(e)}")
            except Exception as e:
                return ToolResult(success=False, error=f"Unexpected error during validation: {str(e)}")

        try:
            return self._run(**kwargs)
        except Exception as e:
            return ToolResult(success=False, error=f"Execution Error: {str(e)}")

    @abstractmethod
    def _run(self, **kwargs) -> ToolResult:
        """
        The actual logic of the tool. Subclasses must implement this.
        """
        pass
