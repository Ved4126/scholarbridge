# Release Notes v1: ScholarBridge Backend MVP

**Release Name:** ScholarBridge Backend MVP
**Recommended Tag:** `v1.0-mvp`

## Release Summary
We are thrilled to announce the completion of the ScholarBridge Backend MVP! This milestone represents the culmination of Phases 0-9, successfully implementing a fully-tested, deterministic scholarship matching engine. The system evaluates student profiles against a local scholarship catalogue using a rules-based system of hard pre-filters and Match/Tractability (M/T) scoring heuristics.

## Completed Phases
- Phases 1-8 covering core logic, M/T engine, API exposure, and integration testing.
- Phase 9 completing comprehensive documentation.

## Core Features
- Deterministic Match and Tractability scoring engine.
- Hard pre-filter system for instant eligibility disqualification.
- Actionable feedback generation (Gap Analysis and Action Checklists).
- Profile ingestion, completeness tracking, and validation via Pydantic.

## API Endpoints
- Profile Management: `POST /profile`, `GET /profile/{id}`, `PATCH /profile/{id}`, `DELETE /profile/{id}`, `GET /profile/{id}/completeness`
- Scoring: `POST /score/all`, `POST /score/single`, `GET /score/cached/{id}`
- System: `GET /health`

## Test Result
- **107 passing tests** across 0 errors and 0 failures. The suite covers unit, integration, and edge-case scenarios.

## Known Limitations
The MVP relies entirely on in-memory storage meaning profiles and cache do not persist across restarts. It uses local test data files, has no authentication, no frontend, and operates on pure rules-based logic without any Active Machine Learning or Vector Search. See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for full context.

## Post-MVP Roadmap
Future development will shift focus to persistence (PostgreSQL), user-facing experiences (Next.js, Auth), and advanced AI capabilities (Embeddings, Pinecone, ML ranking) once usage data is gathered. See [POST_MVP_ROADMAP.md](POST_MVP_ROADMAP.md) for future plans.
