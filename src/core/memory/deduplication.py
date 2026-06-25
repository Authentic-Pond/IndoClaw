"""
Memory deduplication utilities for IndoClaw.
Provides functions to detect and handle duplicate memories.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import hashlib
import difflib


@dataclass
class DuplicateCandidate:
    """Represents a potential duplicate memory."""
    memory_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


def compute_content_hash(content: str) -> str:
    """
    Compute a hash of the content for quick duplicate detection.

    Args:
        content: The content to hash

    Returns:
        SHA256 hash of the content
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compute_fingerprint(content: str) -> str:
    """
    Compute a normalized fingerprint of content for similarity comparison.
    Removes extra whitespace and normalizes case for comparison.

    Args:
        content: The content to fingerprint

    Returns:
        Normalized fingerprint string
    """
    # Normalize whitespace and lowercase
    normalized = ' '.join(content.lower().split())
    return normalized


def content_similarity(content1: str, content2: str) -> float:
    """
    Compute similarity score between two content strings.

    Uses sequence matching to determine how similar two strings are.

    Args:
        content1: First content string
        content2: Second content string

    Returns:
        Similarity score in range [0, 1]
    """
    if not content1 or not content2:
        return 0.0

    if content1 == content2:
        return 1.0

    # Use difflib for sequence matching
    seq_match = difflib.SequenceMatcher(None, content1, content2)
    return seq_match.ratio()


def deduplicate_memories(
    memories: List[Any],
    content_attr: str = 'content',
    id_attr: str = 'id',
    similarity_threshold: float = 0.9
) -> List[Any]:
    """
    Remove duplicate memories from a list based on content similarity.

    Args:
        memories: List of memory objects to deduplicate
        content_attr: Attribute name containing the content
        id_attr: Attribute name containing the unique ID
        similarity_threshold: Similarity score threshold for considering duplicates
                             (1.0 = exact match, lower = more lenient)

    Returns:
        List of unique memory objects
    """
    if not memories:
        return []

    seen_hashes: Set[str] = set()
    unique_memories: List[Any] = []
    duplicates: List[DuplicateCandidate] = []

    for memory in memories:
        content = getattr(memory, content_attr, '')
        memory_id = getattr(memory, id_attr, str(id(memory)))

        # Compute hash for exact matching
        content_hash = compute_content_hash(content)

        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_memories.append(memory)
        else:
            # Check for near-duplicates with similarity
            for existing in unique_memories:
                existing_content = getattr(existing, content_attr, '')
                similarity = content_similarity(content, existing_content)

                if similarity >= similarity_threshold:
                    duplicates.append(DuplicateCandidate(
                        memory_id=memory_id,
                        content=content,
                        similarity_score=similarity,
                        metadata={}
                    ))
                    break
            else:
                # No similar memory found, add as unique
                unique_memories.append(memory)

    return unique_memories


def find_duplicates(
    memories: List[Any],
    content_attr: str = 'content',
    id_attr: str = 'id',
    similarity_threshold: float = 0.9
) -> List[DuplicateCandidate]:
    """
    Find all duplicate pairs in a list of memories.

    Args:
        memories: List of memory objects to check
        content_attr: Attribute name containing the content
        id_attr: Attribute name containing the unique ID
        similarity_threshold: Similarity score threshold

    Returns:
        List of DuplicateCandidate objects representing duplicates
    """
    duplicates: List[DuplicateCandidate] = []
    n = len(memories)

    for i in range(n):
        memory1 = memories[i]
        content1 = getattr(memory1, content_attr, '')

        for j in range(i + 1, n):
            memory2 = memories[j]
            content2 = getattr(memory2, content_attr, '')

            similarity = content_similarity(content1, content2)

            if similarity >= similarity_threshold:
                duplicates.append(DuplicateCandidate(
                    memory_id=getattr(memory2, id_attr, str(id(memory2))),
                    content=content2,
                    similarity_score=similarity,
                    metadata={}
                ))

    return duplicates


class MemoryDeduplicator:
    """
    Utility class for managing memory deduplication.
    Tracks known memories and prevents duplicates from being added.
    """

    def __init__(self, similarity_threshold: float = 0.9):
        """
        Initialize the deduplicator.

        Args:
            similarity_threshold: Similarity threshold for duplicate detection
        """
        self.similarity_threshold = similarity_threshold
        self.known_hashes: Set[str] = set()
        self.known_fingerprints: Set[str] = set()
        self.known_memories: Dict[str, Any] = {}  # id -> memory mapping

    def is_duplicate(self, content: str) -> bool:
        """
        Check if content is a duplicate.

        Args:
            content: The content to check

        Returns:
            True if content is a duplicate, False otherwise
        """
        content_hash = compute_content_hash(content)

        if content_hash in self.known_hashes:
            return True

        fingerprint = compute_fingerprint(content)

        if fingerprint in self.known_fingerprints:
            return True

        return False

    def add_memory(self, content: str, memory_id: str) -> bool:
        """
        Add a memory and check if it was a duplicate.

        Args:
            content: The memory content
            memory_id: The unique ID for this memory

        Returns:
            True if added (not duplicate), False if duplicate
        """
        content_hash = compute_content_hash(content)

        if content_hash in self.known_hashes:
            return False

        fingerprint = compute_fingerprint(content)
        self.known_hashes.add(content_hash)
        self.known_fingerprints.add(fingerprint)
        self.known_memories[memory_id] = content

        return True

    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove a memory from the deduplicator tracking.

        Args:
            memory_id: The ID of the memory to remove

        Returns:
            True if removed, False if not found
        """
        if memory_id in self.known_memories:
            content = self.known_memories.pop(memory_id)
            content_hash = compute_content_hash(content)
            fingerprint = compute_fingerprint(content)
            self.known_hashes.discard(content_hash)
            self.known_fingerprints.discard(fingerprint)
            return True

        return False

    def clear(self) -> None:
        """Clear all tracked memories."""
        self.known_hashes.clear()
        self.known_fingerprints.clear()
        self.known_memories.clear()
