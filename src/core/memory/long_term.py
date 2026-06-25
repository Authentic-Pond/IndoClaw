"""
Long-term memory management for IndoClaw.
Uses vector embeddings for semantic retrieval of past knowledge.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import os
import json
import time

try:
    from chromadb import Client as ChromaClient
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from .provider import BaseMemoryProvider, MemoryEntry


class LongTermMemory(BaseMemoryProvider):
    """Manages long-term memory using vector embeddings (ChromaDB)."""

    def __init__(self, db_path: str = "./data/chroma", top_k: int = 5):
        self.db_path = db_path
        self.top_k = top_k
        self.client = None
        self.collection = None
        self.fallback_file = None
        self.fallback_data = {"memories": []}
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the vector database."""
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
                name="indoclaw_memories",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Chroma initialization warning: {e}")
            self._setup_fallback()

    def _setup_fallback(self) -> None:
        """Set up file-based fallback storage."""
        os.makedirs(self.db_path, exist_ok=True)
        self.fallback_file = os.path.join(self.db_path, "fallback_memories.json")
        if os.path.exists(self.fallback_file):
            with open(self.fallback_file, 'r') as f:
                self.fallback_data = json.load(f)
        else:
            self.fallback_data = {"memories": []}

    def add(self, content: str, metadata: Dict[str, Any] = None, embedding: List[float] = None) -> str:
        """Add a memory entry."""
        import time
        current_time = time.time()

        if self.client:
            import uuid
            memory_id = str(uuid.uuid4())
            # Add freshness metadata
            meta_with_timestamps = (metadata or {}).copy()
            meta_with_timestamps["created_at"] = current_time
            meta_with_timestamps["last_updated"] = current_time
            self.collection.add(
                documents=[content],
                metadatas=[meta_with_timestamps],
                embeddings=[embedding] if embedding else None,
                ids=[memory_id]
            )
            return memory_id
        else:
            # Fallback storage
            import uuid
            memory_id = str(uuid.uuid4())
            entry = {
                "id": memory_id,
                "content": content,
                "metadata": (metadata or {}).copy(),
                "timestamp": current_time,
                "created_at": current_time,
                "last_updated": current_time
            }
            self.fallback_data["memories"].append(entry)
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
            return memory_id

    def query(self, query_text: str, top_k: int = None, metadata_filter: Dict[str, Any] = None,
              sort_by_relevance: bool = True, sort_by_freshness: bool = False) -> List[MemoryEntry]:
        """Query memories by semantic similarity."""
        if top_k is None:
            top_k = self.top_k

        if self.client:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=metadata_filter
            )

            entries = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                entry = MemoryEntry(
                    id=results['ids'][0][i],
                    content=doc,
                    metadata=metadata,
                    relevance_score=results['distances'][0][i] if results.get('distances') else 0.0,
                    created_at=metadata.get("created_at"),
                    last_updated=metadata.get("last_updated")
                )
                entries.append(entry)

            # Normalize relevance scores
            self._normalize_scores(entries)

            # Sort results
            if sort_by_freshness:
                entries.sort(key=lambda e: (e.created_at or 0), reverse=True)
            elif sort_by_relevance:
                entries.sort(key=lambda e: e.relevance_score, reverse=True)

            return entries
        else:
            # Fallback: simple keyword matching with metadata filtering
            entries = self._fallback_query(query_text, top_k, metadata_filter)

            # Set freshness metadata from fallback data
            for entry in entries:
                entry.created_at = entry.metadata.get("created_at")
                entry.last_updated = entry.metadata.get("last_updated")

            # Sort results
            if sort_by_freshness:
                entries.sort(key=lambda e: (e.created_at or 0), reverse=True)
            elif sort_by_relevance:
                entries.sort(key=lambda e: e.relevance_score, reverse=True)

            return entries

    def _normalize_scores(self, entries: List[MemoryEntry]) -> None:
        """
        Normalize relevance scores to [0, 1] range (in-place).

        Args:
            entries: List of MemoryEntry objects with relevance scores
        """
        if not entries:
            return

        scores = [e.relevance_score for e in entries]
        min_score, max_score = min(scores), max(scores)

        if max_score - min_score == 0:
            # All scores are the same
            for entry in entries:
                entry.relevance_score = 1.0
        else:
            for entry in entries:
                entry.relevance_score = (entry.relevance_score - min_score) / (max_score - min_score)

    def _fallback_query(self, query: str, top_k: int, metadata_filter: Dict[str, Any] = None) -> List[MemoryEntry]:
        """Fallback keyword-based search with optional metadata filtering."""
        memories = self.fallback_data.get("memories", [])

        # Apply metadata filter first
        if metadata_filter:
            filtered = []
            for mem in memories:
                match = True
                for key, value in metadata_filter.items():
                    if mem.get('metadata', {}).get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(mem)
            memories = filtered

        query_words = set(query.lower().split())

        scored = []
        for mem in memories:
            content_words = set(mem['content'].lower().split())
            intersection = len(query_words & content_words)
            score = intersection / len(query_words) if query_words else 0
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)

        entries = []
        for score, mem in scored[:top_k]:
            entry = MemoryEntry(
                id=mem['id'],
                content=mem['content'],
                metadata=mem.get('metadata', {}),
                relevance_score=score,
                created_at=mem.get('created_at'),
                last_updated=mem.get('last_updated')
            )
            entries.append(entry)

        return entries

    def clear(self) -> None:
        """Clear all long-term memories."""
        if self.client:
            self.collection.delete(where={})
        else:
            self.fallback_data = {"memories": []}
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f)

    def count(self) -> int:
        """Return the number of stored memories."""
        if self.client:
            return self.collection.count()
        else:
            return len(self.fallback_data.get("memories", []))

    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        if self.client:
            result = self.collection.get(ids=[memory_id])
            if result and result['ids'] and len(result['ids']) > 0:
                metadata = result['metadatas'][0] if result.get('metadatas') else {}
                return MemoryEntry(
                    id=result['ids'][0],
                    content=result['documents'][0] if result.get('documents') else "",
                    metadata=metadata,
                    created_at=metadata.get("created_at"),
                    last_updated=metadata.get("last_updated")
                )
            return None
        else:
            for mem in self.fallback_data.get("memories", []):
                if mem['id'] == memory_id:
                    return MemoryEntry(
                        id=mem['id'],
                        content=mem['content'],
                        metadata=mem.get('metadata', {}),
                        relevance_score=0.0,
                        created_at=mem.get('created_at'),
                        last_updated=mem.get('last_updated')
                    )
            return None

    def delete(self, memory_id: str) -> bool:
        """Delete a specific memory by ID."""
        if self.client:
            try:
                self.collection.delete(ids=[memory_id])
                return True
            except Exception:
                return False
        else:
            memories = self.fallback_data.get("memories", [])
            original_len = len(memories)
            self.fallback_data["memories"] = [m for m in memories if m['id'] != memory_id]
            if self.fallback_file:
                with open(self.fallback_file, 'w') as f:
                    json.dump(self.fallback_data, f, indent=2)
            return original_len != len(self.fallback_data["memories"])

    def get_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[MemoryEntry]:
        """Query memories by metadata filters."""
        if self.client:
            # ChromaDB supports metadata filtering
            result = self.collection.get(where=metadata_filter)
            entries = []
            for i, doc in enumerate(result['documents'] if result.get('documents') else []):
                metadata = result['metadatas'][i] if result.get('metadatas') else {}
                entries.append(MemoryEntry(
                    id=result['ids'][i] if result.get('ids') else "",
                    content=doc,
                    metadata=metadata,
                    created_at=metadata.get("created_at"),
                    last_updated=metadata.get("last_updated")
                ))
            return entries
        else:
            # Fallback: simple keyword matching on metadata values
            memories = self.fallback_data.get("memories", [])
            entries = []
            for mem in memories:
                match = True
                for key, value in metadata_filter.items():
                    if mem.get('metadata', {}).get(key) != value:
                        match = False
                        break
                if match:
                    entries.append(MemoryEntry(
                        id=mem['id'],
                        content=mem['content'],
                        metadata=mem.get('metadata', {}),
                        relevance_score=0.0,
                        created_at=mem.get('created_at'),
                        last_updated=mem.get('last_updated')
                    ))
            return entries


# Global instance
long_term_memory = LongTermMemory()
