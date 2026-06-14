"""Document ingestion entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from sovereign_memory_bank.config import Settings
from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.storage.sqlite_store import SQLiteStore
from sovereign_memory_bank.storage.vector_store import VectorStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph, GraphNode, GraphEdge
from sovereign_memory_bank.models.enums import GraphNodeType, NodeEdgeType, LayerIndex
from sovereign_memory_bank.ingestion.extractor import Extractor
from sovereign_memory_bank.ingestion.graph_builder import GraphBuilder


class Ingester:
    """Orchestrates document ingestion into the memory bank."""

    def __init__(self, settings: Settings, skip_embeddings: bool = False) -> None:
        self.settings = settings
        self.skip_embeddings = skip_embeddings
        self.layer_manager = LayerManager(settings.memory_bank_dir)
        self.markdown_store = MarkdownStore(self.layer_manager)
        self.sqlite_store = SQLiteStore(settings.sqlite_db_path)
        self.vector_store = VectorStore(settings.chroma_persist_dir, settings.chroma_collection)
        self.graph = KnowledgeGraph(settings.memory_bank_dir / "graph.json")
        self.extractor = Extractor()
        self.graph_builder = GraphBuilder(self.graph)
        self._embedder = None

    @property
    def embedder(self):
        if self._embedder is None:
            from sovereign_memory_bank.ingestion.embedder import Embedder
            self._embedder = Embedder(self.settings)
        return self._embedder

    async def initialize(self) -> None:
        self.layer_manager.initialize()
        await self.sqlite_store.initialize()
        self.vector_store.initialize()

    async def ingest_directory(self, source_dir: str | Path) -> dict:
        """Ingest all markdown files from a directory."""
        await self.initialize()
        source_path = Path(source_dir)
        if not source_path.exists():
            return {"error": f"Source directory not found: {source_path}"}

        md_files = sorted(source_path.rglob("*.md"))
        results = {"files_found": len(md_files), "files_processed": 0, "errors": [], "objects_total": 0}

        for i, md_file in enumerate(md_files):
            try:
                r = await self.ingest_file(md_file)
                results["files_processed"] += 1
                results["objects_total"] += r["objects_extracted"]
                print(f"  [{i+1}/{len(md_files)}] {md_file.stem} — {r['objects_extracted']} objects", flush=True)
            except Exception as e:
                results["errors"].append({"file": str(md_file), "error": str(e)})
                print(f"  [{i+1}/{len(md_files)}] {md_file.stem} — ERROR: {e}", flush=True)

            # Save graph every 10 files
            if (i + 1) % 10 == 0:
                self.graph.save()

        self.graph.save()
        await self.sqlite_store.close()
        return results

    async def ingest_file(self, file_path: Path) -> dict:
        """Ingest a single markdown file into Layer 0 and extract memory objects."""
        content = file_path.read_text()
        source_id = file_path.stem

        # Store in Layer 0 (immutable source)
        source_obj_path = self.layer_manager.get_subdir(LayerIndex.SOURCE, "source") / file_path.name
        source_obj_path.parent.mkdir(parents=True, exist_ok=True)
        source_obj_path.write_text(content)

        # Add source node to graph
        source_node = GraphNode(
            id=f"source-{source_id}",
            node_type=GraphNodeType.CONCEPT,
            label=file_path.stem,
            metadata={"path": str(file_path), "layer": "0"},
        )
        self.graph.add_node(source_node)

        # Extract memory objects (Layer 1)
        extracted = self.extractor.extract(content, source_id=source_id)

        objects_saved = 0
        for obj in extracted:
            # Save markdown
            self.markdown_store.save(obj)

            # Save metadata
            await self.sqlite_store.save(obj, layer="1")

            # Generate and save embedding (optional)
            if not self.skip_embeddings:
                try:
                    embedding = self.embedder.embed(obj)
                    if embedding:
                        self.vector_store.add(
                            obj_id=obj.id,
                            text=f"{obj.title} {obj.description}",
                            embedding=embedding,
                            metadata={"type": obj.type.value, "source": source_id},
                        )
                        obj.embedding_id = f"emb-{obj.id}"
                        await self.sqlite_store.update_embedding(obj.id, obj.embedding_id)
                except Exception:
                    pass  # Skip embedding on failure

            # Add to graph
            node = self.graph_builder.add_memory_node(obj)
            obj.graph_node_id = node.id

            # Connect to source
            self.graph.add_edge(
                GraphEdge(
                    source=f"source-{source_id}",
                    target=node.id,
                    edge_type=NodeEdgeType.REFERENCES,
                )
            )

            objects_saved += 1

        return {"source": source_id, "objects_extracted": objects_saved}
