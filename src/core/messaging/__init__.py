"""
Multi-agent messaging for IndoClaw.
Provides AgentMessage schema and AgentRegistry for agent communication.
"""

from .agent_message import AgentMessage, AgentMessagePriority
from .agent_registry import AgentRegistry, get_agent_registry
from .delegation_tool import DelegationTool

__all__ = [
    "AgentMessage",
    "AgentMessagePriority",
    "AgentRegistry",
    "DelegationTool",
    "get_agent_registry",
]
