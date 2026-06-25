"""
Episode memory provider for IndoClaw.
Handles storage and retrieval of episodic memories (events).
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import asdict

try:
    from chromadb import Client as ChromaClient
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from .episode import Episode, EpisodeSummary


class EpisodeMemory:
    """
    Manages episodic memory - stored events and experiences.
    Uses ChromaDB for vector search or file-based fallback.
    """

    def __init__(self, db_path: str = "./data/chroma_episodes"):
        self.db_path = db_path
        self.client = None
        self.collection = None
        self.fallback_file = None
        self.fallback_data: Dict[str, Any] = {"episodes": []}
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the episode storage."""
        if not CHROMA_AVAILABLE:
            self._setup_fallback()
            return

        os.makedirs(self.db_path, exist_ok=True)

        try:
            self.client = ChromaClient(
                ChromaSettings(
                    persist_directory=self.db_path,
                    anonymized_telemetry=False
                )
            )
            self.collection = self.client.get_or_create_collection(
                name="indoclaw_episodes",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Chroma episode initialization warning: {e}")
            self._setup_fallback()

    def _setup_fallback(self) -> None:
        """Set up file-based fallback storage."""
        os.makedirs(self.db_path, exist_ok=True)
        self.fallback_file = os.path.join(self.db_path, "fallback_episodes.json")
        if os.path.exists(self.fallback_file):
            with open(self.fallback_file, 'r') as f:
                self.fallback_data = json.load(f)
        else:
            self.fallback_data = {"episodes": []}

    def add(self, episode: Episode) -> str:
        """
        Add an episode to storage.

        Args:
            episode: The Episode object to store

        Returns:
            The unique ID of the stored episode
        """
        if self.client:
            self.collection.add(
                documents=[episode.content],
                metadatas=[episode.to_dict()],
                ids=[episode.id]
            )
            return episode.id
        else:
            # Fallback storage
            entry = asdict(episode)
            self.fallback_data["episodes"].append(entry)
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
            return episode.id

    def query(self, query_text: str, top_k: int = 5) -> List[Episode]:
        """
        Query episodes by semantic similarity.

        Args:
            query_text: The query text
            top_k: Number of results to return

        Returns:
            List of matching Episode objects
        """
        if self.client:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k
            )

            episodes = []
            for i, doc in enumerate(results['documents'][0]):
                data = results['metadatas'][0][i] if results.get('metadatas') else {}
                episodes.append(Episode.from_dict(data))
            return episodes
        else:
            return self._fallback_query(query_text, top_k)

    def _fallback_query(self, query: str, top_k: int) -> List[Episode]:
        """Fallback keyword-based search for episodes."""
        episodes = self.fallback_data.get("episodes", [])
        query_words = set(query.lower().split())

        scored = []
        for ep in episodes:
            content_words = set(ep['content'].lower().split())
            intersection = len(query_words & content_words)
            score = intersection / len(query_words) if query_words else 0
            scored.append((score, ep))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [Episode.from_dict(ep) for score, ep in scored[:top_k]]

    def get(self, episode_id: str) -> Optional[Episode]:
        """
        Retrieve a specific episode by ID.

        Args:
            episode_id: The unique ID of the episode

        Returns:
            Episode if found, None otherwise
        """
        if self.client:
            result = self.collection.get(ids=[episode_id])
            if result and result['ids'] and len(result['ids']) > 0:
                return Episode.from_dict(result['metadatas'][0])
            return None
        else:
            for ep in self.fallback_data.get("episodes", []):
                if ep['id'] == episode_id:
                    return Episode.from_dict(ep)
            return None

    def get_by_agent(self, agent_id: str) -> List[Episode]:
        """
        Get all episodes for a specific agent.

        Args:
            agent_id: The agent identifier

        Returns:
            List of episodes associated with the agent
        """
        if self.client:
            results = self.collection.get(where={"agent_id": agent_id})
            return [Episode.from_dict(m) for m in results['metadatas']]
        else:
            return [
                Episode.from_dict(ep)
                for ep in self.fallback_data.get("episodes", [])
                if ep.get("agent_id") == agent_id
            ]

    def get_by_time_range(
        self, start_timestamp: float, end_timestamp: float
    ) -> List[Episode]:
        """
        Get episodes within a time range.

        Args:
            start_timestamp: Start of time range (Unix timestamp)
            end_timestamp: End of time range (Unix timestamp)

        Returns:
            List of episodes in the time range
        """
        if self.client:
            # ChromaDB supports range queries with metadata
            results = self.collection.get(
                where={
                    "$and": [
                        {"timestamp": {"$gte": start_timestamp}},
                        {"timestamp": {"$lte": end_timestamp}}
                    ]
                }
            )
            return [Episode.from_dict(m) for m in results['metadatas']]
        else:
            return [
                Episode.from_dict(ep)
                for ep in self.fallback_data.get("episodes", [])
                if start_timestamp <= ep.get("timestamp", 0) <= end_timestamp
            ]

    def update(self, episode: Episode) -> bool:
        """
        Update an existing episode.

        Args:
            episode: The Episode object with updated data

        Returns:
            True if updated, False if not found
        """
        # Update timestamp
        episode.metadata["last_updated"] = time.time()

        if self.client:
            existing = self.collection.get(ids=[episode.id])
            if existing and existing['ids']:
                self.collection.update(
                    ids=[episode.id],
                    documents=[episode.content],
                    metadatas=[episode.to_dict()]
                )
                return True
            return False
        else:
            episodes = self.fallback_data.get("episodes", [])
            for i, ep in enumerate(episodes):
                if ep['id'] == episode.id:
                    episodes[i] = asdict(episode)
                    if self.fallback_file:
                        with open(self.fallback_file, 'w') as f:
                            json.dump(self.fallback_data, f, indent=2)
                    return True
            return False

    def delete(self, episode_id: str) -> bool:
        """
        Delete an episode by ID.

        Args:
            episode_id: The unique ID of the episode

        Returns:
            True if deleted, False if not found
        """
        if self.client:
            try:
                self.collection.delete(ids=[episode_id])
                return True
            except Exception:
                return False
        else:
            episodes = self.fallback_data.get("episodes", [])
            original_len = len(episodes)
            self.fallback_data["episodes"] = [ep for ep in episodes if ep['id'] != episode_id]
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
            return original_len != len(self.fallback_data["episodes"])

    def link_to_semantic(self, episode_id: str, semantic_id: str) -> bool:
        """
        Link an episode to a semantic memory.

        Args:
            episode_id: The episode ID
            semantic_id: The semantic memory ID

        Returns:
            True if linked, False if episode not found
        """
        episode = self.get(episode_id)
        if not episode:
            return False

        episode.link_to_semantic(semantic_id)
        return self.update(episode)

    def unlink_from_semantic(self, episode_id: str, semantic_id: str) -> bool:
        """
        Remove a link from an episode to a semantic memory.

        Args:
            episode_id: The episode ID
            semantic_id: The semantic memory ID

        Returns:
            True if unlinked, False if episode not found
        """
        episode = self.get(episode_id)
        if not episode:
            return False

        episode.unlink_from_semantic(semantic_id)
        return self.update(episode)

    def get_by_semantic(self, semantic_id: str) -> List[Episode]:
        """
        Get all episodes linked to a specific semantic memory.

        Args:
            semantic_id: The semantic memory ID

        Returns:
            List of episodes linked to the semantic memory
        """
        if self.client:
            results = self.collection.get(where={"linked_semantic_ids": semantic_id})
            return [Episode.from_dict(m) for m in results['metadatas']]
        else:
            return [
                Episode.from_dict(ep)
                for ep in self.fallback_data.get("episodes", [])
                if semantic_id in ep.get("linked_semantic_ids", [])
            ]

    def clear(self) -> None:
        """Clear all episodes from storage."""
        if self.client:
            self.collection.delete(where={})
        else:
            self.fallback_data = {"episodes": []}
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f)

    def count(self) -> int:
        """Return the number of stored episodes."""
        if self.client:
            return self.collection.count()
        else:
            return len(self.fallback_data.get("episodes", []))

    def get_summary(self, episode_id: str) -> Optional[EpisodeSummary]:
        """
        Get a summary of an episode.

        Args:
            episode_id: The episode ID

        Returns:
            EpisodeSummary if found, None otherwise
        """
        episode = self.get(episode_id)
        if not episode:
            return None

        # Generate summary from episode content
        return EpisodeSummary(
            id=episode.id,
            title=episode.title,
            timestamp=episode.timestamp,
            key_insights=[],  # Could be populated by an LLM in future
            entities=[],  # Could be extracted in future
            confidence=1.0
        )


# Global instance
episode_memory = EpisodeMemory()
