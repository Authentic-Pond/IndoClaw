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


@dataclass
class MemoryEntry:
    """Represents a memory entry in long-term storage."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    timestamp: float = field(default_factory=time.time)
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LongTermMemory:
    """Manages long-term memory using vector embeddings."""
    
    def __init__(self, db_path: str = "./data/chroma", top_k: int = 5):
        self.db_path = db_path
        self.top_k = top_k
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the vector database."""
        if not CHROMA_AVAILABLE:
            self._setup_fallback()
            return
        
        os.makedirs(self.db_path, exist_ok=True)
        
        try:
            from chromadb.config import Settings as ChromaSettings
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
        if self.client:
            import uuid
            memory_id = str(uuid.uuid4())
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
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
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            self.fallback_data["memories"].append(entry)
            with open(self.fallback_file, 'w') as f:
                json.dump(self.fallback_data, f, indent=2)
            return memory_id
    
    def query(self, query_text: str, top_k: int = None) -> List[MemoryEntry]:
        """Query memories by semantic similarity."""
        if top_k is None:
            top_k = self.top_k
        
        if self.client:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            entries = []
            for i, doc in enumerate(results['documents'][0]):
                entry = MemoryEntry(
                    id=results['ids'][0][i],
                    content=doc,
                    metadata=results['metadatas'][0][i],
                    relevance_score=results['distances'][0][i] if results.get('distances') else 0.0
                )
                entries.append(entry)
            return entries
        else:
            # Fallback: simple keyword matching
            return self._fallback_query(query_text, top_k)
    
    def _fallback_query(self, query: str, top_k: int) -> List[MemoryEntry]:
        """Fallback keyword-based search."""
        memories = self.fallback_data.get("memories", [])
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
                relevance_score=score
            )
            entries.append(entry)
        
        return entries
    
    def clear(self) -> None:
        """Clear all long-term memories."""
        if self.client:
            self.collection.delete(where={})
        else:
            self.fallback_data = {"memories": []}
            with open(self.fallback_file, 'w') as f:
                json.dump(self.fallback_data, f)
    
    def count(self) -> int:
        """Return the number of stored memories."""
        if self.client:
            return self.collection.count()
        else:
            return len(self.fallback_data.get("memories", []))


# Global instance
long_term_memory = LongTermMemory()