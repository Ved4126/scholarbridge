# PLAN.md — ScholarBridge Project Execution Plan

> **Document Type:** Technical Program Management — Phase-Gated Execution Plan
> **Enforcement Level:** Mandatory — AI agents must work exactly one phase at a time.
> No phase skipping. No jumping ahead. Explicit STOP after each phase.
> **Repository:** https://github.com/Ved4126/scholarbridge
> **Last Updated:** June 09, 2026

---

## Execution Rules

Every AI agent and every contributor must follow these rules without exception:

1. **Read before coding.** Before writing any code, read `AI_RULES.md`, `PRD.md`, `ARCHITECTURE.md`,
   and this file in full.
2. **One phase at a time.** Identify the current incomplete phase. Work only on that phase.
3. **No phase skipping.** Phases must complete in order: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9.
4. **No jumping ahead.** Do not build systems that belong to a later phase.
5. **STOP after each phase.** At the end of every phase, the agent stops and waits for explicit human
   approval before proceeding.
6. **Mandatory phase report.** Each phase completion must include:
   - **Current Phase:** (number and name)
   - **Repository Findings:** (what files exist, what is missing)
   - **Files Changed:** (list of created/modified files)
   - **Implementation:** (summary of what was built)
   - **Verification:** (how the work was verified — curl output, test output, etc.)
   - **Tests:** (which tests pass, which fail)
   - **Blockers:** (any issues requiring human input)
   - **Next Recommended Phase:** (state the next phase number and name only)

---

## Phase 0 — Repository Inspection

**Purpose:** Understand the current state of the repository before writing any code.

**Deliverables:**
- [ ] List of all existing files and their paths
- [ ] List of missing files that must exist before coding begins
- [ ] Identification of any files that conflict with ARCHITECTURE.md structure
- [ ] Current status summary

**Success Criteria:**
- Repository has been fully inspected
- Missing documentation files have been identified
- ARCHITECTURE.md folder structure has been confirmed or discrepancies noted

**Prohibited During This Phase:**
- Writing any application code
- Installing any packages
- Running any services

**→ STOP. Wait for approval before proceeding to Phase 1.**

---

## Phase 1 — FastAPI Application Setup

**Purpose:** Create a running FastAPI application with a health check endpoint.

**Deliverables:**
- [ ] `backend/app/main.py` — FastAPI app with health check endpoint
- [ ] `requirements.txt` — all Python dependencies listed (see below)
- [ ] Application runs with `uvicorn backend.app.main:app --reload`
- [ ] `GET /health` returns `{"status": "ok", "version": "0.1.0"}`

**Required Dependencies (minimum for Phase 1):**
```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic[email]>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
httpx>=0.27.0
```

**Files to Create:**
- `backend/app/main.py` — FastAPI app instantiation, CORS, router registration stubs, health endpoint
- `backend/__init__.py`, `backend/app/__init__.py` (empty init files for package structure)

**Verification:**
```bash
uvicorn backend.app.main:app --reload
curl http://localhost:8000/health
# Expected: {"status": "ok", "version": "0.1.0"}
curl http://localhost:8000/docs
# Expected: Swagger UI loads
```

**→ STOP. Wait for approval before proceeding to Phase 2.**

---

## Phase 2 — Student Profile Model

**Purpose:** Implement the complete Pydantic v2 student profile model with validation and feature vector conversion.

**Deliverables:**
- [ ] `backend/app/agents/profile_agent.py` — `StudentProfile` Pydantic v2 model (30+ fields)
- [ ] `StudentProfile.to_feature_vector()` method — returns flat `dict[str, Any]`
- [ ] `completeness_score(profile: StudentProfile) -> float` — returns 0.0–100.0
- [ ] `tests/test_profile_agent.py` — unit tests for model validation and feature vector
- [ ] All tests pass

**Profile Fields Required (30+ total across 6 categories):**

_Category 1: Identity_
- `name: str`
- `email: EmailStr`
- `nationality: str` (ISO 3166-1 alpha-2, e.g. `"IN"`)
- `country_of_origin: str`
- `home_country: str`
- `age: Optional[int]`

_Category 2: Academic_
- `degree_level: Literal["undergraduate", "masters", "phd", "postdoc"]`
- `field_of_study: str`
- `gpa: float` (must be between 0.0 and 4.0, inclusive)
- `institution_name: str`
- `enrollment_status: Literal["full-time", "part-time"]`
- `graduation_year: Optional[int]`

_Category 3: Visa & Immigration_
- `visa_type: Literal["F-1", "J-1", "other"]`
- `visa_status: Literal["active", "expired"]`
- `opt_eligible: Optional[bool]`
- `cpt_eligible: Optional[bool]`

_Category 4: Financial_
- `demonstrated_financial_need: bool`
- `household_income_range: Optional[Literal["<30k", "30k-60k", "60k-90k", "90k-120k", ">120k"]]`
- `dependent_count: Optional[int]`

_Category 5: Achievements_
- `published_papers_count: int` (default 0)
- `awards_and_honors: list[str]` (default [])
- `leadership_roles: list[str]` (default [])
- `deans_list: bool` (default False)
- `research_experience: bool` (default False)
- `has_stem_degree: bool` (default False)

_Category 6: Preferences_
- `preferred_min_award_amount: Optional[float]`
- `open_to_essay_required: bool` (default True)
- `open_to_interview_required: bool` (default True)
- `target_countries: list[str]` (default ["US"])

**Validation Rules:**
- `gpa` must be >= 0.0 and <= 4.0
- `nationality` must be a 2-character uppercase string
- `age` if provided must be >= 15 and <= 80
- `email` must be a valid email address
- All `Literal` fields validated by Pydantic automatically

**Tests to Write:**
- Valid profile creates successfully
- GPA out of range (e.g., 5.0) raises `ValidationError`
- Invalid degree level raises `ValidationError`
- `to_feature_vector()` returns correct keys and values for a known profile
- `completeness_score()` returns 100.0 for a fully-filled profile
- `completeness_score()` returns correct partial score when optional fields are None

**→ STOP. Wait for approval before proceeding to Phase 3.**

---

## Phase 3 — Scholarship Loader

**Purpose:** Implement the scholarship data loader that reads JSON files, validates them against `data/schema.json`, and returns structured Scholarship objects.

**Deliverables:**
- [ ] `data/schema.json` — canonical scholarship record schema (see ARCHITECTURE.md Section 5)
- [ ] `backend/app/scorer/models.py` updated with `Scholarship`, `FeatureSpec` Pydantic models
- [ ] `scripts/load_scholarships.py` — CLI + importable function `load_scholarships(directory: Path) -> list[Scholarship]`
- [ ] At least **1 real scholarship record** in `data/scholarships/` to verify end-to-end loading. Recommended: aim for 10–50 records as seed data — data volume is not a blocker.
- [ ] `tests/test_scholarship_loader.py` — unit tests for loader behavior
- [ ] All tests pass

**Loader Behavior Requirements:**
- Load all `.json` files recursively from the target directory
- Validate each file against `Scholarship` Pydantic model
- Log a warning for each invalid file: `[WARN] Rejected {filepath}: {error_message}`
- Never raise an unhandled exception on bad data
- Return only valid scholarship records
- Check for duplicate `id` fields — log a warning and skip the duplicate

**Tests to Write:**
- Valid scholarship file loads successfully
- Missing required field (e.g., no `source_url`) is rejected with a warning
- Expired scholarship (deadline in the past) loads but is later filtered by pre-filters (not at load time)
- Duplicate `id` is detected and the second record is skipped
- Empty directory returns an empty list without error
- At least one real scholarship record (e.g., Aga Khan Foundation) loads successfully

**→ STOP. Wait for approval before proceeding to Phase 4.**

---

## Phase 4 — Feature Matcher

**Purpose:** Implement deterministic feature-by-feature matching between a student profile vector and a scholarship's feature manifest.

**Deliverables:**
- [ ] `backend/app/scorer/feature_matcher.py` — implements `match_feature()` for all **5 MVP types**
- [ ] `tests/test_feature_matcher.py` — comprehensive unit tests
- [ ] All tests pass

**`match_feature()` signature:**
```python
def match_feature(feature: FeatureSpec, profile_vector: dict[str, Any]) -> int:
    """Returns 1 if matched, 0 if not. Always returns 0 for output type."""
```

**Feature Type Implementations (MVP — 5 types only):**

| Type | Match Logic |
|---|---|
| `enum` | `profile_vector[feature.field] in feature.values` |
| `threshold` | `profile_vector[feature.field] >= feature.minimum` |
| `boolean` | `bool(profile_vector[feature.field]) == True` |
| `output` | Always `0` — contributes to T, never to M |
| `range` | `feature.minimum <= profile_vector[feature.field] <= feature.maximum` |

**Deferred Feature Type:**

| Type | Status | Action |
|---|---|---|
| `score_test` | Deferred — do NOT implement | Log a warning and return 0 if encountered |

**Edge Cases to Handle:**
- Field missing from profile vector → return 0 (not an error)
- Field value is `None` in profile vector → return 0 (not an error)
- `score_test` encountered → log `[WARN] score_test feature skipped (deferred): {feature.field}` and return 0, subtract 1 from T
- Unknown feature type (anything other than the 5 MVP types and `score_test`) → raise `ValueError(f"Unknown feature type: {feature.type}")`
- `enum` comparison is case-insensitive for nationality codes

**Tests to Write (minimum 20 tests — 4 per MVP feature type):**
- `enum`: match when value is in list
- `enum`: no match when value is not in list
- `enum`: missing field returns 0
- `enum`: case-insensitive nationality match
- `threshold`: match when value meets minimum
- `threshold`: no match when value is below minimum
- `threshold`: exact boundary (value == minimum) returns 1
- `threshold`: missing field returns 0
- `boolean`: True profile field returns 1
- `boolean`: False profile field returns 0
- `boolean`: missing field returns 0
- `output`: always returns 0 regardless of profile
- `range`: value within bounds returns 1
- `range`: value at lower bound returns 1
- `range`: value at upper bound returns 1
- `range`: value below lower bound returns 0
- `range`: value above upper bound returns 0
- `range`: None field (e.g., missing age) returns 0
- `score_test`: logs warning and returns 0 — does not raise
- Unknown type raises `ValueError`

**→ STOP. Wait for approval before proceeding to Phase 5.**

---

## Phase 5 — Hard Pre-Filters

**Purpose:** Implement the four hard eligibility pre-filters that run before scoring. A scholarship that fails any pre-filter is excluded entirely from results.

> **Age is NOT a hard pre-filter.** Age requirements are expressed as a `range`-type feature in the feature manifest and are evaluated by the feature matcher. A missing `age` field reduces the score naturally — it does not block the scholarship.

**Deliverables:**
- [ ] `backend/app/scorer/scorer.py` — `apply_hard_filters()` function
- [ ] `tests/test_hard_filters.py` — unit tests for all 4 hard filter types
- [ ] All tests pass

**`apply_hard_filters()` signature:**
```python
def apply_hard_filters(profile: StudentProfile, scholarship: Scholarship) -> bool:
    """
    Returns True if scholarship passes ALL hard filters.
    Returns False if scholarship fails ANY hard filter.
    Age is NOT checked here — it is a feature manifest entry evaluated by the scorer.
    """
```

**Hard Filter Specifications (4 filters):**

| Filter | Rule | Failure Condition |
|---|---|---|
| `deadline` | `scholarship.deadline > date.today()` | Deadline is today or in the past |
| `citizenship` | `scholarship.accepted_nationalities` is empty OR `profile.nationality in scholarship.accepted_nationalities` | Student nationality not in accepted list (when list is non-empty) |
| `degree` | `scholarship.accepted_degree_levels` is empty OR `profile.degree_level in scholarship.accepted_degree_levels` | Student degree not in accepted levels (when list is non-empty) |
| `visa` | `scholarship.accepted_visa_types` is empty OR `profile.visa_type in scholarship.accepted_visa_types` | Student visa type not in accepted types (when list is non-empty) |

**Tests to Write:**
- Expired scholarship (deadline yesterday) returns False
- Scholarship expiring today returns False
- Scholarship deadline tomorrow returns True (passes deadline filter)
- Nationality mismatch returns False
- Nationality match returns True
- Empty accepted_nationalities list (open to all) returns True for any nationality
- Degree level mismatch returns False
- Degree level match returns True
- Visa type mismatch returns False
- Visa type match returns True
- Scholarship passes all 4 filters simultaneously → True
- Scholarship fails 1 of 4 filters → False
- Scholarship with `age_range` field is NOT blocked by hard filter — confirm it reaches the scorer (age handled in feature manifest)

**→ STOP. Wait for approval before proceeding to Phase 6.**

---

## Phase 6 — M/T Scorer

**Purpose:** Implement the full scoring pipeline: `score_one()` and `score_all()` with gap analysis, action checklist generation, and ranked output.

**Deliverables:**
- [ ] `backend/app/scorer/scorer.py` — `score_one()` and `score_all()` functions
- [ ] `backend/app/scorer/models.py` — `ScoringResult`, `FeatureMatchDetail` Pydantic models
- [ ] `tests/test_scorer.py` — unit tests for full scoring pipeline
- [ ] All tests pass

**`score_one()` behavior:**
- Call `feature_matcher.match_feature()` for each feature in `feature_manifest`
- Accumulate M (sum of matches, excluding output type)
- T = total number of features in manifest
- Score = `round((M / T) * 100, 1)` — 0.0 if T == 0
- Build `gap_analysis`: list of `FeatureMatchDetail` for unmatched non-output features
- Build `action_checklist`: list of `description` strings from all `output`-type features
- Assign `match_label` via `compute_match_label(score)`

**`score_all()` behavior:**
- Accept `profile: StudentProfile` and `scholarships: list[Scholarship]`
- For each scholarship, call `apply_hard_filters()` — skip if returns False
- For passing scholarships, call `score_one()`
- Filter out results with `score < 40.0`
- Sort remaining results by `score` descending
- Return top 20 results

**`compute_match_label()` behavior:**
- score >= 90.0 → `"Strong Match"`
- score >= 70.0 → `"Good Match"`
- score >= 40.0 → `"Possible Match"`
- score < 40.0 → `"Below Threshold"` (these are filtered out by `score_all` anyway)

**Tests to Write:**
- Known profile + known scholarship → verify exact score
- All features matched → score = 100.0
- No features matched (all output type) → score = 0.0
- Scholarship with only output features → score = 0.0, action_checklist populated, gap_analysis empty
- Gap analysis contains exactly the unmatched non-output features
- Action checklist contains exactly the output-type features
- `score_all` applies pre-filters correctly (expired scholarship excluded)
- `score_all` returns results sorted by score descending
- `score_all` excludes results below 40%
- `score_all` returns maximum 20 results even if more qualify
- T=0 edge case returns score 0.0 without division-by-zero error

**→ STOP. Wait for approval before proceeding to Phase 7.**

---

## Phase 7 — API Routes

**Purpose:** Expose the profile and scorer functionality through FastAPI endpoints.

**Deliverables:**
- [ ] `backend/app/api/profile_router.py` — 5 profile endpoints
- [ ] `backend/app/api/scorer_router.py` — 3 scorer endpoints
- [ ] `backend/app/db/database.py` — in-memory profile store
- [ ] `backend/app/main.py` — updated to register both routers
- [ ] `tests/test_profile_router.py` — integration tests using `httpx.AsyncClient`
- [ ] `tests/test_scorer_router.py` — integration tests
- [ ] All tests pass

**Profile Router Endpoints (all must be implemented):**
- `POST /profile` — body: `StudentProfile` JSON, returns: `{profile_id, completeness, message}`
- `GET /profile/{profile_id}` — returns: full profile JSON or 404
- `PATCH /profile/{profile_id}` — body: partial profile JSON, returns: updated profile
- `DELETE /profile/{profile_id}` — returns: `{message: "Profile deleted"}` or 404
- `GET /profile/{profile_id}/completeness` — returns: `{profile_id, completeness}`

**Scorer Router Endpoints (all must be implemented):**
- `POST /score/all` — body: `StudentProfile` JSON, returns: full ranked results response
- `POST /score/single` — body: `{profile: StudentProfile, scholarship_id: str}`, returns: single `ScoringResult`
- `GET /score/cached/{profile_id}` — returns: last scoring result or 404

**Error Handling:**
- Profile not found → `HTTP 404` with `{"detail": "Profile not found"}`
- Scholarship not found (for `score/single`) → `HTTP 404` with `{"detail": "Scholarship not found"}`
- Validation errors → `HTTP 422` (FastAPI default) with field-level error details
- All 5xx errors → log the exception with full traceback, return `{"detail": "Internal server error"}`

**Integration Tests to Write:**
- Create profile → verify 200 response with `profile_id`
- Get profile by ID → verify full profile returned
- Get nonexistent profile → verify 404
- Delete profile → verify 200, then verify GET returns 404
- `POST /score/all` with valid profile → verify results are returned and sorted by score
- `POST /score/single` with valid scholarship ID → verify correct single result
- `GET /score/cached/{profile_id}` after scoring → verify cached result returned

**→ STOP. Wait for approval before proceeding to Phase 8.**

---

## Phase 8 — Testing

**Purpose:** Complete the full pytest test suite to verified end-to-end behavior of the system.

**Deliverables:**
- [ ] All previously written tests passing: 0 failures, 0 errors
- [ ] Additional integration tests covering edge cases not covered in prior phases
- [ ] Test coverage report generated (`pytest --cov=backend`)
- [ ] `tests/conftest.py` — shared fixtures (test profile, test scholarship set)
- [ ] Minimum 60 tests total across all test files

**Required Test Categories:**
- Profile model validation (Phase 2 tests)
- Scholarship loader (Phase 3 tests)
- Feature matcher — all 5 MVP types + score_test warning behavior (Phase 4 tests)
- Hard pre-filters — all 4 filters + age-as-feature confirmation (Phase 5 tests)
- Scorer — score_one, score_all, labels (Phase 6 tests)
- Profile API — CRUD + completeness (Phase 7 tests)
- Scorer API — all 3 endpoints (Phase 7 tests)
- End-to-end test: full profile → score_all → verify ranked output

**Test Fixtures (in `conftest.py`):**
- `test_profile` — a fully complete, valid StudentProfile
- `test_incomplete_profile` — a profile with several optional fields missing
- `test_scholarship_set` — list of 5 scholarships with known expected scores for `test_profile`
- `test_app` — FastAPI TestClient instance

**→ STOP. Wait for approval before proceeding to Phase 9.**

---

## Phase 9 — Documentation

**Purpose:** Write developer-facing documentation so any new engineer can run the system without guessing.

**Deliverables:**
- [ ] `docs/SETUP.md` — complete local development setup guide
- [ ] `docs/API.md` — all endpoints with curl examples and expected responses
- [ ] `README.md` at project root — project overview, quick start, link to docs

**`SETUP.md` Must Include:**
- Python version requirement (Python 3.11+)
- How to clone the repository
- How to create and activate a virtual environment
- How to install dependencies: `pip install -r requirements.txt`
- How to copy `.env.example` to `.env`
- How to run the development server: `uvicorn backend.app.main:app --reload`
- How to run all tests: `pytest tests/ -v`
- How to add a new scholarship record (file format, required fields, where to place it)

**`API.md` Must Include — for each endpoint:**
- Method + path
- Description
- Request body (JSON example)
- Response body (JSON example)
- Error responses (with HTTP status code)
- curl command that can be copy-pasted and run

**→ STOP. Wait for approval. MVP is now complete when all success criteria below are met.**

---

## MVP Definition of Done

The MVP is **complete** when all of the following criteria are met — no exceptions:

### Backend API
- [ ] `GET /health` returns `{"status": "ok", "version": "0.1.0"}`
- [ ] `POST /profile` accepts a valid 30+ field student profile and returns a `profile_id`
- [ ] `GET /profile/{id}` retrieves the stored profile by ID
- [ ] `PATCH /profile/{id}` updates specific fields
- [ ] `DELETE /profile/{id}` removes the profile
- [ ] `GET /profile/{id}/completeness` returns an accurate completeness score (0–100)

### Scoring Engine
- [ ] All five feature types implemented and tested: `enum`, `threshold`, `boolean`, `output`, `range`
- [ ] All five hard pre-filters implemented and tested: `deadline`, `citizenship`, `degree`, `visa`, `age`
- [ ] `POST /score/all` returns correctly scored, pre-filtered, ranked results for a valid profile
- [ ] Results sorted by score descending
- [ ] Results below 40% excluded from response
- [ ] Maximum 20 results returned
- [ ] Gap analysis populated with unmatched non-output features
- [ ] Action checklist populated with all output-type features

### Data
- [ ] At least **1 scholarship record** successfully loaded from `data/scholarships/` (recommended: 10–50 records as seed dataset)
- [ ] Data volume is NOT a completion gate — a working scorer with 1 valid record satisfies this criterion
- [ ] All loaded records conform to `data/schema.json`
- [ ] At least one expired scholarship confirmed to be filtered out by the deadline pre-filter

### Tests
- [ ] `pytest tests/ -v` passes with 0 failures, 0 errors
- [ ] Minimum 60 tests total

### No Violations
- [ ] No prohibited system from AI_RULES.md Section 3 has been introduced
- [ ] No ML code exists anywhere in the codebase
- [ ] No live scraping code exists anywhere in the codebase
- [ ] No vector database code exists anywhere in the codebase
- [ ] `score_test` is NOT implemented — confirmed absent from all Python source files
- [ ] Age is NOT used as a hard pre-filter — confirmed handled via feature manifest `range` type only

---

## Phase Status Tracker

| Phase | Name | Status | Approved By | Date |
|---|---|---|---|---|
| 0 | Repository Inspection | 🔄 In Progress | — | June 09, 2026 |
| 1 | FastAPI Setup | ⬜ Not Started | — | — |
| 2 | Profile Model | ⬜ Not Started | — | — |
| 3 | Scholarship Loader | ⬜ Not Started | — | — |
| 4 | Feature Matcher | ⬜ Not Started | — | — |
| 5 | Hard Pre-Filters | ⬜ Not Started | — | — |
| 6 | M/T Scorer | ⬜ Not Started | — | — |
| 7 | API Routes | ⬜ Not Started | — | — |
| 8 | Testing | ⬜ Not Started | — | — |
| 9 | Documentation | ⬜ Not Started | — | — |

---

*Execution plan updated June 09, 2026 — Governance update v1.1*
*Source: Create PLAN.md.pdf instructions + ScholarBridge_Chat_Summary.pdf*
