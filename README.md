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

## Quick Start

### Prerequisites

- Python 3.13+
- [Ollama](https://ollama.ai) running locally (optional, for embeddings)

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

# Ingest documents (fast, no embeddings)
smb ingest --source kbmd/blog --skip-embeddings

# Check status
smb status

# Start the API server
smb serve
```

## Agent Skill

An agent skill is installed at `~/.agents/skills/sovereign-memory-bank/SKILL.md`. To use it with an AI agent:

1. The skill file is auto-discovered by agents that support skill loading
2. When you mention memory bank, knowledge graph, smb, or cognitive memory, the agent will load the skill
3. The skill provides the agent with full context on CLI commands, API endpoints, workflows, and configuration

To manually load the skill in a conversation, tell the agent:

> Load the sovereign-memory-bank skill

Or reference the skill file directly:

```
~/.agents/skills/sovereign-memory-bank/SKILL.md
```

## Test Results

Tested with 134 blog posts from `kbmd/blog/`:

| Metric | Value |
|--------|-------|
| Files processed | 134/134 |
| Errors | 0 |
| Memory objects | 25,218 |
| Graph nodes | 25,353 |
| Graph edges | 25,219 |
| Contradictions | 6,859 |
| Research questions | 6,859 |
| Test suite | 40/40 passing |

## License

MIT

---
---

# Agent Skill: sovereign-memory-bank

The following is the complete agent skill file for the Sovereign Memory Bank. This skill is installed at `~/.agents/skills/sovereign-memory-bank/SKILL.md` and is used by AI agents to interact with the system.

---

```
---
name: sovereign-memory-bank
description: "Autonomous cognitive memory system for agent reasoning and knowledge synthesis. Ingests markdown documents, extracts memory objects (concepts, claims, entities), builds a knowledge graph with typed edges, generates vector embeddings, and evolves its own knowledge through contradiction detection, abstraction promotion, and synthesis generation. Use this skill when the user wants to ingest documents into a memory bank, query a knowledge graph, run evolution cycles, start the agent API, or work with cognitive memory architectures. Also use when the user mentions memory bank, knowledge graph, cognitive memory, smb, or wants to build a local-first AI memory system."
---
```

# Sovereign Memory Bank Skill

Local-first autonomous cognitive memory system for agent reasoning and knowledge synthesis.

## What This Skill Does

This skill guides you through using the Sovereign Memory Bank (SMB) — a 7-layer cognitive memory architecture that ingests markdown documents and transforms them into an evolving knowledge substrate optimized for agent reasoning, not retrieval.

**Core Philosophy:** *The purpose is not retrieval. The purpose is synthesis.*
- Memory objects are cognitive artifacts (concepts, claims, entities), not documents
- The knowledge graph supports multi-hop reasoning with typed nodes and edges
- The evolution engine autonomously merges duplicates, detects contradictions, and promotes abstractions
- All processing is local — no cloud API dependency

## When to Use This Skill

Use this skill when:

- **Ingesting documents** — transforming markdown files into memory objects
- **Querying knowledge** — searching the memory bank via API or graph traversal
- **Running evolution** — triggering contradiction detection, dedup, synthesis
- **Starting the agent interface** — launching the FastAPI server for agent access
- **Exploring the memory bank** — inspecting layers, graph stats, or memory objects
- **Building cognitive systems** — designing memory architectures for AI agents
- **The user mentions** memory bank, knowledge graph, cognitive memory, smb, evolution engine, or local-first AI memory

**Do NOT use this skill when:** the user wants a simple vector database, document search, or RAG without cognitive architecture.

## Prerequisites

Before running any SMB commands, verify:

1. **Python 3.13+ installed** — Run `python --version` to check
2. **SMB installed** — Run `smb --help` to check
3. **Ollama running** (optional) — `ollama serve` should be active for embeddings

If SMB isn't installed:
```bash
cd /path/to/newbank
pip install -e ".[dev]"
```

## Project Structure

```
newbank/
├── kbmd/                          # Source markdown documents
├── memory-bank/                   # Generated memory bank
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
├── pyproject.toml
└── smb.sspec                     # SovereignSpec specification
```

## The SMB Workflow

Execute these steps in order when working with the Sovereign Memory Bank.

### Step 1: Initialize the Memory Bank

```bash
smb init
```

Creates the `memory-bank/` directory structure with all 7 layers.

### Step 2: Ingest Documents

```bash
# Ingest all documents from kbmd/
smb ingest

# Ingest from a specific directory
smb ingest --source /path/to/docs

# Ingest without embeddings (faster, no Ollama needed)
smb ingest --source kbmd/blog --skip-embeddings
```

Documents are:
1. Stored immutably in Layer 0
2. Extracted into concepts, claims, entities, relationships (Layer 1)
3. Added to the knowledge graph with typed edges
4. (Optional) Embedded in ChromaDB for semantic search

### Step 3: Run Evolution Cycles

```bash
smb evolve
```

The evolution engine:
1. Detects and merges duplicate concepts
2. Splits overloaded concepts into focused sub-concepts
3. Detects contradictions between claims
4. Generates research questions from contradictions
5. Promotes recurring patterns into abstractions
6. Generates novel syntheses from related concepts

### Step 4: Start the Agent Interface

```bash
# Start the API server
smb serve

# Start on custom host/port
smb serve --host 127.0.0.1 --port 9000
```

### Step 5: Check Status

```bash
smb status
```

Shows file counts per layer, graph stats, and vector store info.

## CLI Reference

| Command | Description |
|---------|-------------|
| `smb init` | Initialize memory bank directory structure |
| `smb ingest [--source PATH] [--skip-embeddings]` | Ingest markdown documents |
| `smb evolve` | Run one evolution cycle |
| `smb serve [--host HOST] [--port PORT]` | Start FastAPI agent interface |
| `smb status` | Show memory bank statistics |

## API Reference

### Memory Objects

```
GET    /api/memory/              — List all memory objects
POST   /api/memory/              — Create a memory object
GET    /api/memory/{id}          — Get a memory object
PUT    /api/memory/{id}          — Update a memory object
DELETE /api/memory/{id}          — Delete a memory object
```

**Create request:**
```json
{
  "type": "concept",
  "title": "Dynamic Persona Systems",
  "description": "A system for creating adaptive AI personas",
  "confidence": 0.85,
  "tags": ["ai", "personas"]
}
```

### Knowledge Graph

```
GET /api/graph/stats             — Graph statistics
GET /api/graph/nodes/{id}        — Get a specific node
GET /api/graph/neighbors/{id}    — Get neighbors (optional ?edge_type=related_to)
GET /api/graph/multi-hop/{id}    — Multi-hop query (?max_hops=3)
GET /api/graph/path/{start}/{end}— Find path between nodes
POST /api/graph/nodes            — Add a node
POST /api/graph/edges            — Add an edge
GET /api/graph/type/{type}       — List nodes by type
```

### Search

```
POST /api/search/                — Semantic vector search
GET  /api/search/stats           — Vector store statistics
```

**Search request:**
```json
{
  "query": "AI agents",
  "n_results": 10,
  "type_filter": "concept"
}
```

### Hybrid Recall

```
POST /api/hybrid/                — Combined vector search + graph traversal
```

**Hybrid request:**
```json
{
  "query": "machine learning",
  "n_results": 5,
  "max_hops": 2
}
```

## Memory Object Types

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

## Graph Edge Types

`references` · `supports` · `contradicts` · `extends` · `derives_from` · `inspired_by` · `evolves_into` · `related_to` · `contains` · `explains`

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

## Configuration

Configuration is managed via environment variables or `.env`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SMB_PROJECT_ROOT` | `.` | Project root directory |
| `SMB_MEMORY_BANK_DIR` | `{root}/memory-bank` | Memory bank output directory |
| `SMB_KBMD_DIR` | `{root}/kbmd` | Source documents directory |
| `SMB_OLLAMA_HOST` | `http://localhost:11434` | Ollama API host |
| `SMB_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `SMB_API_HOST` | `0.0.0.0` | API server host |
| `SMB_API_PORT` | `8000` | API server port |

## Common Workflows

### Ingest and Query

```bash
# 1. Initialize
smb init

# 2. Ingest documents
smb ingest --source kbmd/blog --skip-embeddings

# 3. Start API
smb serve

# 4. Query via API
curl -X POST http://localhost:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents", "n_results": 5}'
```

### Run Full Evolution

```bash
# Ingest with embeddings (requires Ollama)
smb ingest --source kbmd/blog

# Run evolution (detects contradictions, creates abstractions)
smb evolve

# Check results
smb status
```

### Agent Integration

```python
import httpx

# Create memory object
r = httpx.post("http://localhost:8000/api/memory/", json={
    "type": "concept",
    "title": "Agent Memory",
    "description": "Memory system for AI agents"
})
obj = r.json()

# Add graph relationship
httpx.post("http://localhost:8000/api/graph/edges", json={
    "source": f"mem-{obj['id']}",
    "target": "mem-existing-concept",
    "edge_type": "extends"
})

# Hybrid search
r = httpx.post("http://localhost:8000/api/hybrid/", json={
    "query": "memory systems",
    "n_results": 5,
    "max_hops": 2
})
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_graph.py -v

# Run with coverage
pytest tests/ --cov=sovereign_memory_bank
```

## Tips

1. **Use `--skip-embeddings`** for fast ingestion without Ollama
2. **Run `smb evolve` periodically** to detect contradictions and create abstractions
3. **The graph is the brain** — use multi-hop queries for deep reasoning
4. **Contradictions are features** — they generate research questions
5. **Layer 0 is immutable** — source documents are preserved exactly
6. **Memory objects are markdown** — human-readable and machine-parseable
7. **The API is agent-agnostic** — any HTTP client can interact with it
