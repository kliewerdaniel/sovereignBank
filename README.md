# Sovereign Memory Bank

An autonomous cognitive memory system that ingests markdown documents and creates a continuously evolving memory architecture optimized for agent reasoning and knowledge synthesis.

**The purpose is not retrieval. The purpose is synthesis.**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What It Does

Sovereign Memory Bank takes a directory of markdown documents (`kbmd/`) and transforms them into a 7-layer cognitive memory architecture. The system extracts atomic memory objects, builds a knowledge graph, generates vector embeddings, and periodically evolves its own knowledge organization through an autonomous evolution engine.

Key capabilities:

- **Multi-layer memory architecture** (Layers 0-6) from raw source to executive memory
- **Knowledge graph** with typed nodes and edges supporting multi-hop reasoning
- **Vector embeddings** for semantic recall via ChromaDB
- **Autonomous evolution** — merges duplicates, splits overloaded concepts, promotes abstractions, detects contradictions
- **Agent interface** — FastAPI REST API for read, create, modify, and query operations
- **Hybrid recall** — combines vector search with graph traversal
- **Fully local** — no cloud API dependencies

## Architecture

```
Layer 0: Source Memory        — Immutable original documents
Layer 1: Extracted Memory     — Concepts, claims, entities, relationships
Layer 2: Semantic Memory      — Taxonomy, clusters, communities
Layer 3: Reflective Memory    — Insights, questions, contradictions
Layer 4: Synthetic Memory     — Abstractions, world-models, syntheses
Layer 5: Narrative Memory     — Narratives, timelines, evolution history
Layer 6: Executive Memory     — Research, specifications, projects, plans
```

All layers are interconnected via a knowledge graph and vector store, enabling both semantic recall and structural reasoning.

## Quick Start

### Prerequisites

- Python 3.13+
- [Ollama](https://ollama.ai) running locally (for embeddings)

### Install

```bash
git clone https://github.com/youruser/newbank.git
cd newbank
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Initialize and Run

```bash
# Initialize memory bank directory structure
smb init

# Ingest documents from kbmd/
smb ingest

# Run one evolution cycle
smb evolve

# Start the API server
smb serve
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `smb init` | Create `memory-bank/` directory structure (Layers 0-6) |
| `smb ingest [--source PATH]` | Ingest markdown documents from source directory |
| `smb evolve` | Run one evolution cycle (dedup, split, contradictions, abstractions, synthesis) |
| `smb serve [--host HOST] [--port PORT]` | Start the FastAPI agent interface |

## API Reference

### Memory Objects

```
GET    /api/memory/              — List all memory objects
POST   /api/memory/              — Create a memory object
GET    /api/memory/{id}          — Get a memory object
PUT    /api/memory/{id}          — Update a memory object
DELETE /api/memory/{id}          — Delete a memory object
```

### Knowledge Graph

```
GET /api/graph/stats             — Graph statistics (node/edge counts)
GET /api/graph/nodes/{id}        — Get a specific node
GET /api/graph/neighbors/{id}    — Get neighbors (optional edge_type filter)
GET /api/graph/multi-hop/{id}    — Multi-hop query (max_hops, edge_type)
GET /api/graph/path/{start}/{end}— Find path between two nodes
POST /api/graph/nodes            — Add a node
POST /api/graph/edges            — Add an edge
GET /api/graph/type/{type}       — List nodes by type
```

### Search

```
POST /api/search/                — Semantic vector search
GET  /api/search/stats           — Vector store statistics
```

### Hybrid Recall

```
POST /api/hybrid/                — Combined vector search + graph traversal
```

## Memory Object Format

All memory objects are stored as markdown files with YAML frontmatter:

```markdown
---
id: concept-001
type: concept
confidence: 0.91
created: 2026-06-14T00:00:00+00:00
modified: 2026-06-14T00:00:00+00:00
status: active
embedding_id: emb-001
graph_node_id: node-001
title: "Dynamic Persona Systems"
tags:
  - ai
  - personas
---

Dynamic Persona Systems

Description of the concept...
```

### Supported Types

| Type | Layer | Description |
|------|-------|-------------|
| `concept` | 1 | Extracted concepts from source material |
| `claim` | 1 | Factual or opinion claims |
| `entity` | 1 | Named entities (people, orgs, places) |
| `relationship` | 1 | Typed relationships between objects |
| `insight` | 3 | Reflective insights from multiple sources |
| `contradiction` | 3 | Detected contradictions between claims |
| `question` | 3 | Research questions from gaps |
| `synthesis` | 4 | Novel syntheses combining knowledge |
| `abstraction` | 4 | Higher-order abstractions |
| `narrative` | 5 | Narratives connecting ideas over time |

### Graph Edge Types

`references` · `supports` · `contradicts` · `extends` · `derives_from` · `inspired_by` · `evolves_into` · `related_to` · `contains` · `explains`

## Configuration

Configuration is managed via `pydantic-settings`. Defaults:

| Setting | Default | Description |
|---------|---------|-------------|
| `SMB_PROJECT_ROOT` | `.` | Project root directory |
| `SMB_MEMORY_BANK_DIR` | `{root}/memory-bank` | Memory bank output directory |
| `SMB_KBMD_DIR` | `{root}/kbmd` | Source documents directory |
| `SMB_OLLAMA_HOST` | `http://localhost:11434` | Ollama API host |
| `SMB_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `SMB_API_HOST` | `0.0.0.0` | API server host |
| `SMB_API_PORT` | `8000` | API server port |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/
```

## Project Structure

```
newbank/
├── kbmd/                          # Source markdown documents
├── memory-bank/                   # Generated memory bank (after init)
│   ├── layer-0/source/           # Immutable source artifacts
│   ├── layer-1/{concepts,claims,entities,relationships}/
│   ├── layer-2/{taxonomy,clusters,communities}/
│   ├── layer-3/{insights,questions,contradictions}/
│   ├── layer-4/{abstractions,world-models,meta-concepts,syntheses}/
│   ├── layer-5/{narratives,timelines,evolution}/
│   ├── layer-6/{research,specifications,projects,plans}/
│   ├── graph.json                # Knowledge graph
│   ├── vectors/                  # ChromaDB vector store
│   └── metadata.db               # SQLite metadata
├── src/sovereign_memory_bank/     # Source code
├── tests/                         # Test suite
├── .sovereignspec/               # SovereignSpec project config
├── pyproject.toml
├── smb.sspec                     # SovereignSpec specification
└── spec.md                       # Full specification document
```

## Spec-Driven Development

This project was built using [SovereignSpec](https://github.com/kliewerdaniel/sovereignSpec), a local-first spec-driven development engine. The specification lives in `smb.sspec` and `.sovereignspec/`.

```bash
# Validate the spec
sovereignspec spec validate sovereign-memory-bank

# Compile the spec
sovereignspec spec compile sovereign-memory-bank

# Generate tasks
sovereignspec tasks sovereign-memory-bank
```

## License

MIT
