"""
Memory versioning utilities for IndoClaw.
Tracks versions of memories for history and rollback capabilities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import time


@dataclass
class MemoryVersion:
    """
    Represents a version of a memory entry.

    Each version captures the state of a memory at a specific point in time,
    allowing for history tracking and rollback capabilities.
    """

    version_id: str
    memory_id: str
    content: str
    timestamp: float
    version_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_current: bool = True
    version_notes: str = ""
    edited_by: Optional[str] = None  # Could be agent_id or user_id

    def __post_init__(self):
        """Ensure metadata is initialized."""
        if self.metadata is None:
            self.metadata = {}

    @property
    def created_at(self) -> datetime:
        """Get the timestamp as a datetime object."""
        return datetime.fromtimestamp(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary for storage."""
        return {
            "version_id": self.version_id,
            "memory_id": self.memory_id,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "version_number": self.version_number,
            "is_current": self.is_current,
            "version_notes": self.version_notes,
            "edited_by": self.edited_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryVersion":
        """Create a MemoryVersion from a dictionary."""
        return cls(
            version_id=data["version_id"],
            memory_id=data["memory_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=data["timestamp"],
            version_number=data["version_number"],
            is_current=data.get("is_current", True),
            version_notes=data.get("version_notes", ""),
            edited_by=data.get("edited_by"),
        )


@dataclass
class MemoryHistory:
    """Represents the full version history of a memory."""

    memory_id: str
    current_version: MemoryVersion
    versions: List[MemoryVersion] = field(default_factory=list)

    def get_version(self, version_number: int) -> Optional[MemoryVersion]:
        """Get a specific version by number."""
        # Check current version first
        if self.current_version.version_number == version_number:
            return self.current_version
        for v in self.versions:
            if v.version_number == version_number:
                return v
        return None

    def get_version_by_id(self, version_id: str) -> Optional[MemoryVersion]:
        """Get a specific version by ID."""
        for v in self.versions:
            if v.version_id == version_id:
                return v
        return None

    def get_previous_version(self) -> Optional[MemoryVersion]:
        """Get the previous version relative to current."""
        current_num = self.current_version.version_number
        for v in self.versions:
            if v.version_number == current_num - 1:
                return v
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            "memory_id": self.memory_id,
            "current_version": self.current_version.to_dict(),
            "versions": [v.to_dict() for v in self.versions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryHistory":
        """Create a MemoryHistory from a dictionary."""
        current = MemoryVersion.from_dict(data["current_version"])
        versions = [MemoryVersion.from_dict(v) for v in data.get("versions", [])]
        return cls(
            memory_id=data["memory_id"],
            current_version=current,
            versions=versions,
        )


class MemoryVersioning:
    """
    Manages versioning for memory entries.
    Tracks all versions of memories and allows for version switching.
    """

    def __init__(self, db_path: str = "./data/memory_versions"):
        self.db_path = db_path
        self.versions: Dict[str, MemoryHistory] = {}
        self._initialize()

    def _initialize(self) -> None:
        """Initialize versioning storage."""
        import os
        os.makedirs(self.db_path, exist_ok=True)

    def create_version(
        self,
        memory_id: str,
        content: str,
        metadata: Dict[str, Any] = None,
        version_notes: str = "",
        edited_by: str = None,
    ) -> MemoryVersion:
        """
        Create a new version of a memory entry.

        Args:
            memory_id: The ID of the memory being versioned
            content: The new content for this version
            metadata: Optional metadata dictionary
            version_notes: Notes about this version change
            edited_by: ID of who/what made the edit

        Returns:
            The created MemoryVersion
        """
        if memory_id not in self.versions:
            # First version of this memory
            version_num = 1
            versions = []
        else:
            history = self.versions[memory_id]
            version_num = history.current_version.version_number + 1
            versions = history.versions

        # Mark current version as not current
        if memory_id in self.versions:
            self.versions[memory_id].current_version.is_current = False

        # Create new version
        import uuid
        version_id = str(uuid.uuid4())
        new_version = MemoryVersion(
            version_id=version_id,
            memory_id=memory_id,
            content=content,
            metadata=metadata or {},
            timestamp=time.time(),
            version_number=version_num,
            is_current=True,
            version_notes=version_notes,
            edited_by=edited_by,
        )

        # Update history
        if memory_id not in self.versions:
            self.versions[memory_id] = MemoryHistory(
                memory_id=memory_id,
                current_version=new_version,
                versions=[],
            )
        else:
            # Add the previous version to history before updating current
            prev_version = self.versions[memory_id].current_version
            if prev_version is not None:
                self.versions[memory_id].versions.append(prev_version)
            self.versions[memory_id].current_version = new_version

        return new_version

    def get_version(self, memory_id: str, version_number: int = None) -> Optional[MemoryVersion]:
        """
        Get a specific version of a memory.

        Args:
            memory_id: The ID of the memory
            version_number: Version number (None for current)

        Returns:
            MemoryVersion or None if not found
        """
        if memory_id not in self.versions:
            return None

        history = self.versions[memory_id]

        if version_number is None:
            return history.current_version

        # Check current version first (it might be the requested version)
        if history.current_version.version_number == version_number:
            return history.current_version

        # Check versions list
        for v in history.versions:
            if v.version_number == version_number:
                return v

        return None

    def get_history(self, memory_id: str) -> Optional[MemoryHistory]:
        """
        Get the full version history of a memory.

        Args:
            memory_id: The ID of the memory

        Returns:
            MemoryHistory or None if not found
        """
        return self.versions.get(memory_id)

    def get_all_versions(self, memory_id: str) -> List[MemoryVersion]:
        """
        Get all versions of a memory, sorted by version number.

        Args:
            memory_id: The ID of the memory

        Returns:
            List of MemoryVersion objects
        """
        if memory_id not in self.versions:
            return []

        history = self.versions[memory_id]
        return sorted(history.versions + [history.current_version],
                      key=lambda v: v.version_number)

    def rollback_to_version(self, memory_id: str, version_number: int) -> Optional[MemoryVersion]:
        """
        Rollback a memory to a previous version.

        Args:
            memory_id: The ID of the memory
            version_number: The version number to rollback to

        Returns:
            The new current version, or None if not found
        """
        history = self.versions.get(memory_id)
        if not history:
            return None

        version_to_restore = history.get_version(version_number)
        if not version_to_restore:
            return None

        # Create a new version that is a copy of the target version
        return self.create_version(
            memory_id=memory_id,
            content=version_to_restore.content,
            metadata=version_to_restore.metadata.copy(),
            version_notes=f"Rolled back to version {version_number}",
            edited_by="system",
        )

    def delete_version(self, memory_id: str, version_number: int) -> bool:
        """
        Delete a specific version of a memory.

        Args:
            memory_id: The ID of the memory
            version_number: The version number to delete

        Returns:
            True if deleted, False if not found
        """
        history = self.versions.get(memory_id)
        if not history:
            return False

        # Cannot delete the current version
        if history.current_version.version_number == version_number:
            return False

        # Find and remove the version
        original_len = len(history.versions)
        history.versions = [v for v in history.versions
                          if v.version_number != version_number]

        return len(history.versions) != original_len

    def count_versions(self, memory_id: str) -> int:
        """Return the number of versions for a memory."""
        if memory_id not in self.versions:
            return 0
        history = self.versions[memory_id]
        return len(history.versions) + 1  # Include current version
