# Sovereign Memory Bank - Implementation Tasks

Spec: `sovereign-memory-bank` (v0.1.0)
Generated: 2026-06-14

---

## Phase 1: Foundation & Core Data Models

### [P] Task 1: Project Scaffolding
Status: [x] completed — 2026-06-14
Completed: Project installs with `pip install -e .`, all imports resolve
Files created:
  - pyproject.toml
  - src/sovereign_memory_bank/__init__.py
  - src/sovereign_memory_bank/config.py
  - src/sovereign_memory_bank/cli.py
  - src/sovereign_memory_bank/models/__init__.py
Dependencies: None

### [P] Task 2: Memory Object Data Models (Pydantic)
Status: [ ] pending
Files to create/modify:
  - src/models/memory_object.py
  - src/models/enums.py
Dependencies: Task 1
Acceptance: All memory object types defined with id, type, confidence, created, modified, status, embedding_id, graph_node_id fields. Edge types and node types enums match spec constraints.

### [P] Task 3: Layer Directory Structure
Status: [ ] pending
Files to create/modify:
  - src/layers/__init__.py
  - src/layers/layer_manager.py
Dependencies: Task 2
Acceptance: Can create/verify layer directories (layer-0 through layer-6) under memory-bank/

### [P] Task 4: Knowledge Graph Core
Status: [ ] pending
Files to create/modify:
  - src/graph/__init__.py
  - src/graph/graph_store.py
  - src/graph/node.py
  - src/graph/edge.py
Dependencies: Task 2
Acceptance: Graph supports add_node, add_edge, get_neighbors, multi_hop_query with typed nodes (concepts, entities, claims, insights, narratives, abstractions) and typed edges (references, supports, contradicts, extends, derives_from, inspired_by, evolves_into, related_to, contains, explains)

---

## Phase 2: Storage Layer

### [P] Task 5: Markdown Memory Object Storage
Status: [ ] pending
Files to create/modify:
  - src/storage/__init__.py
  - src/storage/markdown_store.py
Dependencies: Task 2, Task 3
Acceptance: Can persist memory objects as markdown files with YAML headers in correct layer directories. Can load them back. Layer 0 objects are immutable once written.

### [P] Task 6: SQLite Metadata Store
Status: [ ] pending
Files to create/modify:
  - src/storage/sqlite_store.py
  - src/storage/schema.sql
Dependencies: Task 2
Acceptance: Can store/retrieve memory object metadata (id, type, status, created, modified, layer). Supports queries by type, status, layer.

### [P] Task 7: ChromaDB Vector Store
Status: [ ] pending
Files to create/modify:
  - src/storage/vector_store.py
Dependencies: Task 2
Acceptance: Can store embeddings for memory objects, perform semantic search, retrieve by similarity. Uses local ChromaDB instance with nomic-embed-text embeddings.

---

## Phase 3: Ingestion Pipeline

### [P] Task 8: Document Ingestion Entry Point
Status: [ ] pending
Files to create/modify:
  - src/ingestion/__init__.py
  - src/ingestion/ingester.py
Dependencies: Task 5, Task 6, Task 7
Acceptance: Can scan kbmd/ directory, read markdown files, and pass them to extraction pipeline

### [P] Task 9: Atomic Memory Object Extraction
Status: [ ] pending
Files to create/modify:
  - src/ingestion/extractor.py
Dependencies: Task 8
Acceptance: Given a markdown document, extracts concepts, claims, entities, and relationships as memory objects in Layer 1. Each object has required fields populated.

### [P] Task 10: Embedding Generation During Ingestion
Status: [ ] pending
Files to create/modify:
  - src/ingestion/embedder.py
Dependencies: Task 7, Task 9
Acceptance: Each extracted memory object gets an embedding generated and stored in ChromaDB. embedding_id is set on the memory object.

### [P] Task 11: Graph Population During Ingestion
Status: [ ] pending
Files to create/modify:
  - src/ingestion/graph_builder.py
Dependencies: Task 4, Task 9
Acceptance: Extracted memory objects are added to the knowledge graph with correct node types. Relationships between objects are added as edges.

---

## Phase 4: Agent Interface

### [P] Task 12: FastAPI Application Setup
Status: [ ] pending
Files to create/modify:
  - src/api/__init__.py
  - src/api/app.py
  - src/api/routes/__init__.py
Dependencies: Task 1
Acceptance: FastAPI app starts, serves health check endpoint

### [P] Task 13: Memory Object CRUD Endpoints
Status: [ ] pending
Files to create/modify:
  - src/api/routes/memory.py
Dependencies: Task 12, Task 5
Acceptance: GET/POST/PUT/DELETE endpoints for memory objects. Agents can read, create, modify, and reorganize memory objects.

### [P] Task 14: Graph Query Endpoints
Status: [ ] pending
Files to create/modify:
  - src/api/routes/graph.py
Dependencies: Task 12, Task 4
Acceptance: Endpoints for graph traversal, multi-hop queries, neighbor lookup. Supports typed node and edge filtering.

### [P] Task 15: Semantic Search Endpoint
Status: [ ] pending
Files to create/modify:
  - src/api/routes/search.py
Dependencies: Task 12, Task 7
Acceptance: Vector similarity search endpoint. Returns memory objects ranked by semantic relevance.

### [P] Task 16: Hybrid Recall Endpoint
Status: [ ] pending
Files to create/modify:
  - src/api/routes/hybrid.py
Dependencies: Task 14, Task 15
Acceptance: Combines vector search with graph traversal. Returns both semantically similar and graph-connected results.

---

## Phase 5: Evolution Engine

### [P] Task 17: Evolution Engine Core
Status: [ ] pending
Files to create/modify:
  - src/evolution/__init__.py
  - src/evolution/engine.py
Dependencies: Task 4, Task 5, Task 6
Acceptance: Evolution engine can run a full cycle: detect duplicates, merge/split concepts, promote abstractions, detect contradictions, refresh embeddings

### [P] Task 18: Duplicate Detection & Merging
Status: [ ] pending
Files to create/modify:
  - src/evolution/dedup.py
Dependencies: Task 17
Acceptance: Given 100+ concepts with duplicates, engine identifies and merges them. Merged objects retain provenance.

### [P] Task 19: Concept Splitting
Status: [ ] pending
Files to create/modify:
  - src/evolution/splitter.py
Dependencies: Task 17
Acceptance: Overloaded concepts (too many relationships) are split into focused sub-concepts. Relationships are redistributed.

### [P] Task 20: Contradiction Detection
Status: [ ] pending
Files to create/modify:
  - src/evolution/contradiction_detector.py
Dependencies: Task 17
Acceptance: Contradictions between claims are detected. Contradiction objects are created as first-class memory objects with links to conflicting claims. Research questions are generated.

### [P] Task 21: Abstraction Promotion
Status: [ ] pending
Files to create/modify:
  - src/evolution/abstraction.py
Dependencies: Task 17
Acceptance: Higher-order abstractions are constructed automatically from lower-level concepts. Abstractions cite source objects.

### [P] Task 22: Knowledge Synthesis Generation
Status: [ ] pending
Files to create/modify:
  - src/evolution/synthesis.py
Dependencies: Task 17
Acceptance: Syntheses are generated from concepts, claims, relationships, narratives, and insights. Syntheses span multiple source documents and produce novel insights.

---

## Phase 6: Memory Layer Implementation

### [P] Task 23: Layer 0 - Source Artifacts (Immutable)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer0.py
Dependencies: Task 5
Acceptance: Source markdown documents are stored immutably. Any write attempt to Layer 0 is rejected.

### [P] Task 24: Layer 1 - Atomic Memory Objects
Status: [ ] pending
Files to create/modify:
  - src/layers/layer1.py
Dependencies: Task 9
Acceptance: Concepts, claims, entities, relationships are stored and retrievable from Layer 1.

### [P] Task 25: Layer 2 - Organization (Taxonomy, Clusters, Communities)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer2.py
Dependencies: Task 17
Acceptance: Taxonomy, clusters, and communities are maintained. Knowledge is organized into hierarchical and grouped structures.

### [P] Task 26: Layer 3 - Reflective Cognition (Insights, Questions, Contradictions)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer3.py
Dependencies: Task 20
Acceptance: Insights, research questions, and contradictions are stored. Contradiction objects link to conflicting claims.

### [P] Task 27: Layer 4 - Synthetic Memory (Abstractions, World-Models, Meta-Concepts, Syntheses)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer4.py
Dependencies: Task 21, Task 22
Acceptance: Abstractions, world-models, meta-concepts, and syntheses are stored. Each cites source objects.

### [P] Task 28: Layer 5 - Narrative Memory (Narratives, Timelines, Evolution)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer5.py
Dependencies: Task 17
Acceptance: Narratives, timelines, and evolution records are stored. Memory evolution history is tracked.

### [P] Task 29: Layer 6 - Executive Memory (Research, Specifications, Projects, Plans)
Status: [ ] pending
Files to create/modify:
  - src/layers/layer6.py
Dependencies: Task 12
Acceptance: Research topics, specifications, project plans, and executive summaries are stored.

---

## Phase 7: Testing & Validation

### [P] Task 30: Unit Tests for Data Models
Status: [ ] pending
Files to create/modify:
  - tests/test_models.py
Dependencies: Task 2
Acceptance: All memory object types validate correctly. Invalid objects are rejected.

### [P] Task 31: Unit Tests for Storage Layer
Status: [ ] pending
Files to create/modify:
  - tests/test_storage.py
Dependencies: Task 5, Task 6, Task 7
Acceptance: Markdown store, SQLite store, and vector store all pass CRUD tests.

### [P] Task 32: Integration Tests for Ingestion Pipeline
Status: [ ] pending
Files to create/modify:
  - tests/test_ingestion.py
Dependencies: Task 8, Task 9, Task 10, Task 11
Acceptance: tc-smoke-ingestion test case passes: 10 markdown docs produce at least one concept, claim, and entity in Layer 1.

### [P] Task 33: Integration Tests for Contradiction Detection
Status: [ ] pending
Files to create/modify:
  - tests/test_contradictions.py
Dependencies: Task 20
Acceptance: tc-contradiction-detection test case passes: contradictory documents produce contradiction objects and research questions.

### [P] Task 34: Integration Tests for Emergent Synthesis
Status: [ ] pending
Files to create/modify:
  - tests/test_synthesis.py
Dependencies: Task 22
Acceptance: tc-emergent-synthesis test case passes: evolution engine produces syntheses not verbatim in source.

### [P] Task 35: Integration Tests for Multi-Hop Graph Queries
Status: [ ] pending
Files to create/modify:
  - tests/test_graph.py
Dependencies: Task 4
Acceptance: tc-graph-multi-hop test case passes: 3-hop paths are returned correctly.

### [P] Task 36: Integration Tests for Autonomous Evolution
Status: [ ] pending
Files to create/modify:
  - tests/test_evolution.py
Dependencies: Task 17, Task 18, Task 19
Acceptance: tc-autonomous-evolution test case passes: duplicates merged, overloaded concepts split.

### [P] Task 37: Integration Tests for Agent-Writable Interface
Status: [ ] pending
Files to create/modify:
  - tests/test_agent_interface.py
Dependencies: Task 13
Acceptance: tc-agent-writable test case passes: agent can create concept, add relationship, query it back.

### [P] Task 38: Integration Tests for Hybrid Vector+Graph Recall
Status: [ ] pending
Files to create/modify:
  - tests/test_hybrid.py
Dependencies: Task 16
Acceptance: tc-vector-graph-hybrid test case passes: hybrid search returns both semantic and graph-connected results.

---

## Phase 8: Documentation & Polish

### [P] Task 39: API Documentation
Status: [ ] pending
Files to create/modify:
  - docs/api.md
Dependencies: Task 13, Task 14, Task 15, Task 16
Acceptance: All endpoints documented with request/response examples.

### [P] Task 40: Architecture Documentation
Status: [ ] pending
Files to create/modify:
  - docs/architecture.md
Dependencies: None
Acceptance: 7-layer architecture documented with diagrams, data flow, and component descriptions.

### [P] Task 41: Knowledge Graph Update
Status: [ ] pending
Files to create/modify:
  - .sovereignspec/graph/graph.json
Dependencies: All implementation tasks
Acceptance: Graph contains nodes for all modules, specs, and endpoints. Edges reflect dependencies and references.

---

## Parallel Execution Graph

```
Task 1 (Foundation)
├── Task 2 (Data Models) ──┬── Task 3 (Layer Structure)
│                          ├── Task 4 (Graph Core)
│                          ├── Task 5 (Markdown Store) ──┬── Task 8 (Ingestion Entry)
│                          │                             ├── Task 23 (Layer 0)
│                          │                             └── Task 31 (Storage Tests)
│                          ├── Task 6 (SQLite Store) ──┬── Task 8
│                          │                           └── Task 31
│                          ├── Task 7 (Vector Store) ──┬── Task 8
│                          │                           └── Task 31
│                          └── Task 30 (Model Tests)
├── Task 12 (FastAPI) ──┬── Task 13 (CRUD) ──┬── Task 37
│                       ├── Task 14 (Graph API) ──┬── Task 16 (Hybrid) ──┬── Task 38
│                       │                         └── Task 35
│                       ├── Task 15 (Search) ── Task 16
│                       └── Task 29 (Layer 6)
│
Task 8 → Task 9 (Extract) → Task 10 (Embed) + Task 11 (Graph Build)
                         └── Task 32 (Ingestion Tests)
Task 17 (Evolution Engine) → Task 18 + Task 19 + Task 20 + Task 21 + Task 22
                         └── Task 33, Task 34, Task 36
Task 20 → Task 26 (Layer 3)
Task 21 + Task 22 → Task 27 (Layer 4)
Task 17 → Task 25 (Layer 2) + Task 28 (Layer 5)
```
