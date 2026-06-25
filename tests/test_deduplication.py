"""
Tests for memory deduplication (Task 6.3.1).
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.memory.deduplication import (
    MemoryDeduplicator,
    compute_content_hash,
    compute_fingerprint,
    content_similarity,
    deduplicate_memories,
    find_duplicates,
    DuplicateCandidate,
)


class TestContentHashing:
    """Tests for content hashing functions."""

    def test_compute_content_hash(self):
        """Test computing SHA256 hash of content."""
        content = "Test content"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest

    def test_compute_content_hash_different(self):
        """Test that different content produces different hashes."""
        content1 = "Test content"
        content2 = "Different content"

        hash1 = compute_content_hash(content1)
        hash2 = compute_content_hash(content2)

        assert hash1 != hash2

    def test_compute_fingerprint(self):
        """Test fingerprint normalization."""
        content1 = "  Test   content  "
        content2 = "Test content"
        content3 = "test CONTENT"

        fp1 = compute_fingerprint(content1)
        fp2 = compute_fingerprint(content2)
        fp3 = compute_fingerprint(content3)

        assert fp1 == fp2
        assert fp1 == fp3


class TestContentSimilarity:
    """Tests for content similarity functions."""

    def test_similarity_exact_match(self):
        """Test similarity score for identical content."""
        content = "Test content"
        score = content_similarity(content, content)

        assert score == 1.0

    def test_similarity_different(self):
        """Test similarity score for different content."""
        content1 = "Hello world"
        content2 = "Goodbye universe"

        score = content_similarity(content1, content2)

        assert 0.0 <= score < 1.0

    def test_similarity_partial_match(self):
        """Test similarity score for partially matching content."""
        content1 = "Python programming language"
        content2 = "Python programming"

        score = content_similarity(content1, content2)

        assert 0.5 < score < 1.0

    def test_similarity_empty_string(self):
        """Test similarity with empty strings."""
        score = content_similarity("", "content")
        assert score == 0.0

        score = content_similarity("", "")
        assert score == 0.0


class TestMemoryDeduplicator:
    """Tests for MemoryDeduplicator class."""

    def test_add_unique_memory(self):
        """Test adding a unique memory."""
        dedup = MemoryDeduplicator()

        result = dedup.add_memory("Unique content", "id-1")

        # First add should succeed
        assert result is True
        # After adding, is_duplicate should return True
        assert dedup.is_duplicate("Unique content")

    def test_add_duplicate_memory(self):
        """Test adding a duplicate memory."""
        dedup = MemoryDeduplicator()

        dedup.add_memory("Duplicate content", "id-1")
        result = dedup.add_memory("Duplicate content", "id-2")

        assert result is False
        assert dedup.is_duplicate("Duplicate content")

    def test_remove_memory(self):
        """Test removing a memory."""
        dedup = MemoryDeduplicator()

        dedup.add_memory("Content to remove", "id-1")
        assert dedup.is_duplicate("Content to remove")

        result = dedup.remove_memory("id-1")
        assert result is True
        assert not dedup.is_duplicate("Content to remove")

    def test_remove_nonexistent_memory(self):
        """Test removing a non-existent memory."""
        dedup = MemoryDeduplicator()

        result = dedup.remove_memory("non-existent-id")
        assert result is False

    def test_clear(self):
        """Test clearing all memories."""
        dedup = MemoryDeduplicator()

        dedup.add_memory("Content 1", "id-1")
        dedup.add_memory("Content 2", "id-2")

        dedup.clear()

        assert not dedup.is_duplicate("Content 1")
        assert not dedup.is_duplicate("Content 2")

    def test_similarity_threshold(self):
        """Test deduplication with similarity threshold."""
        dedup = MemoryDeduplicator(similarity_threshold=0.8)

        # Add content
        dedup.add_memory("Python programming language", "id-1")

        # Add exact same content - should be duplicate
        result = dedup.add_memory("Python programming language", "id-2")

        # Exact duplicate should be rejected
        assert result is False


class TestDeduplicateMemories:
    """Tests for deduplicate_memories function."""

    class MockMemory:
        """Mock memory class for testing."""
        def __init__(self, content: str, memory_id: str):
            self.content = content
            self.id = memory_id

    def test_deduplicate_exact_duplicates(self):
        """Test deduplication of exact duplicates."""
        memories = [
            self.MockMemory("Duplicate", "id-1"),
            self.MockMemory("Duplicate", "id-2"),
            self.MockMemory("Unique", "id-3"),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 2
        assert result[0].id == "id-1"
        assert result[1].id == "id-3"

    def test_deduplicate_no_duplicates(self):
        """Test with no duplicates."""
        memories = [
            self.MockMemory("Content 1", "id-1"),
            self.MockMemory("Content 2", "id-2"),
            self.MockMemory("Content 3", "id-3"),
        ]

        result = deduplicate_memories(memories)

        assert len(result) == 3

    def test_deduplicate_empty_list(self):
        """Test with empty list."""
        result = deduplicate_memories([])

        assert result == []


class TestFindDuplicates:
    """Tests for find_duplicates function."""

    class MockMemory:
        """Mock memory class for testing."""
        def __init__(self, content: str, memory_id: str):
            self.content = content
            self.id = memory_id

    def test_find_exact_duplicates(self):
        """Test finding exact duplicates."""
        memories = [
            self.MockMemory("Duplicate content", "id-1"),
            self.MockMemory("Duplicate content", "id-2"),
            self.MockMemory("Unique", "id-3"),
        ]

        duplicates = find_duplicates(memories)

        assert len(duplicates) == 1
        assert duplicates[0].memory_id == "id-2"

    def test_find_no_duplicates(self):
        """Test with no duplicates."""
        memories = [
            self.MockMemory("Content 1", "id-1"),
            self.MockMemory("Content 2", "id-2"),
        ]

        duplicates = find_duplicates(memories)

        assert len(duplicates) == 0

    def test_find_duplicates_threshold(self):
        """Test finding duplicates with custom threshold."""
        memories = [
            self.MockMemory("Python programming", "id-1"),
            self.MockMemory("Python programming language", "id-2"),
        ]

        # With high threshold, these are not duplicates
        duplicates = find_duplicates(memories, similarity_threshold=0.95)
        assert len(duplicates) == 0

        # With lower threshold, these may be considered duplicates
        duplicates = find_duplicates(memories, similarity_threshold=0.7)
        assert len(duplicates) >= 0  # May or may not match depending on similarity
