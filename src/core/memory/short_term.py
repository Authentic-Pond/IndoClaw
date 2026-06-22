"""
Short-term memory management for IndoClaw.
Manages conversation history and recent interactions.
"""

from typing import List, Dict, Any
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """Manages short-term memory (conversation history)."""
    
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.messages: deque = deque(maxlen=capacity)
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to short-term memory."""
        message = Message(
            role=role,
            content=content,
            timestamp=kwargs.get('timestamp', 0),
            metadata=kwargs.get('metadata', {})
        )
        self.messages.append(message)
    
    def get_recent_messages(self, n: int = None) -> List[Message]:
        """Get the most recent messages."""
        if n is None:
            return list(self.messages)
        return list(self.messages)[-n:]
    
    def get_context(self, n: int = 5) -> List[Dict[str, str]]:
        """Get conversation context as list of dicts for API calls."""
        messages = self.get_recent_messages(n)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    def clear(self) -> None:
        """Clear all short-term memory."""
        self.messages.clear()
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __iter__(self):
        return iter(self.messages)