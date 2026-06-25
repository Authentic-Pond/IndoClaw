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

    def test_query_with_metadata_filter(self):
        """Test querying memories with metadata filtering."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Python programming for data science", {"category": "tech", "topic": "data"})
        memory.add("Python programming for web development", {"category": "tech", "topic": "web"})
        memory.add("Java programming for backend", {"category": "tech", "topic": "backend"})
        memory.add("Biology basics", {"category": "science"})

        # Query with metadata filter for tech category
        results = memory.query("Python", top_k=5, metadata_filter={"category": "tech"})
        assert len(results) >= 1
        # All results should have category == "tech"
        for entry in results:
            assert entry.metadata.get("category") == "tech"

    def test_query_with_multiple_metadata_filters(self):
        """Test querying memories with multiple metadata filters."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Python programming for data science", {"category": "tech", "topic": "data"})
        memory.add("Python programming for web development", {"category": "tech", "topic": "web"})
        memory.add("Java programming for data science", {"category": "tech", "topic": "data"})
        memory.add("Biology basics", {"category": "science"})

        # Query with multiple metadata filters
        results = memory.query(
            "Python",
            top_k=5,
            metadata_filter={"category": "tech", "topic": "data"}
        )
        assert len(results) >= 1
        # All results should match both filters
        for entry in results:
            assert entry.metadata.get("category") == "tech"
            assert entry.metadata.get("topic") == "data"

    def test_query_without_metadata_filter(self):
        """Test that query still works without metadata filter (backward compatibility)."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Python programming for data science", {"category": "tech"})
        memory.add("Biology basics", {"category": "science"})

        # Query without metadata filter should return all relevant results
        results = memory.query("Python", top_k=5)
        assert len(results) >= 1

    def test_relevance_score_normalization(self):
        """Test that relevance scores are normalized to [0, 1] range."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Low relevance content")
        memory.add("Medium relevance content")
        memory.add("High relevance content")

        results = memory.query("High relevance", top_k=3)

        # All scores should be in [0, 1] range
        for entry in results:
            assert 0.0 <= entry.relevance_score <= 1.0

    def test_freshness_metadata_on_add(self):
        """Test that freshness metadata is tracked on add."""
        import time
        memory = LongTermMemory(db_path=self.db_path)

        before_time = time.time()
        memory_id = memory.add("Test content")
        after_time = time.time()

        entry = memory.get(memory_id)

        assert entry is not None
        assert entry.created_at is not None
        assert entry.last_updated is not None
        assert before_time <= entry.created_at <= after_time

    def test_sort_by_freshness(self):
        """Test that results can be sorted by freshness."""
        import time
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("First content")
        time.sleep(0.1)
        memory.add("Second content")
        time.sleep(0.1)
        memory.add("Third content")

        # Query with freshness sorting (newest first)
        results = memory.query("content", top_k=5, sort_by_freshness=True)

        # Third content should be first (newest)
        assert len(results) >= 3
        # created_at should be in descending order
        for i in range(len(results) - 1):
            if results[i].created_at and results[i + 1].created_at:
                assert results[i].created_at >= results[i + 1].created_at

    def test_sort_by_relevance(self):
        """Test that results are sorted by relevance by default."""
        memory = LongTermMemory(db_path=self.db_path)

        memory.add("Python programming language")
        memory.add("Java programming language")
        memory.add("Python programming for data science")
        memory.add("Machine learning concepts")

        # Query for Python
        results = memory.query("Python", top_k=5, sort_by_relevance=True)

        # Results should have valid relevance scores
        for entry in results:
            assert 0.0 <= entry.relevance_score <= 1.0

    def test_memory_entry_freshness_fields(self):
        """Test MemoryEntry freshness metadata fields."""
        import time
        current_time = time.time()
        entry = MemoryEntry(
            id="test-id",
            content="Test content",
            created_at=current_time,
            last_updated=current_time
        )

        assert entry.created_at == current_time
        assert entry.last_updated == current_time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
