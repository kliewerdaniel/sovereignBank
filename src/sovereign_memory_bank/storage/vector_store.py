"""ChromaDB vector store for semantic embeddings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from sovereign_memory_bank.models.memory_object import MemoryObject


class VectorStore:
    """Local ChromaDB vector store for memory object embeddings."""

    def __init__(self, persist_dir: Path, collection_name: str = "memory_objects") -> None:
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None

    def initialize(self) -> None:
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _ensure_init(self) -> None:
        if self._collection is None:
            self.initialize()

    def add(
        self,
        obj_id: str,
        text: str,
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Add an embedding for a memory object."""
        self._ensure_init()
        meta = metadata or {}
        if embedding:
            self._collection.add(
                ids=[obj_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta],
            )
        else:
            self._collection.add(
                ids=[obj_id],
                documents=[text],
                metadatas=[meta],
            )
        return obj_id

    def update(
        self,
        obj_id: str,
        text: str,
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Update an existing embedding."""
        self._ensure_init()
        meta = metadata or {}
        if embedding:
            self._collection.update(
                ids=[obj_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta],
            )
        else:
            self._collection.update(
                ids=[obj_id],
                documents=[text],
                metadatas=[meta],
            )

    def delete(self, obj_id: str) -> None:
        self._ensure_init()
        self._collection.delete(ids=[obj_id])

    def query(
        self,
        text: Optional[str] = None,
        embedding: Optional[list[float]] = None,
        n_results: int = 10,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """Semantic search returning matching memory objects."""
        self._ensure_init()
        kwargs: dict = {"n_results": n_results}
        if text:
            kwargs["query_texts"] = [text]
        if embedding:
            kwargs["query_embeddings"] = [embedding]
        if where:
            kwargs["where"] = where

        try:
            results = self._collection.query(**kwargs)
        except Exception:
            return []  # Graceful fallback for dimension mismatches etc.

        items = []
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for i, obj_id in enumerate(ids):
            items.append(
                {
                    "id": obj_id,
                    "distance": distances[i] if i < len(distances) else None,
                    "document": documents[i] if i < len(documents) else None,
                    "metadata": metadatas[i] if i < len(metadatas) else None,
                }
            )
        return items

    def get(self, obj_id: str) -> Optional[dict]:
        self._ensure_init()
        results = self._collection.get(ids=[obj_id], include=["documents", "metadatas"])
        if results["ids"]:
            return {
                "id": results["ids"][0],
                "document": results["documents"][0] if results["documents"] else None,
                "metadata": results["metadatas"][0] if results["metadatas"] else None,
            }
        return None

    def count(self) -> int:
        self._ensure_init()
        return self._collection.count()

    def list_all(self, limit: int = 1000) -> list[dict]:
        self._ensure_init()
        results = self._collection.get(limit=limit, include=["documents", "metadatas"])
        items = []
        for i, obj_id in enumerate(results["ids"]):
            items.append(
                {
                    "id": obj_id,
                    "document": results["documents"][i] if results["documents"] else None,
                    "metadata": results["metadatas"][i] if results["metadatas"] else None,
                }
            )
        return items
