"""
Tools available to IndoClaw agents.
"""

from .base import BaseTool, ToolResult
from .web_search import WebSearchTool
from .file_ops import FileOperationTool
from .calculation import CalculatorTool
from .llm_call import LLMCallTool
from .duckduckgo_search import DuckDuckGoSearchTool
from .registry import ToolRegistry

# Auto-register all tools on import
_tool_registry = ToolRegistry()
_tool_registry.register_multiple([
    WebSearchTool(),
    FileOperationTool(),
    CalculatorTool(),
    LLMCallTool(),
    DuckDuckGoSearchTool(),
])

__all__ = [
    "BaseTool",
    "ToolResult",
    "WebSearchTool",
    "FileOperationTool",
    "CalculatorTool",
    "LLMCallTool",
    "DuckDuckGoSearchTool",
    "ToolRegistry",
    "_tool_registry",
]
