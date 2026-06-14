"""Layer directory structure manager."""

from pathlib import Path

from sovereign_memory_bank.models.enums import LayerIndex


# Directory structure for each layer
LAYER_DIRECTORIES: dict[LayerIndex, list[str]] = {
    LayerIndex.SOURCE: ["source"],
    LayerIndex.EXTRACTED: ["concepts", "claims", "entities", "relationships"],
    LayerIndex.SEMANTIC: ["taxonomy", "clusters", "communities"],
    LayerIndex.REFLECTIVE: ["insights", "questions", "contradictions"],
    LayerIndex.SYNTHETIC: ["abstractions", "world-models", "meta-concepts", "syntheses"],
    LayerIndex.NARRATIVE: ["narratives", "timelines", "evolution"],
    LayerIndex.EXECUTIVE: ["research", "specifications", "projects", "plans"],
}


class LayerManager:
    """Manages the memory-bank directory structure."""

    def __init__(self, memory_bank_dir: Path) -> None:
        self.root = memory_bank_dir

    def initialize(self) -> None:
        """Create all layer directories."""
        self.root.mkdir(parents=True, exist_ok=True)
        for layer_idx, subdirs in LAYER_DIRECTORIES.items():
            layer_dir = self.root / f"layer-{layer_idx.value}"
            layer_dir.mkdir(parents=True, exist_ok=True)
            for sub in subdirs:
                (layer_dir / sub).mkdir(parents=True, exist_ok=True)

    def get_layer_dir(self, layer: LayerIndex) -> Path:
        return self.root / f"layer-{layer.value}"

    def get_subdir(self, layer: LayerIndex, subdir: str) -> Path:
        return self.root / f"layer-{layer.value}" / subdir

    def layer_exists(self, layer: LayerIndex) -> bool:
        return (self.root / f"layer-{layer.value}").is_dir()

    def list_layers(self) -> list[Path]:
        return sorted(self.root.glob("layer-*"))
