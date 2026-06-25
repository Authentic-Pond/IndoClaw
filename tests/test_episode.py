"""
Tests for episode memory (Phase 6.2).
"""

import pytest
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.core.memory.episode import Episode, EpisodeSummary
from src.core.memory.episode_provider import EpisodeMemory


class TestEpisode:
    """Tests for Episode dataclass."""

    def test_episode_creation(self):
        """Test Episode creation with all fields."""
        episode = Episode(
            id="test-episode-1",
            title="Test Episode",
            content="Test content",
            timestamp=time.time(),
            metadata={"test": "value"}
        )

        assert episode.id == "test-episode-1"
        assert episode.title == "Test Episode"
        assert episode.content == "Test content"
        assert episode.metadata["test"] == "value"

    def test_episode_default_metadata(self):
        """Test Episode default metadata initialization."""
        episode = Episode(
            id="test-episode-2",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        assert episode.metadata == {}
        assert episode.linked_semantic_ids == []

    def test_episode_to_dict(self):
        """Test Episode to dictionary conversion."""
        episode = Episode(
            id="test-episode-3",
            title="Test",
            content="Content",
            timestamp=time.time(),
            agent_id="agent-1"
        )

        data = episode.to_dict()

        assert data["id"] == "test-episode-3"
        assert data["agent_id"] == "agent-1"

    def test_episode_from_dict(self):
        """Test Episode creation from dictionary."""
        data = {
            "id": "test-episode-4",
            "title": "Test",
            "content": "Content",
            "timestamp": time.time(),
            "agent_id": "agent-1"
        }

        episode = Episode.from_dict(data)

        assert episode.id == "test-episode-4"
        assert episode.agent_id == "agent-1"

    def test_episode_link_to_semantic(self):
        """Test linking episode to semantic memory."""
        episode = Episode(
            id="test-episode-5",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        episode.link_to_semantic("semantic-1")
        assert "semantic-1" in episode.linked_semantic_ids

    def test_episode_unlink_from_semantic(self):
        """Test unlinking episode from semantic memory."""
        episode = Episode(
            id="test-episode-6",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        episode.link_to_semantic("semantic-1")
        episode.unlink_from_semantic("semantic-1")

        assert "semantic-1" not in episode.linked_semantic_ids


class TestEpisodeSummary:
    """Tests for EpisodeSummary dataclass."""

    def test_summary_creation(self):
        """Test EpisodeSummary creation."""
        summary = EpisodeSummary(
            id="test-summary-1",
            title="Test Summary",
            timestamp=time.time(),
            key_insights=["Insight 1"],
            entities=["Entity 1"],
            sentiment="positive",
            confidence=0.9
        )

        assert summary.id == "test-summary-1"
        assert summary.key_insights == ["Insight 1"]
        assert summary.sentiment == "positive"
        assert summary.confidence == 0.9

    def test_summary_to_dict(self):
        """Test EpisodeSummary to dictionary conversion."""
        summary = EpisodeSummary(
            id="test-summary-2",
            title="Test",
            timestamp=time.time()
        )

        data = summary.to_dict()

        assert data["id"] == "test-summary-2"
        assert data["key_insights"] == []


class TestEpisodeMemory:
    """Tests for EpisodeMemory implementation."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up a temporary directory for testing."""
        self.db_path = str(tmp_path / "test_episodes")
        yield
        # Cleanup is automatic with tmp_path

    def test_initialization(self):
        """Test episode memory initialization."""
        memory = EpisodeMemory(db_path=self.db_path)

        assert memory.db_path == self.db_path
        assert memory.count() == 0

    def test_add_episode(self):
        """Test adding an episode."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode = Episode(
            id="test-episode-1",
            title="Test Episode",
            content="Test content",
            timestamp=time.time()
        )

        memory.add(episode)
        assert memory.count() == 1

    def test_get_episode(self):
        """Test retrieving an episode by ID."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode = Episode(
            id="test-episode-2",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        memory.add(episode)
        retrieved = memory.get("test-episode-2")

        assert retrieved is not None
        assert retrieved.id == "test-episode-2"

    def test_get_nonexistent_episode(self):
        """Test getting a non-existent episode."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode = memory.get("non-existent-id")
        assert episode is None

    def test_query_episodes(self):
        """Test querying episodes by text."""
        memory = EpisodeMemory(db_path=self.db_path)

        memory.add(Episode(
            id="episode-1",
            title="Python programming",
            content="Python is a versatile programming language",
            timestamp=time.time()
        ))
        memory.add(Episode(
            id="episode-2",
            title="Java programming",
            content="Java is an object-oriented language",
            timestamp=time.time()
        ))

        results = memory.query("Python", top_k=2)
        assert len(results) >= 1

    def test_delete_episode(self):
        """Test deleting an episode."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode = Episode(
            id="test-episode-3",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        memory.add(episode)
        assert memory.count() == 1

        memory.delete("test-episode-3")
        assert memory.count() == 0

    def test_get_by_agent(self):
        """Test getting episodes by agent ID."""
        memory = EpisodeMemory(db_path=self.db_path)

        memory.add(Episode(
            id="episode-1",
            title="Agent 1 Task",
            content="Content",
            timestamp=time.time(),
            agent_id="agent-1"
        ))
        memory.add(Episode(
            id="episode-2",
            title="Agent 2 Task",
            content="Content",
            timestamp=time.time(),
            agent_id="agent-2"
        ))

        agent_1_episodes = memory.get_by_agent("agent-1")
        assert len(agent_1_episodes) == 1
        assert agent_1_episodes[0].id == "episode-1"

    def test_clear_episodes(self):
        """Test clearing all episodes."""
        memory = EpisodeMemory(db_path=self.db_path)

        memory.add(Episode(
            id="episode-1",
            title="Test",
            content="Content",
            timestamp=time.time()
        ))
        memory.add(Episode(
            id="episode-2",
            title="Test",
            content="Content",
            timestamp=time.time()
        ))

        assert memory.count() == 2

        memory.clear()
        assert memory.count() == 0

    def test_link_to_semantic(self):
        """Test linking episode to semantic memory."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode = Episode(
            id="episode-1",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        memory.add(episode)
        result = memory.link_to_semantic("episode-1", "semantic-1")

        assert result is True
        retrieved = memory.get("episode-1")
        assert "semantic-1" in retrieved.linked_semantic_ids

    def test_get_by_semantic(self):
        """Test getting episodes by semantic link."""
        memory = EpisodeMemory(db_path=self.db_path)

        episode1 = Episode(
            id="episode-1",
            title="Test",
            content="Content",
            timestamp=time.time()
        )
        episode2 = Episode(
            id="episode-2",
            title="Test",
            content="Content",
            timestamp=time.time()
        )

        memory.add(episode1)
        memory.add(episode2)

        memory.link_to_semantic("episode-1", "semantic-1")
        memory.link_to_semantic("episode-2", "semantic-1")

        linked_episodes = memory.get_by_semantic("semantic-1")
        assert len(linked_episodes) == 2
