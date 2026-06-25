"""
Memory provider interfaces for IndoClaw.
Provides a standardized abstraction for different memory implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MemoryEntry:
    """Represents a memory entry in storage."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    relevance_score: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMemoryProvider(ABC):
    """
    Abstract base class for memory providers.
    Defines the standard interface for all memory implementations.
    """

    @abstractmethod
    def add(self, content: str, metadata: Dict[str, Any] = None, embedding: List[float] = None) -> str:
        """
        Add a memory entry to storage.

        Args:
            content: The text content to store
            metadata: Optional metadata dictionary
            embedding: Optional vector embedding for semantic search

        Returns:
            The unique ID of the stored memory
        """
        pass

    @abstractmethod
    def query(self, query_text: str, top_k: int = 5) -> List[MemoryEntry]:
        """
        Query memories by semantic similarity.

        Args:
            query_text: The query text
            top_k: Number of results to return

        Returns:
            List of matching MemoryEntry objects, sorted by relevance
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memories from storage."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored memories."""
        pass

    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The unique ID of the memory

        Returns:
            MemoryEntry if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory by ID.

        Args:
            memory_id: The unique ID of the memory

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def get_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[MemoryEntry]:
        """
        Query memories by metadata filters.

        Args:
            metadata_filter: Dictionary of metadata key-value pairs to match

        Returns:
            List of matching MemoryEntry objects
        """
        pass
