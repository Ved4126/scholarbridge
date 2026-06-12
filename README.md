# ScholarBridge Backend MVP

ScholarBridge is an automated scholarship matching system. This repository contains the Backend MVP, which focuses exclusively on the core logic: ingesting a student profile, evaluating eligibility via hard pre-filters, calculating match/tractability scores, and returning a ranked list of recommended scholarships.

## Current MVP Status
**Status:** MVP Complete (Phase 9)
All core business logic, matching engines, API endpoints, and integration tests have been implemented. The MVP is fully functional using in-memory data structures. It is currently tagged at `v1.0-mvp`.

## Architecture Overview
The backend is built with FastAPI and follows a strict separation of concerns:
- **API Layer (`backend/app/api/`)**: Defines FastAPI routers and Pydantic models. Zero business logic.
- **Scoring Engine (`backend/app/scorer/`)**: Handles all logic for matching, filtering, and scoring student profiles against scholarships.
- **Profile Agent (`backend/app/agents/profile_agent.py`)**: Manages the ingestion and validation of student data, converting it into a standardized feature vector.
- **Data Layer (`backend/app/db/database.py`)**: MVP in-memory persistence for profiles and score caching.

## Folder Structure
```
scholarbridge-repo/
├── backend/
│   └── app/
│       ├── agents/          # Profile logic
│       ├── api/             # FastAPI routers
│       ├── db/              # In-memory database
│       ├── scorer/          # Core scoring engine
│       └── main.py          # FastAPI application entry point
├── data/
│   └── scholarships/        # JSON catalogue of scholarships
├── docs/                    # Extensive documentation
├── scripts/                 # Utility scripts (e.g., data loaders)
└── tests/                   # Test suite (pytest)
```

## Setup Instructions
Please refer to [docs/SETUP.md](docs/SETUP.md) for detailed instructions on Python version recommendations, virtual environment setup, and dependency management.

## Running the API
From the repository root, start the FastAPI server:
```bash
.venv/bin/uvicorn backend.app.main:app --reload
```
The API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

## Running Tests
Run the full pytest suite (107 tests) from the project root:
```bash
PYTHONPATH=. .venv/bin/pytest tests/ -v
```

## Endpoint Overview
- **Profile**: `POST /profile`, `GET /profile/{id}`, `PATCH /profile/{id}`, `DELETE /profile/{id}`, `GET /profile/{id}/completeness`
- **Scorer**: `POST /score/all`, `POST /score/single`, `GET /score/cached/{id}`
- **Health**: `GET /health`
*See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for detailed request/response schemas.*

## Development Workflow
Development is currently driven by strict adherence to the MVP scope. See `docs/AI_RULES.md` and `docs/PLAN.md` for guidelines.

## Current Limitations
The system currently uses in-memory storage (volatile across restarts), has no authentication, and no frontend. AI/ML ranking and real database persistence are out-of-scope for this MVP. See [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) for full details.

## Next Roadmap
The post-MVP roadmap focuses on production hardening (PostgreSQL, Redis), adding a Next.js frontend, authentication, and eventually ML/Vector search integration. See [docs/POST_MVP_ROADMAP.md](docs/POST_MVP_ROADMAP.md) for details.
