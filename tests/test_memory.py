"""
Tests for memory providers (Phase 4).
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.memory.provider import BaseMemoryProvider, MemoryEntry
from src.core.memory.long_term import LongTermMemory


class TestBaseMemoryProvider:
    """Tests for BaseMemoryProvider interface."""

    def test_memory_entry_dataclass(self):
        """Test MemoryEntry dataclass."""
        entry = MemoryEntry(
            id="test-id",
            content="Test content",
            metadata={"key": "value"},
        )

        assert entry.id == "test-id"
        assert entry.content == "Test content"
        assert entry.metadata["key"] == "value"
        assert entry.relevance_score == 0.0

    def test_memory_entry_default_metadata(self):
        """Test MemoryEntry default metadata."""
        entry = MemoryEntry(
            id="test-id",
            content="Test content",
        )

        assert entry.metadata == {}


class TestLongTermMemory:
    """Tests for LongTermMemory implementation."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up a temporary directory for testing."""
        self.db_path = str(tmp_path / "test_chroma")
        yield
        # Cleanup is automatic with tmp_path

    def test_initialization(self):
        """Test memory initialization."""
        memory = LongTermMemory(db_path=self.db_path)

        assert memory.db_path == self.db_path
        assert memory.top_k == 5
        assert memory.count() == 0

    def test_add_memory(self):
        """Test adding a memory entry."""
        memory = LongTermMemory(db_path=self.db_path)

        memory_id = memory.add("Test content", {"tag": "test"})

        assert memory_id is not None
        assert len(memory_id) > 0
        assert memory.count() == 1

    def test_add_memory_with_embedding(self):
        """Test adding a memory with embedding."""
        memory = LongTermMemory(db_path=self.db_path)

        embedding = [0.1, 0.2, 0.3]
        memory_id = memory.add("Test content", embedding=embedding)

        assert memory_id is not None
        assert memory.count() == 1

    def test_query_memories(self):
        """Test querying memories."""
        memory = LongTermMemory(db_path=self.db_path)

        # Add some memories
        memory.add("Python programming language")
        memory.add("Java programming language")
        memory.add("Machine learning concepts")

        # Query should return relevant results
        results = memory.query("Python programming", top_k=2)

        assert len(results) <= 2
        assert len(results) > 0
        assert isinstance(results[0], MemoryEntry)

    def test_get_memory_by_id(self):
        """Test retrieving a specific memory by ID."""
        memory = LongTermMemory(db_path=self.db_path)

        memory_id = memory.add("Test content")
        entry = memory.get(memory_id)

        assert entry is not None
        assert entry.id == memory_id
        assert entry.content == "Test content"

    def test_get_memory_not_found(self):
        """Test getting a non-existent memory."""
        memory = LongTermMemory(db_path=self.db_path)

        entry = memory.get("non-existent-id")
        assert entry is None

    def test_delete_memory(self):
        """Test deleting a memory."""
        memory = LongTermMemory(db_path=self.db_path)

        memory_id = memory.add("Test content")
        assert memory.count() == 1

        result = memory.delete(memory_id)
        assert result is True
        assert memory.count() == 0

    def test_delete_nonexistent_memory(self):
        """Test deleting a non-existent memory."""
        memory = LongTermMemory(db_path=self.db_path)

        result = memory.delete("non-existent-id")
        assert result is False

    def test_clear_memories(self):
        """Test clearing all memories."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Content 1")
        memory.add("Content 2")
        assert memory.count() == 2

        memory.clear()
        assert memory.count() == 0

    def test_get_by_metadata(self):
        """Test querying memories by metadata."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Content 1", {"category": "tech"})
        memory.add("Content 2", {"category": "tech"})
        memory.add("Content 3", {"category": "science"})

        results = memory.get_by_metadata({"category": "tech"})
        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
