"""
Tests for memory versioning (Task 6.3.2).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.memory.versioning import (
    MemoryVersion,
    MemoryHistory,
    MemoryVersioning,
)


class TestMemoryVersion:
    """Tests for MemoryVersion dataclass."""

    def test_version_creation(self):
        """Test MemoryVersion creation."""
        version = MemoryVersion(
            version_id="version-1",
            memory_id="memory-1",
            content="Test content",
            metadata={"key": "value"},
            timestamp=1234567890.0,
            version_number=1,
        )

        assert version.version_id == "version-1"
        assert version.memory_id == "memory-1"
        assert version.content == "Test content"
        assert version.version_number == 1
        assert version.is_current is True

    def test_version_default_metadata(self):
        """Test MemoryVersion default metadata."""
        version = MemoryVersion(
            version_id="version-2",
            memory_id="memory-1",
            content="Test",
            timestamp=1234567890.0,
            version_number=1,
        )

        assert version.metadata == {}

    def test_version_to_dict(self):
        """Test MemoryVersion to dictionary conversion."""
        version = MemoryVersion(
            version_id="version-3",
            memory_id="memory-1",
            content="Content",
            timestamp=1234567890.0,
            version_number=1,
            version_notes="Initial version",
        )

        data = version.to_dict()

        assert data["version_id"] == "version-3"
        assert data["version_notes"] == "Initial version"

    def test_version_from_dict(self):
        """Test MemoryVersion from dictionary."""
        data = {
            "version_id": "version-4",
            "memory_id": "memory-1",
            "content": "Content",
            "timestamp": 1234567890.0,
            "version_number": 1,
            "version_notes": "Test",
        }

        version = MemoryVersion.from_dict(data)

        assert version.version_id == "version-4"
        assert version.version_notes == "Test"

    def test_created_at_property(self):
        """Test created_at property returns datetime."""
        import datetime
        version = MemoryVersion(
            version_id="version-5",
            memory_id="memory-1",
            content="Content",
            timestamp=1234567890.0,
            version_number=1,
        )

        created = version.created_at
        assert isinstance(created, datetime.datetime)
        assert created.year == 2009


class TestMemoryHistory:
    """Tests for MemoryHistory dataclass."""

    def test_history_creation(self):
        """Test MemoryHistory creation."""
        version = MemoryVersion(
            version_id="v1",
            memory_id="m1",
            content="Content",
            timestamp=1234567890.0,
            version_number=1,
        )
        history = MemoryHistory(
            memory_id="m1",
            current_version=version,
            versions=[],
        )

        assert history.memory_id == "m1"
        assert history.current_version == version

    def test_get_version(self):
        """Test getting a version by number."""
        v1 = MemoryVersion(
            version_id="v1",
            memory_id="m1",
            content="v1 content",
            timestamp=1234567890.0,
            version_number=1,
        )
        v2 = MemoryVersion(
            version_id="v2",
            memory_id="m1",
            content="v2 content",
            timestamp=1234567891.0,
            version_number=2,
        )
        history = MemoryHistory(
            memory_id="m1",
            current_version=v2,
            versions=[v1],
        )

        assert history.get_version(1) == v1
        assert history.get_version(2) == v2
        assert history.get_version(99) is None

    def test_get_previous_version(self):
        """Test getting the previous version."""
        v1 = MemoryVersion(
            version_id="v1",
            memory_id="m1",
            content="v1 content",
            timestamp=1234567890.0,
            version_number=1,
        )
        v2 = MemoryVersion(
            version_id="v2",
            memory_id="m1",
            content="v2 content",
            timestamp=1234567891.0,
            version_number=2,
        )
        history = MemoryHistory(
            memory_id="m1",
            current_version=v2,
            versions=[v1],
        )

        prev = history.get_previous_version()
        assert prev == v1

    def test_get_previous_version_at_first(self):
        """Test getting previous version when at first version."""
        v1 = MemoryVersion(
            version_id="v1",
            memory_id="m1",
            content="v1 content",
            timestamp=1234567890.0,
            version_number=1,
        )
        history = MemoryHistory(
            memory_id="m1",
            current_version=v1,
            versions=[],
        )

        prev = history.get_previous_version()
        assert prev is None


class TestMemoryVersioning:
    """Tests for MemoryVersioning class."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up a temporary directory for testing."""
        self.db_path = str(tmp_path / "test_versions")
        yield

    def test_create_first_version(self):
        """Test creating the first version of a memory."""
        versioning = MemoryVersioning(db_path=self.db_path)

        version = versioning.create_version(
            memory_id="memory-1",
            content="Initial content",
        )

        assert version.version_number == 1
        assert version.is_current is True

    def test_create_multiple_versions(self):
        """Test creating multiple versions of a memory."""
        versioning = MemoryVersioning(db_path=self.db_path)

        v1 = versioning.create_version(
            memory_id="memory-1",
            content="Version 1",
        )
        v2 = versioning.create_version(
            memory_id="memory-1",
            content="Version 2",
        )

        assert v2.version_number == 2
        assert v1.is_current is False
        assert v2.is_current is True

    def test_get_current_version(self):
        """Test getting the current version."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="Initial",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="Updated",
        )

        current = versioning.get_version("memory-1")
        assert current is not None
        assert current.content == "Updated"
        assert current.version_number == 2

    def test_get_specific_version(self):
        """Test getting a specific version by number."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="Version 1",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="Version 2",
        )

        v1 = versioning.get_version("memory-1", version_number=1)
        # The get_version method should check both current and versions list
        # But version 1 is now the current version after version 2 is created
        assert v1 is not None
        assert v1.content == "Version 1"
        assert v1.version_number == 1

    def test_get_history(self):
        """Test getting the full history."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="V1",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="V2",
        )

        history = versioning.get_history("memory-1")
        assert history is not None
        assert len(history.versions) >= 1

    def test_rollback_to_version(self):
        """Test rolling back to a previous version."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="Original",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="Modified",
        )

        new_version = versioning.rollback_to_version("memory-1", 1)

        assert new_version.version_number == 3
        assert new_version.content == "Original"
        assert "Rolled back to version 1" in new_version.version_notes

    def test_rollback_to_nonexistent_version(self):
        """Test rolling back to a non-existent version."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="V1",
        )

        result = versioning.rollback_to_version("memory-1", 99)
        assert result is None

    def test_delete_version(self):
        """Test deleting a version."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="V1",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="V2",
        )

        # Cannot delete current version
        result = versioning.delete_version("memory-1", 2)
        assert result is False

        # Can delete previous version
        result = versioning.delete_version("memory-1", 1)
        assert result is True

    def test_count_versions(self):
        """Test counting versions."""
        versioning = MemoryVersioning(db_path=self.db_path)

        versioning.create_version(
            memory_id="memory-1",
            content="V1",
        )
        versioning.create_version(
            memory_id="memory-1",
            content="V2",
        )

        assert versioning.count_versions("memory-1") == 2

    def test_version_with_metadata(self):
        """Test creating a version with metadata."""
        versioning = MemoryVersioning(db_path=self.db_path)

        version = versioning.create_version(
            memory_id="memory-1",
            content="Content",
            metadata={"key": "value", "category": "test"},
            version_notes="Test version",
            edited_by="agent-1",
        )

        assert version.metadata["key"] == "value"
        assert version.version_notes == "Test version"
        assert version.edited_by == "agent-1"

    def test_nonexistent_memory(self):
        """Test operations on non-existent memory."""
        versioning = MemoryVersioning(db_path=self.db_path)

        assert versioning.get_version("nonexistent") is None
        assert versioning.get_history("nonexistent") is None
        assert versioning.rollback_to_version("nonexistent", 1) is None
        assert versioning.count_versions("nonexistent") == 0
