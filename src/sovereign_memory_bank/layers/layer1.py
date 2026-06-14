"""Layer 1: Extracted Memory Objects (concepts, claims, entities, relationships)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.models.enums import MemoryType, LayerIndex
from sovereign_memory_bank.models.memory_object import (
    MemoryObject, Concept, Claim, Entity, Relationship, deserialize_memory
)
from sovereign_memory_bank.storage.markdown_store import TYPE_TO_LOCATION


class Layer1:
    """Manages extracted atomic memory objects."""

    def __init__(self, layer_manager: LayerManager) -> None:
        self.layers = layer_manager

    def get_dir(self, mem_type: MemoryType) -> Path:
        layer_idx, subdir = TYPE_TO_LOCATION[mem_type]
        return self.layers.get_subdir(layer_idx, subdir)

    def save(self, obj: MemoryObject) -> Path:
        """Save a memory object to its type directory."""
        dir_path = self.get_dir(obj.type)
        dir_path.mkdir(parents=True, exist_ok=True)
        path = dir_path / f"{obj.id}.md"
        path.write_text(obj.to_markdown())
        return path

    def load(self, mem_type: MemoryType, obj_id: str) -> Optional[MemoryObject]:
        """Load a memory object."""
        dir_path = self.get_dir(mem_type)
        path = dir_path / f"{obj_id}.md"
        if not path.exists():
            return None
        import yaml
        content = path.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                header = yaml.safe_load(parts[1]) or {}
                return deserialize_memory(header, parts[2])
        return None

    def list_by_type(self, mem_type: MemoryType) -> list[MemoryObject]:
        """List all objects of a given type."""
        dir_path = self.get_dir(mem_type)
        objects = []
        for md_file in sorted(dir_path.glob("*.md")):
            import yaml
            content = md_file.read_text()
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    header = yaml.safe_load(parts[1]) or {}
                    objects.append(deserialize_memory(header, parts[2]))
        return objects

    def count(self, mem_type: Optional[MemoryType] = None) -> int:
        if mem_type:
            return len(list(self.get_dir(mem_type).glob("*.md")))
        return sum(
            len(list(self.get_dir(t).glob("*.md")))
            for t in TYPE_TO_LOCATION
            if t in [MemoryType.CONCEPT, MemoryType.CLAIM, MemoryType.ENTITY, MemoryType.RELATIONSHIP]
        )
