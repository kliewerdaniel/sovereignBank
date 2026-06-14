"""Markdown file storage for memory objects with YAML frontmatter."""

from pathlib import Path
from typing import Optional

import yaml

from sovereign_memory_bank.layers.layer_manager import LayerManager, LAYER_DIRECTORIES
from sovereign_memory_bank.models.enums import MemoryType, LayerIndex
from sovereign_memory_bank.models.memory_object import MemoryObject, deserialize_memory


# Mapping of memory types to their layer and subdirectory
TYPE_TO_LOCATION: dict[MemoryType, tuple[LayerIndex, str]] = {
    MemoryType.CONCEPT: (LayerIndex.EXTRACTED, "concepts"),
    MemoryType.CLAIM: (LayerIndex.EXTRACTED, "claims"),
    MemoryType.ENTITY: (LayerIndex.EXTRACTED, "entities"),
    MemoryType.RELATIONSHIP: (LayerIndex.EXTRACTED, "relationships"),
    MemoryType.INSIGHT: (LayerIndex.REFLECTIVE, "insights"),
    MemoryType.CONTRADICTION: (LayerIndex.REFLECTIVE, "contradictions"),
    MemoryType.QUESTION: (LayerIndex.REFLECTIVE, "questions"),
    MemoryType.SYNTHESIS: (LayerIndex.SYNTHETIC, "syntheses"),
    MemoryType.ABSTRACTION: (LayerIndex.SYNTHETIC, "abstractions"),
    MemoryType.NARRATIVE: (LayerIndex.NARRATIVE, "narratives"),
}


class MarkdownStore:
    """Read/write memory objects as markdown files with YAML headers."""

    def __init__(self, layer_manager: LayerManager) -> None:
        self.layers = layer_manager

    def _get_path(self, mem_type: MemoryType, obj_id: str) -> Path:
        layer_idx, subdir = TYPE_TO_LOCATION[mem_type]
        return self.layers.get_subdir(layer_idx, subdir) / f"{obj_id}.md"

    def _parse_yaml_header(self, content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter from markdown content."""
        if not content.startswith("---"):
            return {}, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        raw_header = parts[1]
        body = parts[2].strip()

        # Try standard YAML parse first
        try:
            header_data = yaml.safe_load(raw_header) or {}
            return header_data, body
        except yaml.YAMLError:
            pass

        # Fallback: line-by-line key: value parsing
        header_data = {}
        for line in raw_header.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Handle list items
                if value.startswith("[") and value.endswith("]"):
                    import ast
                    try:
                        value = ast.literal_eval(value)
                    except (ValueError, SyntaxError):
                        pass
                elif value == "":
                    value = None
                header_data[key] = value
        return header_data, body

    def save(self, obj: MemoryObject) -> Path:
        """Persist a memory object to disk."""
        path = self._get_path(obj.type, obj.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(obj.to_markdown())
        return path

    def load(self, mem_type: MemoryType, obj_id: str) -> Optional[MemoryObject]:
        """Load a memory object from disk."""
        path = self._get_path(mem_type, obj_id)
        if not path.exists():
            return None
        content = path.read_text()
        header_data, body = self._parse_yaml_header(content)
        return deserialize_memory(header_data, body)

    def exists(self, mem_type: MemoryType, obj_id: str) -> bool:
        return self._get_path(mem_type, obj_id).exists()

    def delete(self, mem_type: MemoryType, obj_id: str) -> bool:
        path = self._get_path(mem_type, obj_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_objects(self, mem_type: MemoryType) -> list[MemoryObject]:
        """List all objects of a given type."""
        layer_idx, subdir = TYPE_TO_LOCATION[mem_type]
        dir_path = self.layers.get_subdir(layer_idx, subdir)
        objects = []
        for md_file in sorted(dir_path.glob("*.md")):
            try:
                content = md_file.read_text()
                header_data, body = self._parse_yaml_header(content)
                objects.append(deserialize_memory(header_data, body))
            except Exception:
                continue  # Skip unparseable files
        return objects

    def list_all(self) -> list[MemoryObject]:
        """List all memory objects across all types."""
        all_objects = []
        for mem_type in TYPE_TO_LOCATION:
            all_objects.extend(self.list_objects(mem_type))
        return all_objects

    def count(self, mem_type: Optional[MemoryType] = None) -> int:
        if mem_type:
            return len(self.list_objects(mem_type))
        return sum(len(self.list_objects(t)) for t in TYPE_TO_LOCATION)
