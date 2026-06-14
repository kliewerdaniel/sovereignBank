"""Embedding generation for memory objects using Ollama."""

from __future__ import annotations

import httpx
from typing import Optional

from sovereign_memory_bank.config import Settings
from sovereign_memory_bank.models.memory_object import MemoryObject


class Embedder:
    """Generates embeddings via Ollama local API."""

    def __init__(self, settings: Settings) -> None:
        self.host = settings.ollama_host
        self.model = settings.embedding_model
        self._client = httpx.AsyncClient(base_url=self.host, timeout=30.0)

    async def embed_text(self, text: str) -> Optional[list[float]]:
        """Generate embedding for raw text."""
        try:
            response = await self._client.post(
                "/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding")
        except Exception:
            return None

    def embed(self, obj: MemoryObject) -> Optional[list[float]]:
        """Synchronous embedding for a memory object (calls async internally)."""
        import asyncio

        text = f"{obj.title} {obj.description}".strip()
        if not text:
            return None

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're inside an async context, use sync fallback
                return self._embed_sync(text)
            return loop.run_until_complete(self.embed_text(text))
        except RuntimeError:
            return self._embed_sync(text)

    def _embed_sync(self, text: str) -> Optional[list[float]]:
        """Synchronous embedding using httpx."""
        try:
            with httpx.Client(base_url=self.host, timeout=30.0) as client:
                response = client.post(
                    "/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding")
        except Exception:
            return None

    async def embed_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Embed multiple texts."""
        results = []
        for text in texts:
            results.append(await self.embed_text(text))
        return results

    async def close(self) -> None:
        await self._client.aclose()
