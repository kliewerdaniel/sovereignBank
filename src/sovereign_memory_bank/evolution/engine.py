"""Evolution engine core - orchestrates memory evolution cycles."""

from __future__ import annotations

from datetime import datetime, timezone

from sovereign_memory_bank.config import Settings
from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.storage.sqlite_store import SQLiteStore
from sovereign_memory_bank.storage.vector_store import VectorStore
from sovereign_memory_bank.graph.graph_store import KnowledgeGraph
from sovereign_memory_bank.evolution.dedup import DuplicateDetector
from sovereign_memory_bank.evolution.splitter import ConceptSplitter
from sovereign_memory_bank.evolution.contradiction_detector import ContradictionDetector
from sovereign_memory_bank.evolution.abstraction import AbstractionPromoter
from sovereign_memory_bank.evolution.synthesis import SynthesisGenerator
from sovereign_memory_bank.models.enums import MemoryType, MemoryStatus
from sovereign_memory_bank.models.memory_object import Concept


class EvolutionEngine:
    """Runs evolution cycles on the memory bank."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.layer_manager = LayerManager(settings.memory_bank_dir)
        self.markdown_store = MarkdownStore(self.layer_manager)
        self.sqlite_store = SQLiteStore(settings.sqlite_db_path)
        self.vector_store = VectorStore(settings.chroma_persist_dir, settings.chroma_collection)
        self.graph = KnowledgeGraph(settings.memory_bank_dir / "graph.json")

        self.dedup = DuplicateDetector(self.markdown_store, self.graph)
        self.splitter = ConceptSplitter(self.markdown_store, self.graph)
        self.contradiction_detector = ContradictionDetector(self.markdown_store, self.graph)
        self.abstraction_promoter = AbstractionPromoter(self.markdown_store, self.graph)
        self.synthesis_generator = SynthesisGenerator(self.markdown_store, self.graph)

    async def initialize(self) -> None:
        self.layer_manager.initialize()
        await self.sqlite_store.initialize()
        self.vector_store.initialize()

    async def run_cycle(self) -> dict:
        """Execute a full evolution cycle."""
        await self.initialize()

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "steps": {},
        }

        # Step 1: Detect and merge duplicates
        dedup_result = await self.dedup.detect_and_merge()
        results["steps"]["dedup"] = dedup_result

        # Step 2: Split overloaded concepts
        split_result = await self.splitter.split_overloaded()
        results["steps"]["split"] = split_result

        # Step 3: Detect contradictions
        contradiction_result = await self.contradiction_detector.detect()
        results["steps"]["contradictions"] = contradiction_result

        # Step 4: Promote abstractions
        abstraction_result = await self.abstraction_promoter.promote()
        results["steps"]["abstractions"] = abstraction_result

        # Step 5: Generate syntheses
        synthesis_result = await self.synthesis_generator.generate()
        results["steps"]["syntheses"] = synthesis_result

        # Save graph
        self.graph.save()
        await self.sqlite_store.close()

        return results
