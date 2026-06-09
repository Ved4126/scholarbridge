# ARCHITECTURE.md — ScholarBridge System Architecture

> **Document Type:** Technical Architecture Reference
> **Enforcement Level:** Mandatory — No contributor may reorganize files, rename modules, or add
> new directories without first updating this document and obtaining team approval.
> **Repository:** https://github.com/Ved4126/scholarbridge
> **Last Updated:** June 09, 2026

---

## 1. Architecture Philosophy

**Build simple first. Working backend before advanced AI.**

The ScholarBridge architecture is designed around one overriding constraint: **the MVP must work
before any ML, vector search, or agent orchestration is added**. This is not a limitation — it is the
correct sequencing for a system where real user data does not yet exist.

### Core Principles

1. **Rule-based before ML** — The M/T scoring engine is deterministic and rule-based. LightGBM
   ranking comes after 500 annotated training pairs exist. RLHF comes after 2,000+ real sessions.
2. **Static data before live scraping** — MVP reads from JSON files. PostgreSQL, Pinecone, and
   Playwright are post-MVP infrastructure.
3. **One agent at a time** — During MVP, agents are stateless Python functions. LangGraph and
   CrewAI orchestration are introduced only when multiple real agents need to coordinate.
4. **Separation of concerns** — API routes never contain business logic. Business logic never touches
   the HTTP layer. This makes testing trivial and ML replacement straightforward.

---

## 2. MVP Data Flow

```
Student Profile Submission
        │
        ▼
[profile_router.py]  ← POST /profile
        │
        ▼
[profile_agent.py]   ← Pydantic v2 validation, completeness scoring, to_feature_vector()
        │
        ▼
[scorer_router.py]   ← POST /score/all
        │
        ▼
[load_scholarships.py] ← Loads all JSON files from data/scholarships/, validates against schema.json
        │
        ▼
[scorer.py]          ← Hard pre-filters (deadline, citizenship, degree, visa)
        │             (scholarships failing pre-filters are dropped)
        │             NOTE: age is NOT a pre-filter — it is a range feature in the manifest
        ▼
[feature_matcher.py] ← For each scholarship: evaluate each feature in feature_manifest
        │               enum | threshold | boolean | output | range
        │               (score_test is deferred — skip with warning if encountered)
        ▼
[scorer.py]          ← Score = (M / T) × 100, build gap_analysis, action_checklist
        │
        ▼
Ranked Results Response  ← Sorted by score desc, filtered to ≥ 40%, max 20 results
```

---

## 3. Folder Structure

This is the exact canonical folder structure. No new top-level directories may be added during MVP without a team decision and an update to this document.

```
scholarbridge/
├── backend/
│   └── app/
│       ├── agents/
│       │   └── profile_agent.py        # Pydantic models, to_feature_vector(), completeness score
│       ├── api/
│       │   ├── profile_router.py       # FastAPI router: profile CRUD + completeness
│       │   └── scorer_router.py        # FastAPI router: score/all, score/single, score/cached
│       ├── db/
│       │   ├── database.py             # In-memory profile store (MVP) — DB connection post-MVP
│       │   └── models.py               # SQLAlchemy model stubs (post-MVP ready)
│       ├── scorer/
│       │   ├── feature_matcher.py      # All 5 feature type matchers
│       │   ├── scorer.py               # score_one(), score_all(), pre-filter logic
│       │   └── models.py               # ScoringResult, FeatureMatchDetail, ScholarshipResult
│       └── main.py                     # FastAPI app entry, router registration, health check
│
├── data/
│   ├── schema.json                     # Canonical scholarship record schema — all records validated against this
│   └── scholarships/
│       ├── us/                         # US-based scholarships
│       ├── india/                      # India home-country scholarships
│       ├── china/                      # China home-country scholarships
│       ├── south_korea/                # South Korea home-country scholarships
│       ├── nigeria/                    # Nigeria home-country scholarships
│       └── international/              # UN, Fulbright, World Bank, DAAD, Chevening
│
├── scripts/
│   └── load_scholarships.py            # CLI script to validate and preview scholarship data
│
├── tests/
│   ├── test_profile_agent.py           # Unit tests for profile validation and feature vector
│   ├── test_feature_matcher.py         # Unit tests for all 5 feature types
│   ├── test_scorer.py                  # Unit tests for score_one(), score_all(), pre-filters
│   ├── test_profile_router.py          # Integration tests for profile API endpoints
│   └── test_scorer_router.py           # Integration tests for scorer API endpoints
│
├── docs/
│   ├── AI_RULES.md                     # AI governance rules (this document's partner)
│   ├── PRD.md                          # Product requirements
│   ├── ARCHITECTURE.md                 # This file
│   └── PLAN.md                         # Phase-by-phase execution plan
│
├── .env.example                        # API key template (committed — no real values)
├── .gitignore                          # Python, Node, .env, OS files
└── requirements.txt                    # Python dependencies
```

---

## 4. File Responsibilities

### `backend/app/main.py`
- Instantiates the FastAPI application
- Registers `profile_router` and `scorer_router` with their respective prefixes
- Exposes `GET /health` endpoint (returns `{"status": "ok", "version": "0.1.0"}`)
- Configures CORS middleware for local development
- Contains no business logic

### `backend/app/agents/profile_agent.py`
- Defines the `StudentProfile` Pydantic v2 model with all 30+ fields
- Implements `to_feature_vector() -> dict[str, Any]` — converts profile to a flat dict used by the feature matcher
- Implements `completeness_score(profile: StudentProfile) -> float` — returns percentage of non-null fields
- Contains no FastAPI route handlers
- Contains no database access

### `backend/app/api/profile_router.py`
- FastAPI `APIRouter` with prefix `/profile`
- Five endpoints:
  - `POST /` — validates and stores a student profile
  - `GET /{profile_id}` — retrieves a stored profile by ID
  - `PATCH /{profile_id}` — updates specific fields of a stored profile
  - `DELETE /{profile_id}` — removes a profile from the store
  - `GET /{profile_id}/completeness` — returns completeness score for a stored profile
- Delegates all logic to `profile_agent.py` and `database.py`
- Contains no business logic

### `backend/app/api/scorer_router.py`
- FastAPI `APIRouter` with prefix `/score`
- Three endpoints:
  - `POST /all` — accepts a profile payload, scores all loaded scholarships, returns ranked results
  - `POST /single` — accepts a profile + scholarship ID, returns scoring result for that pair only
  - `GET /cached/{profile_id}` — returns the last scoring result for a stored profile (if available)
- Delegates all logic to `scorer.py` and `load_scholarships.py`
- Contains no business logic

### `backend/app/scorer/feature_matcher.py`
- Implements `match_feature(feature: FeatureSpec, profile_vector: dict) -> int` — returns 1 or 0
- Handles all five MVP feature types: `enum`, `threshold`, `boolean`, `output`, `range`
- `score_test` is **deferred** — if encountered, log a warning and return 0 (skip safely)
- Raises `ValueError` on any other unknown feature type (never silently passes)
- Contains no FastAPI, database, or file I/O code

### `backend/app/scorer/scorer.py`
- Implements `apply_hard_filters(profile: StudentProfile, scholarship: Scholarship) -> bool`
  — returns True if scholarship passes all pre-filters (deadline, citizenship, degree, visa, age)
- Implements `score_one(profile: StudentProfile, scholarship: Scholarship) -> ScoringResult`
  — applies feature matcher to all features, computes M/T score, builds gap_analysis, action_checklist
- Implements `score_all(profile: StudentProfile, scholarships: list[Scholarship]) -> list[ScoringResult]`
  — filters via `apply_hard_filters`, scores each, sorts by score desc, returns top 20 with score ≥ 40%
- Contains no FastAPI or file I/O code

### `backend/app/scorer/models.py`
- `FeatureSpec` — Pydantic model for a single feature in a scholarship's feature_manifest
- `FeatureMatchDetail` — stores field name, requirement, student_value, and matched (bool) for gap analysis
- `ScoringResult` — stores scholarship_id, name, org_name, score, match_label, deadline, source_url, gap_analysis, action_checklist
- `ScholarshipResult` — top-level response wrapper for the `/score/all` endpoint

### `backend/app/db/database.py`
- MVP: In-memory Python dict storing `profile_id → StudentProfile`
- Implements `save_profile()`, `get_profile()`, `update_profile()`, `delete_profile()`
- Post-MVP: replaced with async SQLAlchemy sessions (stubs prepared in `models.py`)
- Contains no FastAPI or business logic

### `backend/app/db/models.py`
- SQLAlchemy `StudentProfileORM` model (schema-ready for post-MVP PostgreSQL migration)
- Not used during MVP — exists so the migration requires no schema design work

### `scripts/load_scholarships.py`
- CLI script: `python scripts/load_scholarships.py --dir data/scholarships/`
- Loads all `.json` files from the target directory tree
- Validates each against `data/schema.json`
- Prints a summary: total loaded, total rejected, list of rejected file paths with error reasons
- Used by developers during development; also called programmatically by `scorer_router.py`

---

## 5. Scholarship Schema

Every scholarship record must conform to the following structure (enforced by `data/schema.json`):

```json
{
  "id": "string (UUID or slug — unique across all records)",
  "name": "string (full scholarship name)",
  "org_name": "string (awarding organization name)",
  "country": "string (ISO 3166-1 alpha-2, e.g. 'IN', 'US', 'NG')",
  "source_url": "string (canonical URL — must be https://)",
  "last_verified": "string (ISO 8601 date, e.g. '2026-06-01')",
  "deadline": "string (ISO 8601 date, e.g. '2026-12-01')",
  "accepted_nationalities": ["IN", "PK", "BD"],
  "accepted_degree_levels": ["masters", "phd"],
  "accepted_visa_types": ["F-1", "J-1"],
  "age_range": {"min": 18, "max": 35},
  "feature_manifest": [
    {
      "type": "enum | threshold | boolean | output | range | score_test",
      "field": "string (maps to a field in StudentProfile.to_feature_vector())",
      "label": "string (human-readable name shown in gap analysis)",
      "operator": "gte | lte | eq | in (for threshold and enum types)",
      "values": ["list of accepted values (for enum type)"],
      "minimum": "number (for threshold and range types)",
      "maximum": "number (for range type)",
      "description": "string (shown in action_checklist for output type)"
    }
  ]
}
```

**Example — Aga Khan Foundation Scholarship (first real record):**

```json
{
  "id": "aga-khan-foundation-international-scholarship",
  "name": "Aga Khan Foundation International Scholarship",
  "org_name": "Aga Khan Foundation",
  "country": "IN",
  "source_url": "https://www.akdn.org/our-agencies/aga-khan-foundation/international-scholarships",
  "last_verified": "2026-06-09",
  "deadline": "2026-11-01",
  "accepted_nationalities": ["IN", "PK", "BD", "KE", "TZ", "UG", "MZ", "SY", "EG"],
  "accepted_degree_levels": ["masters", "phd"],
  "accepted_visa_types": ["F-1", "J-1"],
  "age_range": {"min": 18, "max": 30},
  "feature_manifest": [
    {"type": "enum", "field": "nationality", "label": "Nationality", "operator": "in",
     "values": ["IN", "PK", "BD", "KE", "TZ", "UG", "MZ", "SY", "EG"]},
    {"type": "enum", "field": "degree_level", "label": "Degree Level", "operator": "in",
     "values": ["masters", "phd"]},
    {"type": "threshold", "field": "gpa", "label": "GPA", "operator": "gte", "minimum": 3.5},
    {"type": "boolean", "field": "demonstrated_financial_need", "label": "Demonstrated Financial Need"},
    {"type": "range", "field": "age", "label": "Age", "minimum": 18, "maximum": 30},
    {"type": "output", "field": "personal_statement", "label": "Personal Statement",
     "description": "Write a personal statement (500–800 words) describing your academic goals."},
    {"type": "output", "field": "letters_of_recommendation", "label": "Letters of Recommendation",
     "description": "Obtain 2 letters of recommendation from academic supervisors."}
  ]
}
```

---

## 6. Feature Manifest Design

The feature manifest is the machine-readable eligibility specification for a scholarship. It is the bridge
between the scholarship's requirements and the M/T scoring formula.

| Feature Type | Matching Logic | Contributes to M | Contributes to T |
|---|---|---|---|
| `enum` | `student[field] in feature.values` | Yes (if matched) | Yes (always) |
| `threshold` | `student[field] >= feature.minimum` | Yes (if matched) | Yes (always) |
| `boolean` | `student[field] == True` | Yes (if matched) | Yes (always) |
| `output` | Always 0 — cannot be auto-evaluated | **Never** | Yes (always) |
| `range` | `feature.minimum <= student[field] <= feature.maximum` | Yes (if matched) | Yes (always) |
| `score_test` | **Deferred (MVP)** — skip with warning; treat as if absent from manifest | No | No |

> **Age note:** Age requirements are expressed as a `range`-type feature in the feature manifest (e.g., `{"type": "range", "field": "age", "minimum": 18, "maximum": 30}`). If the student's `age` field is `None`, the feature returns 0 (unmatched) and appears in `gap_analysis`. Age is **never** a hard pre-filter.

**Design Constraints:**
- Every feature type must be implemented in `feature_matcher.py`
- Unknown feature types must raise `ValueError` — never silently return 0
- `output`-type features are surfaced in `action_checklist` with their `description` field
- Unmatched non-output features are surfaced in `gap_analysis`

---

## 7. Scoring Architecture

### Pre-Filter Stage (before scoring)

```python
def apply_hard_filters(profile: StudentProfile, scholarship: Scholarship) -> bool:
    """Returns True if scholarship passes ALL hard filters, False otherwise.
    
    NOTE: Age is NOT a hard filter. Age is handled as a range feature in the
    feature manifest. Missing age reduces score; it does not block the scholarship.
    """
    # Filter 1: Deadline
    if scholarship.deadline <= date.today():
        return False
    # Filter 2: Citizenship/Nationality
    if scholarship.accepted_nationalities and profile.nationality not in scholarship.accepted_nationalities:
        return False
    # Filter 3: Degree Level
    if scholarship.accepted_degree_levels and profile.degree_level not in scholarship.accepted_degree_levels:
        return False
    # Filter 4: Visa Type
    if scholarship.accepted_visa_types and profile.visa_type not in scholarship.accepted_visa_types:
        return False
    return True
```

### Scoring Stage (after pre-filters pass)

```python
def score_one(profile: StudentProfile, scholarship: Scholarship) -> ScoringResult:
    M = 0
    T = len(scholarship.feature_manifest)
    gap_analysis = []
    action_checklist = []

    feature_vector = profile.to_feature_vector()

    for feature in scholarship.feature_manifest:
        matched = match_feature(feature, feature_vector)
        if feature.type == "output":
            action_checklist.append(feature.description)
        elif matched == 0:
            gap_analysis.append(FeatureMatchDetail(
                field=feature.field,
                label=feature.label,
                requirement=feature.operator_summary,
                student_value=feature_vector.get(feature.field)
            ))
        M += matched  # 0 for output type, 0 or 1 for all others

    score = round((M / T) * 100, 1) if T > 0 else 0.0
    match_label = compute_match_label(score)

    return ScoringResult(
        scholarship_id=scholarship.id,
        name=scholarship.name,
        org_name=scholarship.org_name,
        score=score,
        match_label=match_label,
        deadline=scholarship.deadline,
        source_url=scholarship.source_url,
        gap_analysis=gap_analysis,
        action_checklist=action_checklist
    )
```

### Score Band Assignment

```python
def compute_match_label(score: float) -> str:
    if score >= 90:
        return "Strong Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 40:
        return "Possible Match"
    else:
        return "Below Threshold"
```

---

## 8. API Architecture

All endpoints are defined here. Adding an endpoint that is not in this table requires updating this document first.

### Profile Endpoints — prefix: `/profile`

| Method | Path | Handler | Description |
|---|---|---|---|
| `POST` | `/profile` | `profile_router.create_profile` | Submit a new student profile; returns `profile_id` |
| `GET` | `/profile/{profile_id}` | `profile_router.get_profile` | Retrieve a profile by ID |
| `PATCH` | `/profile/{profile_id}` | `profile_router.update_profile` | Update specific profile fields |
| `DELETE` | `/profile/{profile_id}` | `profile_router.delete_profile` | Delete a profile |
| `GET` | `/profile/{profile_id}/completeness` | `profile_router.get_completeness` | Return completeness % |

### Scorer Endpoints — prefix: `/score`

| Method | Path | Handler | Description |
|---|---|---|---|
| `POST` | `/score/all` | `scorer_router.score_all` | Score all scholarships against submitted profile |
| `POST` | `/score/single` | `scorer_router.score_single` | Score one scholarship against a profile |
| `GET` | `/score/cached/{profile_id}` | `scorer_router.get_cached` | Retrieve last score result for a stored profile |

### System Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok", "version": "0.1.0"}` |

### Response Schemas

**`POST /profile` response:**
```json
{"profile_id": "uuid-string", "completeness": 82.5, "message": "Profile created successfully"}
```

**`POST /score/all` response:**
```json
{
  "profile_id": "uuid-string",
  "total_evaluated": 48,
  "total_returned": 12,
  "results": [
    {
      "scholarship_id": "aga-khan-foundation-international-scholarship",
      "name": "Aga Khan Foundation International Scholarship",
      "org_name": "Aga Khan Foundation",
      "score": 78.6,
      "match_label": "Good Match",
      "deadline": "2026-11-01",
      "source_url": "https://www.akdn.org/...",
      "gap_analysis": [{"field": "gpa", "label": "GPA", "requirement": ">= 3.5", "student_value": 3.3}],
      "action_checklist": ["Write a personal statement (500–800 words)", "Obtain 2 letters of recommendation"]
    }
  ]
}
```

---

## 9. Deduplication Strategy (Data Layer)

When the same scholarship appears from multiple sources, the composite deduplication key is:

```
key = normalize(org_name) + normalize(scholarship_name) + award_year
```

Where `normalize()` means: lowercase → strip punctuation → collapse whitespace → remove filler words (the, a, an, for, of).

This is enforced in `scripts/load_scholarships.py` when building the scholarship index at load time. Duplicate records log a warning and the **later-discovered record is discarded** (first write wins during MVP).

---

## 10. Future Architecture (Post-MVP Only)

The following components are designed and documented here but **must not be implemented during MVP**. Any code introducing these systems before MVP completion is a rules violation per `AI_RULES.md`.

| System | Purpose | Trigger |
|---|---|---|
| **PostgreSQL** | Persistent profile and scholarship storage | After MVP is working end-to-end |
| **Redis** | Online feature caching for scorer hot path | After 100+ concurrent users |
| **Pinecone / Weaviate** | Vector similarity search for Layer 2 retrieval | After BGE-M3 embeddings are generated |
| **BGE-M3 embeddings** | Multilingual dense retrieval | After 500 scholarships curated |
| **LightGBM-Ranker** | ML-based ranking (Learning-to-Rank) | After 500 annotated (profile, scholarship) pairs |
| **LambdaRank** | Neural ranking upgrade | After 5,000+ real sessions |
| **RLHF feedback loop** | Reward signal from user actions | After 2,000+ real sessions |
| **LangGraph / CrewAI** | Multi-agent orchestration | After multiple agents need to coordinate |
| **Playwright / Scrapy** | Live web scraping (Layer 2) | After MVP + data infrastructure is stable |
| **Next.js frontend** | Student-facing UI | After backend API is stable and tested |
| **Auth0 / Clerk** | User authentication | When multi-user accounts are needed |
| **GitHub Actions CI** | Automated testing on push | After MVP is working |
| **Docker** | Containerized deployment | When deploying to Render / Railway / AWS |

**These systems must remain out of scope until the MVP Definition of Done in PLAN.md is fully met.**

---

*Architecture document updated June 09, 2026 — Governance update v1.1*
*Source: ARCHITECTURE.md.pdf instructions + ScholarBridge_Chat_Summary.pdf*
