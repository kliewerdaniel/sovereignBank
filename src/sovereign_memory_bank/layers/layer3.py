"""Layer 3: Reflective Memory (insights, questions, contradictions)."""

from __future__ import annotations

from typing import Optional

from sovereign_memory_bank.layers.layer_manager import LayerManager
from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import Insight, Question, Contradiction
from sovereign_memory_bank.storage.markdown_store import MarkdownStore, TYPE_TO_LOCATION


class Layer3:
    """Manages reflective cognition objects."""

    def __init__(self, store: MarkdownStore) -> None:
        self.store = store

    def save_insight(self, insight: Insight) -> None:
        self.store.save(insight)

    def save_question(self, question: Question) -> None:
        self.store.save(question)

    def save_contradiction(self, contradiction: Contradiction) -> None:
        self.store.save(contradiction)

    def list_insights(self) -> list[Insight]:
        return self.store.list_objects(MemoryType.INSIGHT)

    def list_questions(self) -> list[Question]:
        return self.store.list_objects(MemoryType.QUESTION)

    def list_contradictions(self) -> list[Contradiction]:
        return self.store.list_objects(MemoryType.CONTRADICTION)

    def get_unanswered_questions(self) -> list[Question]:
        """Return questions that haven't been answered yet."""
        return [q for q in self.list_questions() if q.status.value == "active"]

    def get_active_contradictions(self) -> list[Contradiction]:
        return [c for c in self.list_contradictions() if c.status.value == "active"]
