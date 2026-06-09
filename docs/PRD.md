# PRD.md — ScholarBridge Product Requirements Document

> **Document Type:** Product Requirements Document (PRD)
> **Status:** Active — MVP Scope
> **Repository:** https://github.com/Ved4126/scholarbridge
> **Last Updated:** June 09, 2026
> **Version:** 1.0

This document is the **single source of truth** for product requirements. All engineering decisions
must trace back to a requirement stated here. Do not build features that are not in this document.

---

## 1. Product Overview

**ScholarBridge** is an AI-assisted scholarship discovery platform for international students studying in
the United States. It collects a structured student profile, loads a curated scholarship database, applies
deterministic hard eligibility filters, calculates a transparent eligibility score, and returns a ranked list of
scholarship opportunities the student is genuinely likely to qualify for.

### The Platform Does Five Things

1. **Collects** student profile information across 30+ data points in 6 categories
2. **Loads** scholarship records from a structured, schema-validated JSON database
3. **Applies** hard eligibility pre-filters (deadline, citizenship, degree level, visa type)
4. **Calculates** an eligibility score using the M/T formula: `Score = (M / T) × 100`
5. **Returns** ranked scholarship opportunities with match percentage, gap analysis, and action checklist

---

## 2. Problem Statement

International students in the US face a structurally broken scholarship discovery experience:

- **~1.1 million** international students enrolled in the US (2024–25 academic year)
- **Less than 8%** receive institutional financial aid — universities like SJSU have limited spots for internationals
- **40,000+** scholarships exist across private, public, and international sources — but they are scattered
- **Home-country scholarships** (government programs, diaspora-funded, bilateral agreements) are largely unknown to students who have moved abroad
- **8–12 hours per week** wasted per student on manual scholarship research with low conversion
- Average annual cost at private universities is **$70,000–$90,000** — the financial stakes are extreme

The discovery problem is not a lack of scholarships. It is a **matching and access problem**. ScholarBridge
solves it with structured profile-driven matching and transparent scoring.

---

## 3. Target Users

### Primary Users

| User Type | Description | Visa Status |
|---|---|---|
| F-1 Undergraduate | US university undergrad, any year | F-1 |
| F-1 Graduate (Master's) | MS students in any field | F-1 |
| F-1 PhD Students | Doctoral students, research or coursework phase | F-1 |
| J-1 Exchange Students | Exchange/visiting students | J-1 |

### Secondary Users (Phase 2+)

| User Type | Description |
|---|---|
| International Student Offices | ISSS staff who need bulk scholarship discovery tools |
| Financial Aid Advisors | University advisors helping international students find external funding |

---

## 4. MVP Features (Required — All Must Ship)

These features constitute the MVP. The MVP is not complete until all of them work end-to-end.

### 4.1 Student Profile Intake

- API endpoint to submit a structured student profile
- Profile covers 30+ fields across 6 categories:
  1. **Identity** — name, email, nationality (ISO 3166-1 alpha-2), country of origin, home country
  2. **Academic** — degree level (undergraduate / masters / phd), field of study, GPA (0.0–4.0), institution name, enrollment status (full-time / part-time)
  3. **Visa & Immigration** — visa type (F-1 / J-1 / other), visa status (active / expired), OPT/CPT eligibility
  4. **Financial** — demonstrated financial need (boolean), household income range (enum), dependent count
  5. **Achievements** — published papers (count), awards and honors (list), leadership roles (list), Dean's List (boolean), research experience (boolean)
  6. **Preferences** — preferred scholarship amount (min), open to essay-required scholarships (boolean), open to interview-required scholarships (boolean)

### 4.2 Profile Validation

- Pydantic v2 validation on all profile fields at submission time
- Return structured validation errors (field name + error message) — never generic 500 errors
- Profile completeness score: `(filled_fields / total_fields) × 100` — returned in the profile response

### 4.3 Scholarship Database

- JSON-file-based scholarship store under `data/scholarships/{country}/`
- One JSON file per scholarship record
- All records validated against `data/schema.json` at load time
- Non-conforming records rejected with a logged error — system does not silently skip bad records
- MVP requires successful scoring against a valid scholarship dataset. **Recommended seed dataset: 10–50 scholarship records.** Data volume is not an MVP completion criterion — functionality is.

### 4.4 Scholarship Schema Validation

- Every loaded scholarship must conform to `data/schema.json`
- Required fields: `id`, `name`, `org_name`, `country`, `source_url`, `last_verified`, `deadline`, `feature_manifest`
- `feature_manifest` is a list of feature objects — each with `type`, `field`, `operator/values`, and `weight`
- Schema violations logged with the scholarship file path — never swallowed silently

### 4.5 Eligibility Scoring

The scoring engine is the core of ScholarBridge. It must be:

**Scoring formula:**
```
Score = (M / T) × 100
```

- `M` = count of features in the scholarship's `feature_manifest` that the student's profile satisfies
- `T` = total count of features in the scholarship's `feature_manifest`
- Output-type features (essays, letters of recommendation, writing samples) contribute `0` to M but count toward T — they appear in the action checklist
- Score is a float, rounded to 1 decimal place

**Hard Pre-Filters (run before scoring — failing these means the scholarship is excluded entirely):**

| Filter | Logic |
|---|---|
| `deadline` | Scholarship deadline must be in the future (relative to today) |
| `citizenship` | Student's nationality must be in `accepted_nationalities` (or scholarship is open) |
| `degree` | Student's degree level must match `accepted_degree_levels` |
| `visa` | Student's visa type must match `accepted_visa_types` (or field is absent) |

> **Note:** Age is NOT a hard pre-filter. If a scholarship has an age requirement and the student's `age` field is absent, the scholarship remains eligible. Age is evaluated as a `range`-type feature in the feature manifest. A missing or out-of-range age reduces the score naturally. Missing age must never block a scholarship from reaching the scorer.

**Score Bands:**

| Band | Score Range | Label | Badge Color |
|---|---|---|---|
| Strong Match | 90%–100% | Strong Match | Green |
| Good Match | 70%–89% | Good Match | Blue |
| Possible Match | 40%–69% | Possible Match | Amber |
| Below Threshold | < 40% | (excluded from results) | — |

### 4.6 Ranked Results

- API endpoint that accepts a student profile and returns ranked scholarships
- Results sorted by score descending
- Each result includes: `scholarship_id`, `name`, `org_name`, `score`, `match_label`, `deadline`, `source_url`, `gap_analysis`, `action_checklist`
- Maximum 20 results returned per request (MVP cap)
- Scholarships below 40% score are excluded from the response

### 4.7 Gap Analysis

- For each returned scholarship, identify the features the student does **not** satisfy
- Format: list of `{field, requirement, student_value}` objects
- Displayed to user as "What you're missing" section

### 4.8 Action Checklist

- For each returned scholarship, list all `output`-type features as required tasks
- Examples: "Write personal statement (500–800 words)", "Obtain 2 letters of recommendation"
- These tasks cannot be automatically evaluated — they are surfaced explicitly so students know what preparation is required

### 4.9 Source Links and Deadline Display

- Every scholarship result must include a clickable `source_url`
- Deadline displayed as both ISO date and human-readable relative format (e.g., "47 days remaining")
- Expired scholarships must never appear in results (enforced by the deadline hard pre-filter)

### 4.10 FastAPI Endpoints

All endpoints are defined in ARCHITECTURE.md. The MVP must expose:

- `GET /health` — system health check
- `POST /profile` — create student profile
- `GET /profile/{profile_id}` — retrieve profile
- `PATCH /profile/{profile_id}` — update profile fields
- `DELETE /profile/{profile_id}` — delete profile
- `GET /profile/{profile_id}/completeness` — return completeness score
- `POST /score/all` — score all scholarships against a profile
- `POST /score/single` — score a single scholarship against a profile
- `GET /score/cached/{profile_id}` — return cached scoring results

---

## 5. Explicit Non-Goals

ScholarBridge is **NOT** any of the following. Building these features during MVP is a rules violation:

| What ScholarBridge Is NOT | Why It Is Out of Scope |
|---|---|
| A scholarship **application portal** | Students apply directly on the scholarship's own website |
| A scholarship **submission platform** | We do not host applications |
| An **immigration advisor** | Legal liability; out of scope |
| A **visa advisor** | Legal liability; out of scope |
| A **financial advisor** | Legal liability; out of scope |
| A **chatbot product** | Conversational UI is a post-MVP decision (Open Question Q2) |
| A **social network** | No social features planned |
| A **recommendation engine** | Rule-based M/T scoring only for MVP — ML is post-MVP |
| An **RLHF system** | Requires real user sessions at scale — post-MVP |
| An **ML-first platform** | ML is Phase 2+; MVP is deterministic rule-based only |
| A **scraping platform** | MVP uses static JSON data — live scraping is post-MVP |
| An **analytics dashboard** | No users yet — analytics is post-MVP |
| A **job board** | Scholarships only — no internship or job listings |
| A **university ranking tool** | Not a university comparison service |

---

## 6. User Stories

### Profile & Onboarding

**US-01** — As an F-1 graduate student, I want to submit my academic profile so ScholarBridge can evaluate scholarships against my specific qualifications.

**US-02** — As a student, I want to see a completeness score for my profile so I know if I have provided enough information for accurate matching.

**US-03** — As a student, I want clear field-level validation errors when I submit incomplete or invalid profile data, so I can fix issues without guessing what went wrong.

**US-04** — As a student, I want to update individual profile fields without resubmitting the entire profile, so I can keep my information current over time.

**US-05** — As a PhD student from India, I want my nationality, degree level, and field of study to all be considered simultaneously in matching, so I am not shown scholarships I am ineligible for.

### Scholarship Discovery

**US-06** — As a student, I want to see my eligibility score (e.g., "78%") for each scholarship, so I can quickly understand how strong a match I am.

**US-07** — As a student, I want scholarships sorted from highest to lowest match score, so I see my best opportunities first.

**US-08** — As a student, I want scholarships below 40% match excluded from my results, so I am not wasting time on opportunities I clearly do not qualify for.

**US-09** — As a student, I want to see the specific requirements I do not meet (gap analysis), so I understand exactly why a scholarship was scored lower.

**US-10** — As a student, I want to see the application deadline prominently displayed, including how many days remain, so I can prioritize time-sensitive opportunities.

**US-11** — As a student, I want a direct link to the official scholarship source, so I can apply or get more information without searching again.

**US-12** — As a student from Nigeria, I want home-country scholarships (e.g., PTDF, TETFund) to appear in my results, not just US-based opportunities.

### Action Checklist

**US-13** — As a student, I want to see a specific checklist of documents I need to prepare (personal statement, letters of recommendation) for each scholarship, so I can start preparing in advance.

**US-14** — As a student, I want the action checklist to clearly distinguish between items I can complete now (form fields, GPA) and items that require preparation time (essays, recommendation letters).

### Data Quality

**US-15** — As a developer loading scholarship data, I want the system to reject any scholarship record that does not conform to `data/schema.json` with a specific error message, so data quality problems are caught immediately.

**US-16** — As a developer, I want the system to never show expired scholarships to any user under any circumstances, so students are not misled by stale data.

### API / Developer

**US-17** — As a developer integrating with the API, I want a `/health` endpoint that returns system status, so I can monitor uptime and confirm the service is running.

**US-18** — As a developer, I want all API responses to use consistent JSON schemas, so I can build a frontend without guessing response shapes.

**US-19** — As a developer, I want to score a single scholarship against a profile via a dedicated endpoint, so I can test individual matches during development.

**US-20** — As a developer, I want all validation errors returned as structured JSON (not HTML or plaintext), so the frontend can display them cleanly to users.

### Security & Privacy

**US-21** — As a student, I want my profile data to be deleted when I request it, so I have control over my personal information.

**US-22** — As the project operator, I want no API keys or secrets stored in source code, so the repository can be made public without exposing credentials.

---

## 7. Functional Requirements

### FR-01: Profile Model
- Profile must accept and validate all fields defined in Section 4.1
- GPA must be a float between 0.0 and 4.0 (inclusive)
- Nationality must be a valid ISO 3166-1 alpha-2 country code
- Degree level must be one of: `undergraduate`, `masters`, `phd`, `postdoc`
- Visa type must be one of: `F-1`, `J-1`, `other`
- Email must be a valid email address (Pydantic EmailStr)

### FR-02: Feature Matcher
The feature matcher must implement all **five MVP feature types** from the scholarship feature manifest:

| Feature Type | Logic |
|---|---|
| `enum` | `student.field in scholarship.accepted_values` → 1 if true, 0 if false |
| `threshold` | `student.field >= scholarship.minimum_value` → 1 if true, 0 if false |
| `boolean` | `student.field == True` → 1 if true, 0 if false |
| `output` | Always 0 (essay/letter — cannot be auto-evaluated) |
| `range` | `scholarship.min <= student.field <= scholarship.max` → 1 if true, 0 if false |

**Future Feature Type (Deferred — do not implement during MVP):**

| Feature Type | Status | Reason |
|---|---|---|
| `score_test` | Deferred | Specification not finalized |

If a scholarship record contains a `score_test` feature, the loader must log a warning and skip that feature (treat T as if the feature does not exist for that record).

### FR-03: Scorer
- `score_one(profile, scholarship) → ScoringResult` — scores a single scholarship
- `score_all(profile, scholarships) → list[ScoringResult]` — scores all scholarships, applies pre-filters, sorts by score descending, returns top 20

### FR-04: Scholarship Loader
- `load_scholarships(directory: Path) → list[Scholarship]` — loads and validates all JSON files
- Logs a warning for each rejected file with the file path and specific validation error
- Returns only valid records — never raises an unhandled exception on bad data

### FR-05: API Responses
All endpoints must return responses conforming to defined Pydantic response models. No raw dict returns.

---

## 8. Nonfunctional Requirements

### Performance
- `POST /score/all` must return results in under **2 seconds** for a database of 500 scholarships (MVP scale)
- Profile validation must complete in under **100ms**
- Health endpoint must respond in under **50ms**

### Reliability
- The scoring engine must produce **deterministic results** — the same profile + same scholarships must always produce the same scores
- Invalid scholarship records must be rejected at load time — the system must never crash due to malformed data at query time

### Security
- No secrets in source code or logs
- All API inputs validated before processing
- Profile deletion endpoint must completely remove the profile from in-memory storage (MVP) or database (post-MVP)

### Maintainability
- Every public function must have a docstring
- No function may exceed 50 lines
- Business logic must be unit-testable in isolation (no database or HTTP required to test the scorer)
- Type annotations required on all function signatures

### Scalability (Documented Intent, Not MVP Requirement)
- The JSON-file data store is intentionally temporary. PostgreSQL migration is planned post-MVP.
- The in-memory profile store is intentionally temporary. Database persistence is planned post-MVP.
- The architecture is designed so the scorer and matcher can be replaced with ML models (LightGBM) without changing the API contract.

---

## 9. Success Criteria — MVP Complete When:

- [ ] `POST /profile` accepts a valid 30+ field student profile and returns a profile ID
- [ ] `GET /profile/{id}/completeness` returns an accurate completeness score
- [ ] Scholarship loader reads all JSON files from `data/scholarships/` and rejects non-conforming records with specific error messages
- [ ] `POST /score/all` returns correctly scored, pre-filtered, ranked scholarships for a test profile
- [ ] Hard pre-filters (deadline, citizenship, degree, visa) are all enforced and tested
- [ ] Age requirement handled as a feature manifest `range` entry — missing age reduces score, does not block scholarship
- [ ] All five MVP feature types (enum, threshold, boolean, output, range) are implemented and tested
- [ ] `score_test` is NOT implemented — confirmed absent from codebase
- [ ] Gap analysis and action checklist are included in every scored result
- [ ] `pytest` suite passes with 0 failures
- [ ] No prohibited systems (Section 3 of AI_RULES.md) have been introduced

---

*Document updated June 09, 2026 — Governance update v1.1*
*Source: ScholarBridge_Chat_Summary.pdf + Create PRD.md.pdf instructions*
