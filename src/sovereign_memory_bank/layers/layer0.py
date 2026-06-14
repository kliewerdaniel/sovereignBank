"""Layer 0: Source Artifacts (Immutable)."""

from __future__ import annotations

from pathlib import Path

from sovereign_memory_bank.layers.layer_manager import LayerManager, LAYER_DIRECTORIES
from sovereign_memory_bank.models.enums import LayerIndex


class Layer0:
    """Manages immutable source artifacts."""

    def __init__(self, layer_manager: LayerManager) -> None:
        self.layers = layer_manager
        self.source_dir = layer_manager.get_subdir(LayerIndex.SOURCE, "source")

    def store_source(self, file_path: Path) -> Path:
        """Store a source document. Overwrites if exists (initial ingestion only)."""
        dest = self.source_dir / file_path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_text(file_path.read_text())
        return dest

    def get_source(self, filename: str) -> Path | None:
        path = self.source_dir / filename
        return path if path.exists() else None

    def list_sources(self) -> list[Path]:
        return sorted(self.source_dir.glob("*.md"))

    def is_immutable(self) -> bool:
        """Layer 0 is always immutable."""
        return True

    def reject_write(self) -> None:
        raise PermissionError("Layer 0 is immutable - source artifacts cannot be modified")
