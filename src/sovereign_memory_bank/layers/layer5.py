"""Layer 5: Narrative Memory (narratives, timelines, evolution)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Narrative
from sovereign_memory_bank.storage.markdown_store import MarkdownStore
from sovereign_memory_bank.layers.layer_manager import LayerIndex


class TimelineEntry(BaseModel):
    date: str
    event: str
    related_ids: list[str] = []


class EvolutionRecord(BaseModel):
    timestamp: str
    action: str  # merge, split, promote, deprecate
    affected_ids: list[str]
    description: str = ""


class Layer5:
    """Manages narrative memory and evolution history."""

    def __init__(self, store: MarkdownStore, layer_manager) -> None:
        self.store = store
        self.layers = layer_manager
        self.timelines_dir = layer_manager.get_subdir(LayerIndex.NARRATIVE, "timelines")
        self.evolution_dir = layer_manager.get_subdir(LayerIndex.NARRATIVE, "evolution")

    def save_narrative(self, narrative: Narrative) -> None:
        self.store.save(narrative)

    def list_narratives(self) -> list[Narrative]:
        return self.store.list_objects(MemoryType.NARRATIVE)

    def save_timeline(self, entry: TimelineEntry) -> Path:
        import json
        path = self.timelines_dir / f"{entry.date}-{entry.event[:30].replace(' ', '-')}.json"
        path.write_text(entry.model_dump_json(indent=2))
        return path

    def list_timelines(self) -> list[TimelineEntry]:
        entries = []
        for f in sorted(self.timelines_dir.glob("*.json")):
            entries.append(TimelineEntry.model_validate_json(f.read_text()))
        return entries

    def save_evolution_record(self, record: EvolutionRecord) -> Path:
        import json
        path = self.evolution_dir / f"{record.timestamp[:10]}-{record.action}.json"
        path.write_text(record.model_dump_json(indent=2))
        return path

    def list_evolution_records(self) -> list[EvolutionRecord]:
        records = []
        for f in sorted(self.evolution_dir.glob("*.json")):
            records.append(EvolutionRecord.model_validate_json(f.read_text()))
        return records
