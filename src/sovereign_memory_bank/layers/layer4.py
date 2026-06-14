"""Layer 4: Synthetic Memory (abstractions, world-models, meta-concepts, syntheses)."""

from __future__ import annotations

from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Abstraction, Synthesis
from sovereign_memory_bank.storage.markdown_store import MarkdownStore


class Layer4:
    """Manages synthetic memory objects."""

    def __init__(self, store: MarkdownStore) -> None:
        self.store = store

    def save_abstraction(self, abstraction: Abstraction) -> None:
        self.store.save(abstraction)

    def save_synthesis(self, synthesis: Synthesis) -> None:
        self.store.save(synthesis)

    def list_abstractions(self) -> list[Abstraction]:
        return self.store.list_objects(MemoryType.ABSTRACTION)

    def list_syntheses(self) -> list[Synthesis]:
        return self.store.list_objects(MemoryType.SYNTHESIS)

    def get_by_level(self, level: int) -> list[Abstraction]:
        return [a for a in self.list_abstractions() if a.level == level]

    def count(self) -> int:
        return len(self.list_abstractions()) + len(self.list_syntheses())
