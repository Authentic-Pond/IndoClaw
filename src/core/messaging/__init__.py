"""
Multi-agent messaging for IndoClaw.
Provides AgentMessage schema, AgentRegistry for agent communication,
and interactive prompts for agent-user interaction.
"""

from .agent_message import AgentMessage, AgentMessagePriority
from .agent_registry import AgentRegistry, get_agent_registry
from .delegation_tool import DelegationTool
from .interactive import (
    InteractivePrompts,
    InteractivePrompt,
    PromptResponse,
    PromptType,
    confirm,
    select,
    text_input,
    number_input,
    interactive_prompts,
)

__all__ = [
    "AgentMessage",
    "AgentMessagePriority",
    "AgentRegistry",
    "DelegationTool",
    "get_agent_registry",
    "InteractivePrompts",
    "InteractivePrompt",
    "PromptResponse",
    "PromptType",
    "confirm",
    "select",
    "text_input",
    "number_input",
    "interactive_prompts",
]
