"""
Agent message schema for IndoClaw multi-agent communication.
Implements the communication format defined in Project documentation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class AgentMessagePriority(Enum):
    """Priority levels for agent messages."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AgentMessage:
    """
    Structured message for agent-to-agent communication.

    Format as defined in project documentation:
    - Sender
    - Receiver
    - Task
    - Context
    - Expected Output
    - Priority
    """

    sender: str
    """The ID/name of the sending agent."""

    receiver: str
    """The ID/name of the receiving agent."""

    task: str
    """The task to be performed by the receiver."""

    context: Dict[str, str] = field(default_factory=dict)
    """Additional context for the task (e.g., background info, constraints)."""

    expected_output: Optional[str] = None
    """Description of the expected output format or result."""

    priority: AgentMessagePriority = field(default=AgentMessagePriority.NORMAL)
    """Message priority level."""

    message_id: Optional[str] = None
    """Unique message ID for tracking."""

    timestamp: datetime = field(default_factory=datetime.now)
    """When the message was created."""

    response_to: Optional[str] = None
    """Message ID this is responding to (for conversation threads)."""

    metadata: Dict[str, str] = field(default_factory=dict)
    """Additional metadata (e.g., session_id, trace_id)."""

    def __post_init__(self):
        """Ensure metadata is always a dict."""
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "task": self.task,
            "context": self.context,
            "expected_output": self.expected_output,
            "priority": self.priority.value,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "response_to": self.response_to,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        """Create message from dictionary."""
        priority = AgentMessagePriority(data.get("priority", "normal"))
        timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))

        return cls(
            sender=data.get("sender", "unknown"),
            receiver=data.get("receiver", "unknown"),
            task=data.get("task", ""),
            context=data.get("context", {}),
            expected_output=data.get("expected_output"),
            priority=priority,
            message_id=data.get("message_id"),
            timestamp=timestamp,
            response_to=data.get("response_to"),
            metadata=data.get("metadata", {}),
        )

    def set_priority(self, priority: AgentMessagePriority) -> "AgentMessage":
        """Set message priority and return self for chaining."""
        self.priority = priority
        return self

    def add_context(self, key: str, value: str) -> "AgentMessage":
        """Add context key-value pair and return self for chaining."""
        self.context[key] = value
        return self

    def add_metadata(self, key: str, value: str) -> "AgentMessage":
        """Add metadata key-value pair and return self for chaining."""
        self.metadata[key] = value
        return self
