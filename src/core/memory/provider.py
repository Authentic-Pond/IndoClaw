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
    created_at: Optional[float] = None  # Unix timestamp
    last_updated: Optional[float] = None  # Unix timestamp

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
    def query(self, query_text: str, top_k: int = 5, metadata_filter: Dict[str, Any] = None,
              sort_by_relevance: bool = True, sort_by_freshness: bool = False) -> List[MemoryEntry]:
        """
        Query memories by semantic similarity.

        Args:
            query_text: The query text
            top_k: Number of results to return
            metadata_filter: Optional dictionary of metadata key-value pairs to filter by
            sort_by_relevance: Sort results by relevance score (descending)
            sort_by_freshness: Sort results by creation time (newest first)

        Returns:
            List of matching MemoryEntry objects, sorted by relevance or freshness
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

    def normalize_relevance_scores(self, entries: List[MemoryEntry]) -> List[MemoryEntry]:
        """
        Normalize relevance scores to [0, 1] range.

        Args:
            entries: List of MemoryEntry objects with relevance scores

        Returns:
            List of MemoryEntry objects with normalized scores
        """
        if not entries:
            return entries

        scores = [e.relevance_score for e in entries]
        min_score, max_score = min(scores), max(scores)

        if max_score - min_score == 0:
            # All scores are the same
            for entry in entries:
                entry.relevance_score = 1.0
        else:
            for entry in entries:
                entry.relevance_score = (entry.relevance_score - min_score) / (max_score - min_score)

        return entries
