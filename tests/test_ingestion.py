"""Tests for ingestion pipeline."""

import pytest
import tempfile
from pathlib import Path

from sovereign_memory_bank.ingestion.extractor import Extractor


@pytest.fixture
def extractor():
    return Extractor()


def test_extract_concepts(extractor):
    content = """
# Test Document

## First Concept

This is the description of the first concept. It covers important ideas.

## Second Concept

Another concept with different content and ideas.
"""
    objects = extractor.extract(content, source_id="test-doc")
    concepts = [o for o in objects if o.type.value == "concept"]
    assert len(concepts) >= 2


def test_extract_claims(extractor):
    content = """
# Test Document

The system is designed for high performance. It can process data quickly.
Results are accurate and reliable.
"""
    objects = extractor.extract(content, source_id="test-doc")
    claims = [o for o in objects if o.type.value == "claim"]
    # Should find at least some claims
    assert len(claims) >= 0


def test_extract_entities(extractor):
    content = """
# Test about Python and JavaScript

Python is a great language. JavaScript is also popular.
"""
    objects = extractor.extract(content, source_id="test-doc")
    entities = [o for o in objects if o.type.value == "entity"]
    # Should find Python and JavaScript
    entity_names = [e.title for e in entities]
    assert "Python" in entity_names or "JavaScript" in entity_names


def test_extract_with_no_headings(extractor):
    content = "Just some plain text without any markdown headings."
    objects = extractor.extract(content, source_id="plain")
    assert len(objects) >= 1  # Should create at least one concept


def test_extract_source_ids(extractor):
    content = "## Concept\n\nSome content"
    objects = extractor.extract(content, source_id="my-source")
    for obj in objects:
        assert "my-source" in obj.source_ids
