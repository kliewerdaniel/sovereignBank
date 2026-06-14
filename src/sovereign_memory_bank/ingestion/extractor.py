"""Extract atomic memory objects from source documents."""

from __future__ import annotations

import re
from typing import Optional

from sovereign_memory_bank.models.enums import MemoryType
from sovereign_memory_bank.models.memory_object import (
    MemoryObject,
    Concept,
    Claim,
    Entity,
    Relationship,
)


class Extractor:
    """Extracts concepts, claims, entities, and relationships from markdown text."""

    def extract(self, content: str, source_id: str = "") -> list[MemoryObject]:
        """Extract all memory objects from markdown content."""
        objects: list[MemoryObject] = []

        # Extract the title from markdown heading
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_title = title_match.group(1) if title_match else source_id

        # Extract concepts from headings and key terms
        concepts = self._extract_concepts(content, source_id, doc_title)
        objects.extend(concepts)

        # Extract claims (sentences with assertive language)
        claims = self._extract_claims(content, source_id, doc_title)
        objects.extend(claims)

        # Extract entities (proper nouns, technical terms)
        entities = self._extract_entities(content, source_id)
        objects.extend(entities)

        # Extract relationships between concepts
        relationships = self._extract_relationships(content, concepts, source_id)
        objects.extend(relationships)

        return objects

    def _extract_concepts(
        self, content: str, source_id: str, doc_title: str
    ) -> list[Concept]:
        """Extract concepts from markdown headings and paragraphs."""
        concepts = []
        seen_titles = set()

        # Extract from H2/H3 headings
        for match in re.finditer(r"^#{2,3}\s+(.+)$", content, re.MULTILINE):
            title = match.group(1).strip()
            if title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            # Get the paragraph after this heading
            start = match.end()
            next_heading = re.search(r"^#{1,3}\s+", content[start:], re.MULTILINE)
            end = start + next_heading.start() if next_heading else len(content)
            body = content[start:end].strip()

            concepts.append(
                Concept(
                    title=title,
                    description=body[:500] if body else "",
                    source_ids=[source_id] if source_id else [],
                    tags=self._extract_tags(title),
                )
            )

        # If no concepts from headings, create one for the document
        if not concepts:
            concepts.append(
                Concept(
                    title=doc_title,
                    description=content[:500],
                    source_ids=[source_id] if source_id else [],
                )
            )

        return concepts

    def _extract_claims(
        self, content: str, source_id: str, doc_title: str
    ) -> list[Claim]:
        """Extract factual claims from sentences."""
        claims = []
        claim_patterns = [
            r"(?:is|are|was|were|can|could|will|would|should|must|shall)\s+[^\.\!]+[\.\!]",
        ]

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 300:
                continue
            # Check if it looks like a claim
            for pattern in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(
                        Claim(
                            title=sentence[:80],
                            description=sentence,
                            claim_text=sentence,
                            source_ids=[source_id] if source_id else [],
                        )
                    )
                    break

        return claims[:50]  # Limit to prevent explosion

    def _extract_entities(self, content: str, source_id: str) -> list[Entity]:
        """Extract named entities from text."""
        entities = []
        seen = set()

        # Simple pattern: capitalized words/phrases
        entity_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
        for match in re.finditer(entity_pattern, content):
            name = match.group(1)
            if name.lower() in seen or len(name) < 3:
                continue
            seen.add(name.lower())

            # Determine entity type
            entity_type = "concept"
            if name in ("I", "He", "She", "They"):
                continue

            entities.append(
                Entity(
                    title=name,
                    entity_type=entity_type,
                    source_ids=[source_id] if source_id else [],
                )
            )

        return entities[:100]  # Limit

    def _extract_relationships(
        self, content: str, concepts: list[Concept], source_id: str
    ) -> list[Relationship]:
        """Extract relationships between concepts."""
        relationships = []
        if len(concepts) < 2:
            return relationships

        # Create relationships between concepts that co-occur in the same section
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i + 1 :]:
                # Check if both concepts appear near each other
                if c1.title.lower() in content.lower() and c2.title.lower() in content.lower():
                    relationships.append(
                        Relationship(
                            title=f"{c1.title} <-> {c2.title}",
                            description=f"Co-occurrence relationship between {c1.title} and {c2.title}",
                            source_id=c1.id,
                            target_id=c2.id,
                            edge_type="related_to",
                            source_ids=[source_id] if source_id else [],
                        )
                    )

        return relationships[:50]

    def _extract_tags(self, text: str) -> list[str]:
        """Extract simple tags from text."""
        tags = []
        tech_terms = [
            "python", "api", "database", "ml", "ai", "llm", "agent",
            "graph", "vector", "embedding", "memory", "system",
        ]
        text_lower = text.lower()
        for term in tech_terms:
            if term in text_lower:
                tags.append(term)
        return tags
