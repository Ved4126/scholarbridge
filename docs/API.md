# API.md — ScholarBridge API Reference

> **Base URL (local):** `http://127.0.0.1:8000`
> **Interactive docs:** `http://127.0.0.1:8000/docs`
> **All request bodies:** `Content-Type: application/json`
> **All responses:** `Content-Type: application/json`

---

## Table of Contents

1. [Sample Student Profile JSON](#1-sample-student-profile-json)
2. [GET /health](#2-get-health)
3. [POST /profile/](#3-post-profile)
4. [GET /profile/{profile_id}](#4-get-profileprofile_id)
5. [PATCH /profile/{profile_id}](#5-patch-profileprofile_id)
6. [DELETE /profile/{profile_id}](#6-delete-profileprofile_id)
7. [GET /profile/{profile_id}/completeness](#7-get-profileprofile_idcompleteness)
8. [POST /score/all](#8-post-scoreall)
9. [POST /score/single](#9-post-scoresingle)
10. [GET /score/cached/{profile_id}](#10-get-scorecachedprofile_id)
11. [Error Reference](#11-error-reference)

---

## 1. Sample Student Profile JSON

This is a complete, valid profile payload. Use it as a template for all `POST /profile/` and related requests.

All field names are taken directly from the current `StudentProfile` Pydantic model in
`backend/app/agents/profile_agent.py`.

```json
{
  "full_name": "Priya Sharma",
  "date_of_birth": "1998-03-15",
  "gender": "female",
  "nationality": "IN",
  "dual_citizenship": null,
  "home_country": "IN",
  "home_city": "Mumbai",
  "visa_type": "F-1",
  "enrollment_status": "full_time",
  "first_generation_student": true,
  "degree_level": "masters",
  "field_of_study": "Computer Science",
  "major": "Machine Learning",
  "minor": null,
  "university_name": "MIT",
  "university_state": "MA",
  "gpa": 3.8,
  "gpa_scale": 4.0,
  "gre": null,
  "gmat": null,
  "toefl": 110.0,
  "ielts": null,
  "sat": null,
  "act": null,
  "expected_graduation_year": 2026,
  "previous_degrees": null,
  "published_research": true,
  "research_papers": ["Neural Scaling Laws (2024)"],
  "conference_presentations": 1,
  "patents": 0,
  "academic_awards": ["Dean's List 2023"],
  "previous_scholarships": [],
  "leadership_roles": ["Graduate Student Council President"],
  "volunteer_hours": 120,
  "sports_achievements": [],
  "artistic_achievements": [],
  "entrepreneurship_experience": true,
  "financial_need_level": "medium",
  "family_income_bracket": "40k-80k",
  "current_funding_sources": ["TA stipend"],
  "dependents": 0,
  "career_goals": "AI research in healthcare",
  "intended_industry": "Healthcare AI",
  "willing_to_return_home_country": true,
  "languages": ["English", "Hindi"],
  "preferred_scholarship_types": ["merit-based"]
}
```

### Field Reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `full_name` | string | ✅ | Min 1 character |
| `date_of_birth` | string | ✅ | ISO 8601 date: `"YYYY-MM-DD"` |
| `gender` | string \| null | — | Free text |
| `nationality` | string | ✅ | ISO 3166-1 alpha-2 (e.g. `"IN"`, `"US"`) |
| `dual_citizenship` | string \| null | — | ISO alpha-2 |
| `home_country` | string | ✅ | |
| `home_city` | string \| null | — | |
| `visa_type` | string | ✅ | e.g. `"F-1"`, `"J-1"` |
| `enrollment_status` | enum | ✅ | `"full_time"` or `"part_time"` |
| `first_generation_student` | boolean \| null | — | |
| `degree_level` | enum | ✅ | `"undergrad"`, `"masters"`, `"phd"`, `"postdoc"` |
| `field_of_study` | string | ✅ | |
| `major` | string | ✅ | |
| `minor` | string \| null | — | |
| `university_name` | string | ✅ | |
| `university_state` | string | ✅ | US state abbreviation or country |
| `gpa` | float | ✅ | `>= 0.0`; must be `<= gpa_scale` |
| `gpa_scale` | float | ✅ | `> 0.0` (typically `4.0`) |
| `gre` | float \| null | — | `>= 0` |
| `gmat` | float \| null | — | `>= 0` |
| `toefl` | float \| null | — | `>= 0` |
| `ielts` | float \| null | — | `>= 0` |
| `sat` | float \| null | — | `>= 0` |
| `act` | float \| null | — | `>= 0` |
| `expected_graduation_year` | int | ✅ | Between 1901 and 2099 |
| `previous_degrees` | list[string] \| null | — | |
| `published_research` | boolean | ✅ | |
| `research_papers` | list[string] \| null | — | |
| `conference_presentations` | int | ✅ | `>= 0` |
| `patents` | int | ✅ | `>= 0` |
| `academic_awards` | list[string] | ✅ | Default: `[]` |
| `previous_scholarships` | list[string] | ✅ | Default: `[]` |
| `leadership_roles` | list[string] | ✅ | Default: `[]` |
| `volunteer_hours` | int \| null | — | `>= 0` |
| `sports_achievements` | list[string] | ✅ | Default: `[]` |
| `artistic_achievements` | list[string] | ✅ | Default: `[]` |
| `entrepreneurship_experience` | boolean | ✅ | |
| `financial_need_level` | enum | ✅ | `"low"`, `"medium"`, `"high"` |
| `family_income_bracket` | string \| null | — | |
| `current_funding_sources` | list[string] | ✅ | Default: `[]` |
| `dependents` | int \| null | — | `>= 0` |
| `career_goals` | string \| null | — | |
| `intended_industry` | string \| null | — | |
| `willing_to_return_home_country` | boolean \| null | — | |
| `languages` | list[string] | ✅ | Default: `[]` |
| `preferred_scholarship_types` | list[string] | ✅ | Default: `[]` |

---

## 2. GET /health

**Purpose:** Confirm the server is running. Used for monitoring and smoke tests.

**Request body:** None

```bash
curl http://127.0.0.1:8000/health
```

**Success response (200):**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## 3. POST /profile/

**Purpose:** Create and store a new student profile. Returns a `profile_id` for all subsequent requests.

> **Note the trailing slash.** Omitting it causes a `307 Temporary Redirect`.
> Use `curl -L` to follow the redirect automatically, or always include the `/`.

**Request body:** Full `StudentProfile` JSON (see [Section 1](#1-sample-student-profile-json))

```bash
curl -X POST http://127.0.0.1:8000/profile/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Priya Sharma",
    "date_of_birth": "1998-03-15",
    "nationality": "IN",
    "home_country": "IN",
    "home_city": "Mumbai",
    "visa_type": "F-1",
    "enrollment_status": "full_time",
    "degree_level": "masters",
    "field_of_study": "Computer Science",
    "major": "Machine Learning",
    "university_name": "MIT",
    "university_state": "MA",
    "gpa": 3.8,
    "gpa_scale": 4.0,
    "expected_graduation_year": 2026,
    "published_research": true,
    "conference_presentations": 1,
    "patents": 0,
    "entrepreneurship_experience": true,
    "financial_need_level": "medium"
  }'
```

**Success response (201):**

```json
{
  "profile_id": "a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd",
  "completeness": 75.0,
  "message": "Profile created successfully"
}
```

**Error — validation failure (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "gpa"],
      "msg": "Input should be greater than or equal to 0",
      "type": "greater_than_equal"
    }
  ]
}
```

---

## 4. GET /profile/{profile_id}

**Purpose:** Retrieve a stored profile by its ID.

```bash
curl http://127.0.0.1:8000/profile/a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd
```

**Success response (200):** Full `StudentProfile` JSON object (same shape as the request body in Section 1).

**Error — not found (404):**

```json
{
  "detail": "Profile not found"
}
```

---

## 5. PATCH /profile/{profile_id}

**Purpose:** Update one or more fields of a stored profile. Only the provided fields are changed.

```bash
curl -X PATCH http://127.0.0.1:8000/profile/a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd \
  -H "Content-Type: application/json" \
  -d '{"gpa": 3.9, "career_goals": "AI ethics research"}'
```

**Success response (200):** The complete updated `StudentProfile` JSON object.

**Error — not found (404):**

```json
{
  "detail": "Profile not found"
}
```

**Error — validation failure (422):** Same format as `POST /profile/`.

---

## 6. DELETE /profile/{profile_id}

**Purpose:** Permanently remove a profile from the in-memory store.

```bash
curl -X DELETE http://127.0.0.1:8000/profile/a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd
```

**Success response (200):**

```json
{
  "message": "Profile deleted"
}
```

**Error — not found (404):**

```json
{
  "detail": "Profile not found"
}
```

---

## 7. GET /profile/{profile_id}/completeness

**Purpose:** Return the completeness score for a stored profile. The score is the percentage of
key fields that are non-null and non-empty.

```bash
curl http://127.0.0.1:8000/profile/a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd/completeness
```

**Success response (200):**

```json
{
  "profile_id": "a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd",
  "completeness": 85.0
}
```

The `completeness` value is a float between `0.0` and `100.0`, rounded to 1 decimal place.

**Error — not found (404):**

```json
{
  "detail": "Profile not found"
}
```

---

## 8. POST /score/all

**Purpose:** Score all scholarships in `data/scholarships/` against a stored profile.

Internally this:
1. Looks up the stored profile by `profile_id`
2. Loads all scholarship JSON files
3. Applies hard pre-filters (deadline, citizenship, degree, visa)
4. Scores each passing scholarship using `Score = (M / T) × 100`
5. Excludes results below 40.0
6. Returns up to 20 results sorted by score descending
7. Caches the result (retrievable via `GET /score/cached/{profile_id}`)

```bash
curl -X POST http://127.0.0.1:8000/score/all \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd"}'
```

**Success response (200):** Array of `ScoringResult` objects, sorted by `score` descending.

```json
[
  {
    "scholarship_id": "test_scholarship",
    "name": "ScholarBridge Test Scholarship",
    "org_name": "ScholarBridge Test Organization",
    "score": 66.7,
    "match_label": "Possible Match",
    "deadline": "2099-12-31",
    "source_url": "https://example.com/test-scholarship",
    "gap_analysis": [
      {
        "field": "age",
        "label": "Age limit",
        "requirement": "<= 35.0",
        "student_value": null
      }
    ],
    "action_checklist": [
      "Personal statement required"
    ]
  }
]
```

**Score bands:**

| Score range | `match_label` |
|---|---|
| 90.0 – 100.0 | `"Strong Match"` |
| 70.0 – 89.9 | `"Good Match"` |
| 40.0 – 69.9 | `"Possible Match"` |
| below 40.0 | excluded from results |

**Error — profile not found (404):**

```json
{
  "detail": "Profile not found"
}
```

---

## 9. POST /score/single

**Purpose:** Score one specific scholarship against a stored profile. Does not apply hard pre-filters —
always returns a raw M/T score for that scholarship.

```bash
curl -X POST http://127.0.0.1:8000/score/single \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd",
    "scholarship_id": "test_scholarship"
  }'
```

**Success response (200):** A single `ScoringResult` object (same shape as one element of the `POST /score/all` array).

```json
{
  "scholarship_id": "test_scholarship",
  "name": "ScholarBridge Test Scholarship",
  "org_name": "ScholarBridge Test Organization",
  "score": 66.7,
  "match_label": "Possible Match",
  "deadline": "2099-12-31",
  "source_url": "https://example.com/test-scholarship",
  "gap_analysis": [
    {
      "field": "age",
      "label": "Age limit",
      "requirement": "<= 35.0",
      "student_value": null
    }
  ],
  "action_checklist": [
    "Personal statement required"
  ]
}
```

**Error — profile not found (404):**

```json
{
  "detail": "Profile not found"
}
```

**Error — scholarship not found (404):**

```json
{
  "detail": "Scholarship not found"
}
```

---

## 10. GET /score/cached/{profile_id}

**Purpose:** Return the last scoring result for a profile without re-running the scorer.
The cache is populated when `POST /score/all` is called.

```bash
curl http://127.0.0.1:8000/score/cached/a3f1c2d4-8b7e-4e9a-bcd0-12345678abcd
```

**Success response (200):** Same array format as `POST /score/all`.

**Error — no cached result (404):**

```json
{
  "detail": "Cached score not found"
}
```

> The cache is in-memory and is lost when the server restarts. Call `POST /score/all` again to repopulate.

---

## 11. Error Reference

| HTTP Status | When it occurs |
|---|---|
| `200 OK` | Successful `GET`, `PATCH`, `DELETE` |
| `201 Created` | Successful `POST /profile/` |
| `307 Temporary Redirect` | `POST /profile` without trailing slash — use `POST /profile/` |
| `404 Not Found` | Profile or scholarship not found; no cached score |
| `422 Unprocessable Entity` | Request body fails Pydantic validation |
| `500 Internal Server Error` | Unexpected server error (should not occur in normal operation) |

All error responses follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors (422) use FastAPI's default list format:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error description",
      "type": "error_type"
    }
  ]
}
```
