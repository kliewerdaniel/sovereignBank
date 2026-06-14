"""SQLite metadata store for memory objects."""

from __future__ import annotations

import aiosqlite
from pathlib import Path
from typing import Optional

from sovereign_memory_bank.models.enums import MemoryType, MemoryStatus
from sovereign_memory_bank.models.memory_object import MemoryObject


SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_objects (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT DEFAULT '',
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'active',
    embedding_id TEXT,
    graph_node_id TEXT,
    source_ids TEXT DEFAULT '[]',
    tags TEXT DEFAULT '[]',
    layer TEXT,
    created TEXT NOT NULL,
    modified TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_objects(type);
CREATE INDEX IF NOT EXISTS idx_memory_status ON memory_objects(status);
CREATE INDEX IF NOT EXISTS idx_memory_layer ON memory_objects(layer);
"""


class SQLiteStore:
    """Async SQLite store for memory object metadata."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def save(self, obj: MemoryObject, layer: str = "1") -> None:
        import json

        await self._db.execute(
            """INSERT OR REPLACE INTO memory_objects
               (id, type, title, confidence, status, embedding_id, graph_node_id,
                source_ids, tags, layer, created, modified)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                obj.id,
                obj.type.value,
                obj.title,
                obj.confidence,
                obj.status.value,
                obj.embedding_id,
                obj.graph_node_id,
                json.dumps(obj.source_ids),
                json.dumps(obj.tags),
                layer,
                obj.created.isoformat(),
                obj.modified.isoformat(),
            ),
        )
        await self._db.commit()

    async def get(self, obj_id: str) -> Optional[dict]:
        cursor = await self._db.execute("SELECT * FROM memory_objects WHERE id = ?", (obj_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def delete(self, obj_id: str) -> bool:
        cursor = await self._db.execute("DELETE FROM memory_objects WHERE id = ?", (obj_id,))
        await self._db.commit()
        return cursor.rowcount > 0

    async def list_by_type(self, mem_type: MemoryType) -> list[dict]:
        cursor = await self._db.execute(
            "SELECT * FROM memory_objects WHERE type = ? ORDER BY created", (mem_type.value,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def list_by_status(self, status: MemoryStatus) -> list[dict]:
        cursor = await self._db.execute(
            "SELECT * FROM memory_objects WHERE status = ? ORDER BY created", (status.value,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def list_all(self) -> list[dict]:
        cursor = await self._db.execute("SELECT * FROM memory_objects ORDER BY created")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def count(self, mem_type: Optional[MemoryType] = None) -> int:
        if mem_type:
            cursor = await self._db.execute(
                "SELECT COUNT(*) FROM memory_objects WHERE type = ?", (mem_type.value,)
            )
        else:
            cursor = await self._db.execute("SELECT COUNT(*) FROM memory_objects")
        row = await cursor.fetchone()
        return row[0]

    async def update_embedding(self, obj_id: str, embedding_id: str) -> None:
        await self._db.execute(
            "UPDATE memory_objects SET embedding_id = ?, modified = datetime('now') WHERE id = ?",
            (embedding_id, obj_id),
        )
        await self._db.commit()

    async def update_graph_node(self, obj_id: str, graph_node_id: str) -> None:
        await self._db.execute(
            "UPDATE memory_objects SET graph_node_id = ?, modified = datetime('now') WHERE id = ?",
            (graph_node_id, obj_id),
        )
        await self._db.commit()
