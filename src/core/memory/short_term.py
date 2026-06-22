"""
Short-term memory management for IndoClaw.
Manages conversation history and recent interactions.
"""

from typing import List, Dict, Any
from collections import deque
from dataclasses import dataclass, field
import os
import json


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """Manages short-term memory (conversation history)."""
    
    def __init__(self, capacity: int = 10, storage_path: str = None):
        self.capacity = capacity
        self.messages: deque = deque(maxlen=capacity)
        self.storage_path = storage_path or "./data/short_term_memory.json"
        # Load saved memory if it exists
        self._load()
    
    def _load(self) -> None:
        """Load memory from disk if available."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.messages = deque(maxlen=self.capacity)
                    for msg_data in data.get("messages", []):
                        msg = Message(
                            role=msg_data.get("role", "user"),
                            content=msg_data.get("content", ""),
                            timestamp=msg_data.get("timestamp", 0),
                            metadata=msg_data.get("metadata", {})
                        )
                        self.messages.append(msg)
            except Exception as e:
                # If loading fails, start fresh
                self.messages = deque(maxlen=self.capacity)
    
    def _save(self) -> None:
        """Save memory to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            data = {
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "metadata": msg.metadata
                    }
                    for msg in self.messages
                ]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass  # Silently fail to avoid disrupting operation
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to short-term memory."""
        message = Message(
            role=role,
            content=content,
            timestamp=kwargs.get('timestamp', 0),
            metadata=kwargs.get('metadata', {})
        )
        self.messages.append(message)
        self._save()  # Persist to disk
    
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
        # Clear saved memory file
        try:
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
        except Exception:
            pass
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __iter__(self):
        return iter(self.messages)