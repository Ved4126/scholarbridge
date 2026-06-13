# ScholarBridge

> **Scholarship discovery for international students in the US.**
> Rule-based eligibility scoring. Transparent gap analysis. Zero ML during MVP.

---

## What is ScholarBridge?

ScholarBridge is a backend API that helps international students discover scholarships they
are genuinely likely to qualify for. It collects a structured student profile, evaluates all
scholarships against hard eligibility filters and a deterministic match score, and returns a
ranked list of results with gap analysis and action checklist — telling the student exactly what
they qualify for and what they still need to prepare.

---

## Current MVP Status

**Phase 9 complete — documentation written.**

| Phase | Name | Status |
|---|---|---|
| Phase 0 | Repository Inspection | ✅ Complete |
| Phase 1 | FastAPI Foundation | ✅ Complete |
| Phase 2 | Student Profile Model | ✅ Complete |
| Phase 3 | Scholarship Loader | ✅ Complete |
| Phase 4 | Feature Matcher | ✅ Complete |
| Phase 5 | Hard Pre-Filters | ✅ Complete |
| Phase 6 | M/T Scorer | ✅ Complete |
| Phase 7 | API Routes | ✅ Complete |
| Phase 8 | Testing | ✅ Complete |
| Phase 9 | Documentation | ✅ Complete |
| Phase 10 | Frontend/UI | ✅ Complete |

**Tests:** 107 passing, 0 failing.

---

## Running the Frontend App

The MVP frontend is located in the `frontend/` directory.

To install and run:
```bash
cd frontend
npm install
npm run dev
```

The frontend will run at [http://localhost:3000](http://localhost:3000). Ensure the FastAPI backend is running at [http://localhost:8000](http://localhost:8000).


---

## What the backend currently supports

- `POST /profile/` — create a student profile (30+ fields, Pydantic v2 validated)
- `GET /profile/{id}` — retrieve a stored profile
- `PATCH /profile/{id}` — update profile fields
- `DELETE /profile/{id}` — delete a profile
- `GET /profile/{id}/completeness` — return profile completeness percentage
- `POST /score/all` — score all scholarships against a profile (pre-filtered, ranked, max 20)
- `POST /score/single` — score one specific scholarship against a profile
- `GET /score/cached/{id}` — retrieve last cached scoring result
- `GET /health` — system health check

---

## What is intentionally out of scope during MVP

| Out of Scope | Reason |
|---|---|
| Frontend / UI | Phase 10+ |
| User authentication | No multi-user accounts yet |
| PostgreSQL persistence | In-memory store is sufficient for MVP |
| Redis caching | Not needed at MVP scale |
| ML ranking (LightGBM) | No training data exists yet |
| Vector search (Pinecone) | No embeddings generated yet |
| Web scraping | Static JSON data only |
| Agent orchestration (LangGraph, CrewAI) | Single-agent MVP |
| Analytics dashboard | No users yet |
| Email / notifications | Post-MVP |

See [docs/PRD.md](docs/PRD.md) § 5 for the full non-goals list.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Ved4126/scholarbridge.git
cd scholarbridge

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables template
cp .env.example .env

# 5. Run the server
python3 -m uvicorn backend.app.main:app --reload

# 6. Open Swagger UI
open http://127.0.0.1:8000/docs

# 7. Run tests
python3 -m pytest tests/ -v
```

---

## Documentation

| Document | Purpose |
|---|---|
| [docs/SETUP.md](docs/SETUP.md) | Clone, install, run, add scholarship records, troubleshoot |
| [docs/API.md](docs/API.md) | All 9 endpoints — request bodies, curl examples, response schemas |
| [docs/PRD.md](docs/PRD.md) | Product requirements, user stories, success criteria |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, folder structure, data flow |
| [docs/PLAN.md](docs/PLAN.md) | Phase-by-phase execution plan |
| [docs/NEXT_PHASES.md](docs/NEXT_PHASES.md) | Roadmap for future development phases beyond MVP frontend |
| [docs/SCHOLARSHIP_DATA_GUIDE.md](docs/SCHOLARSHIP_DATA_GUIDE.md) | Standards, criteria, and guidelines for authoring real scholarship records |
| [docs/AI_RULES.md](docs/AI_RULES.md) | AI governance rules — read before any code change |



---

## Development Rules Summary

1. **Read first.** Before any code change, read `docs/AI_RULES.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/PLAN.md`.
2. **One phase at a time.** Do not skip phases or start the next phase without explicit approval.
3. **No business logic in routes.** `api/` routers delegate all logic to `scorer/` and `agents/`.
4. **No rewriting working code.** Minimal-invasive changes only.
5. **Tests must pass.** `python3 -m pytest tests/ -v` must show 0 failures before any commit.
6. **No prohibited systems.** ML, PostgreSQL, Redis, LangGraph, and web scraping are banned until MVP is declared complete.

See [docs/AI_RULES.md](docs/AI_RULES.md) for the full list.

---

## Test Command

```bash
python3 -m pytest tests/ -v
```

Expected: **107 passed, 0 failed**

---

## License

MIT — see [LICENSE](LICENSE).
