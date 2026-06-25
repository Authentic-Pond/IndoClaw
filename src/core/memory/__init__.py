"""
Memory module for IndoClaw AI Agent OS.
"""

from .short_term import ShortTermMemory, Message
from .long_term import LongTermMemory, MemoryEntry, long_term_memory
from .episode import Episode, EpisodeSummary
from .episode_provider import EpisodeMemory
from .deduplication import (
    MemoryDeduplicator,
    compute_content_hash,
    compute_fingerprint,
    content_similarity,
    deduplicate_memories,
    find_duplicates,
    DuplicateCandidate,
)
from .versioning import (
    MemoryVersion,
    MemoryHistory,
    MemoryVersioning,
)

__all__ = [
    "ShortTermMemory",
    "Message",
    "LongTermMemory",
    "MemoryEntry",
    "long_term_memory",
    "Episode",
    "EpisodeSummary",
    "EpisodeMemory",
    "MemoryDeduplicator",
    "compute_content_hash",
    "compute_fingerprint",
    "content_similarity",
    "deduplicate_memories",
    "find_duplicates",
    "DuplicateCandidate",
    "MemoryVersion",
    "MemoryHistory",
    "MemoryVersioning",
]