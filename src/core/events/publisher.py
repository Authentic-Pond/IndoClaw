"""
Event publisher for IndoClaw.
Publishes agent events to configured callbacks (webhooks, files, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
import json
import os


class EventType(Enum):
    """Types of agent events."""
    TASK_START = "task_start"
    TASK_END = "task_end"
    TOOL_EXECUTED = "tool_executed"
    TOOL_APPROVAL_NEEDED = "tool_approval_needed"
    ERROR = "error"
    PLAN_CREATED = "plan_created"
    PLAN_APPROVED = "plan_approved"
    INPUT_REQUESTED = "input_requested"
    INPUT_RECEIVED = "input_received"
    AGENT_THOUGHT = "agent_thought"
    MEMORY_UPDATED = "memory_updated"


@dataclass
class AgentEvent:
    """An event published by the agent system."""
    event_type: EventType
    timestamp: str
    agent_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "payload": self.payload,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class EventCallback(ABC):
    """Base class for event callbacks."""

    @abstractmethod
    def notify(self, event: AgentEvent) -> None:
        """Notify the callback of an event."""
        pass


class WebhookCallback(EventCallback):
    """Event callback that sends events to a webhook URL."""

    def __init__(self, url: str, method: str = "POST", headers: Dict[str, str] = None):
        self.url = url
        self.method = method
        self.headers = headers or {"Content-Type": "application/json"}

    def notify(self, event: AgentEvent) -> None:
        """Send event to webhook."""
        try:
            import requests
            response = requests.request(
                method=self.method,
                url=self.url,
                json=event.to_dict(),
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
        except ImportError:
            # requests not available, log to console
            print(f"[Webhook] Would send to {self.url}: {event.to_json()}")
        except Exception as e:
            print(f"[Webhook] Failed to send event: {e}")


class FileCallback(EventCallback):
    """Event callback that writes events to a file."""

    def __init__(self, filepath: str, append: bool = True):
        self.filepath = filepath
        self.append = append
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure the directory exists."""
        dir_path = os.path.dirname(self.filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def notify(self, event: AgentEvent) -> None:
        """Write event to file."""
        try:
            with open(self.filepath, "a" if self.append else "w") as f:
                f.write(event.to_json() + "\n")
        except Exception as e:
            print(f"[FileCallback] Failed to write event: {e}")


class ConsoleCallback(EventCallback):
    """Event callback that prints events to console."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def notify(self, event: AgentEvent) -> None:
        """Print event to console."""
        if self.verbose:
            print(f"[{event.timestamp}] {event.event_type.value}: {event.agent_id}")
            print(f"  Payload: {json.dumps(event.payload, indent=4)}")
        else:
            print(f"[{event.timestamp}] {event.event_type.value}: {event.agent_id}")


class EventPublisher:
    """Publishes events to registered callbacks."""

    def __init__(self):
        self._callbacks: List[EventCallback] = []
        self._enabled = True
        self._event_history: List[AgentEvent] = []

    def register_callback(self, callback: EventCallback) -> None:
        """Register a callback to receive events."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: EventCallback) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def publish(self, event_type: EventType, agent_id: str, payload: Dict[str, Any] = None, metadata: Dict[str, str] = None) -> None:
        """Publish an event to all registered callbacks."""
        if not self._enabled:
            return

        event = AgentEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            payload=payload or {},
            metadata=metadata or {}
        )

        self._event_history.append(event)
        for callback in self._callbacks:
            try:
                callback.notify(event)
            except Exception as e:
                print(f"[EventPublisher] Callback failed: {e}")

    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False

    def get_history(self, event_type: EventType = None, agent_id: str = None) -> List[AgentEvent]:
        """Get event history, optionally filtered."""
        history = self._event_history
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        if agent_id:
            history = [e for e in history if e.agent_id == agent_id]
        return history

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history = []
