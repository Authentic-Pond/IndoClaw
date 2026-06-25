"""
Episodic memory management for IndoClaw.
Provides data structures for representing and storing events.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Episode:
    """
    Represents an episode (event) in episodic memory.

    Episodes are distinct events or experiences that an agent has encountered.
    They are linked to semantic memories for pattern recognition and learning.
    """

    id: str
    title: str
    content: str
    timestamp: float  # Unix timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Links to related semantic memories
    linked_semantic_ids: List[str] = field(default_factory=list)

    # Episode context
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    environment_state: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure metadata and linked_ids are initialized."""
        if self.metadata is None:
            self.metadata = {}
        if self.linked_semantic_ids is None:
            self.linked_semantic_ids = []
        if self.environment_state is None:
            self.environment_state = {}

    @property
    def created_at(self) -> datetime:
        """Get the timestamp as a datetime object."""
        return datetime.fromtimestamp(self.timestamp)

    @property
    def duration(self) -> Optional[float]:
        """
        Get the duration of the episode if end_timestamp is present.
        Returns None if only a single timestamp exists.
        """
        if hasattr(self, 'end_timestamp') and self.end_timestamp:
            return self.end_timestamp - self.timestamp
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert episode to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "linked_semantic_ids": self.linked_semantic_ids,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "environment_state": self.environment_state,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create an Episode from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {}),
            linked_semantic_ids=data.get("linked_semantic_ids", []),
            agent_id=data.get("agent_id"),
            task_id=data.get("task_id"),
            environment_state=data.get("environment_state", {}),
        )

    def link_to_semantic(self, semantic_id: str) -> None:
        """Link this episode to a semantic memory."""
        if semantic_id not in self.linked_semantic_ids:
            self.linked_semantic_ids.append(semantic_id)

    def unlink_from_semantic(self, semantic_id: str) -> None:
        """Remove a link to a semantic memory."""
        if semantic_id in self.linked_semantic_ids:
            self.linked_semantic_ids.remove(semantic_id)


@dataclass
class EpisodeSummary:
    """
    A summary of an episode for quick retrieval and comparison.
    """

    id: str
    title: str
    timestamp: float
    key_insights: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp,
            "key_insights": self.key_insights,
            "entities": self.entities,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
        }
