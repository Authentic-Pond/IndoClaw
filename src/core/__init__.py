"""
Core module for IndoClaw AI Agent OS.
"""

from .agent import IndoClawAgent, create_agent
from .memory.short_term import ShortTermMemory, Message
from .memory.long_term import LongTermMemory, MemoryEntry
from .memory.provider import BaseMemoryProvider, MemoryEntry as MemoryProviderEntry
from .tools.base import BaseTool, ToolResult
from .tools import _tool_registry as tool_registry
from .planning.planner import Planner, Plan, Task
from .adapters import OpenAIAdapter, OllamaAdapter
from .messaging import AgentMessage, AgentMessagePriority, AgentRegistry, DelegationTool
from .messaging import get_agent_registry
from ..agents import BaseAgent, ResearcherAgent, WriterAgent
from .observation import ThoughtTracer, TraceEntry, TraceLevel, get_tracer, set_tracer_enabled

__all__ = [
    "IndoClawAgent",
    "create_agent",
    "ShortTermMemory",
    "Message",
    "LongTermMemory",
    "MemoryEntry",
    "BaseMemoryProvider",
    "MemoryProviderEntry",
    "BaseTool",
    "ToolResult",
    "tool_registry",
    "Planner",
    "Plan",
    "Task",
    "OpenAIAdapter",
    "OllamaAdapter",
    "AgentMessage",
    "AgentMessagePriority",
    "AgentRegistry",
    "DelegationTool",
    "get_agent_registry",
    "BaseAgent",
    "ResearcherAgent",
    "WriterAgent",
    "ThoughtTracer",
    "TraceEntry",
    "TraceLevel",
    "get_tracer",
    "set_tracer_enabled",
]
