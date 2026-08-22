# Knowledge Factory Pipeline Architecture

The **Knowledge Factory** is the automated production pipeline for turning raw maritime evidence artifacts (Deck Plan PDFs, shipyard general arrangement blueprints, technical specification sheets, harbor master records) into verified canonical knowledge, W3C BOT semantic graphs, spatial geometry, and deterministic cabin intelligence.

## Pipeline Workflow Stages

```
1. TimEvidence (Raw PDF / CAD / Sensor Logs)
   ↓
2. TimArtifact (Cataloged & Hash-Verified)
   ↓
3. Artifact Queue (ArtifactQueue.ts)
   ↓
4. Spatial & Vector Parser
   ↓
5. JSON Schema Validation (Draft 2020-12)
   ↓
6. Knowledge Diff Engine (KnowledgeDiff.ts)
   ↓
7. Conflict Resolver (ConflictResolver.ts)
   ↓
8. Bridge Officer Tim Approval Gate
   ↓
9. Canonical Knowledge Release (KnowledgePublisher.ts)
   ↓
10. W3C BOT Semantic Graph Builder
   ↓
11. Spatial Geometry Builder (geometry/*.geometry.json)
   ↓
12. Explainability & Intelligence Engine
```

## Module Reference
- [`ArtifactQueue.ts`](../../frontend/src/knowledge/pipeline/ArtifactQueue.ts): Ingestion queue and stage tracker.
- [`KnowledgeDiff.ts`](../../frontend/src/knowledge/pipeline/KnowledgeDiff.ts): Structured entity and field comparator.
- [`ConflictResolver.ts`](../../frontend/src/knowledge/pipeline/ConflictResolver.ts): Contradiction auditor (`MATCH`, `CONFLICT`, `UNKNOWN`, `SUPERSEDED`).
- [`KnowledgePublisher.ts`](../../frontend/src/knowledge/pipeline/KnowledgePublisher.ts): Multi-gate publication validator.
- [`KnowledgeFactory.ts`](../../frontend/src/knowledge/pipeline/KnowledgeFactory.ts): End-to-end production orchestrator and fleet metrics aggregator.
