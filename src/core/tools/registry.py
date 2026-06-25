from typing import Dict, List, Optional, Type
from .base import BaseTool

class ToolRegistry:
    """
    Registry for all available tools in IndoClaw.
    Allows dynamic discovery and management of tools.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: An instance of a class inheriting from BaseTool.
        """
        if not tool.is_enabled():
            return

        self._tools[tool.name] = tool

    def register_multiple(self, tools: List[BaseTool]) -> int:
        """
        Register multiple tools at once.

        Args:
            tools: A list of BaseTool instances.

        Returns:
            The number of tools successfully registered.
        """
        count = 0
        for tool in tools:
            if tool.is_enabled():
                self._tools[tool.name] = tool
                count += 1
        return count

    def unregister(self, name: str) -> None:
        """
        Unregister a tool by name.

        Args:
            name: The name of the tool to remove.
        """
        if name in self._tools:
            del self._tools[name]

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Retrieve a tool by name.

        Args:
            name: The name of the tool.

        Returns:
            The tool instance if found, otherwise None.
        """
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """
        List all registered tools and their descriptions.

        Returns:
            A dictionary mapping tool names to descriptions.
        """
        return {name: tool.description for name, tool in self._tools.items()}

    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Return all registered tool instances."""
        return self._tools
