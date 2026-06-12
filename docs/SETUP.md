# SETUP.md — ScholarBridge Developer Setup Guide

> This guide is for engineers cloning and running the ScholarBridge backend for the first time.
> All commands assume macOS or Linux. Windows users should use WSL.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Python Version Requirement](#2-python-version-requirement)
3. [Cloning the Repository](#3-cloning-the-repository)
4. [Create and Activate a Virtual Environment](#4-create-and-activate-a-virtual-environment)
5. [Install Dependencies](#5-install-dependencies)
6. [Environment Variables](#6-environment-variables)
7. [Running the Development Server](#7-running-the-development-server)
8. [Swagger UI](#8-swagger-ui)
9. [Running Tests](#9-running-tests)
10. [Adding a New Scholarship Record](#10-adding-a-new-scholarship-record)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Project Overview

ScholarBridge is a scholarship discovery backend for international students studying in the US.
It accepts a structured student profile, evaluates all scholarships against hard eligibility filters
and a deterministic M/T score, and returns a ranked list of matched opportunities.

**What it does:**
- Validates student profiles with Pydantic v2
- Loads and validates scholarship records from JSON files
- Applies hard pre-filters (deadline, citizenship, degree, visa type)
- Scores each scholarship using `Score = (M / T) × 100`
- Returns ranked results with gap analysis and action checklist

**What it does NOT do (MVP scope):**
- No authentication or user accounts
- No PostgreSQL or Redis — in-memory storage only
- No ML ranking, vector search, or web scraping
- No frontend

---

## 2. Python Version Requirement

**Minimum: Python 3.10**

The codebase uses the `X | Y` union type syntax (e.g. `str | None`) which requires Python 3.10+.
With `from __future__ import annotations` (present in all modules), 3.9 may work but is not tested.
Python 3.12 or 3.13 is recommended.

Check your version:

```bash
python3 --version
```

---

## 3. Cloning the Repository

```bash
git clone https://github.com/Ved4126/scholarbridge.git
cd scholarbridge
```

---

## 4. Create and Activate a Virtual Environment

From inside the `scholarbridge/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your shell prompt will change to show `(.venv)` when the environment is active.

To deactivate at any time:

```bash
deactivate
```

---

## 5. Install Dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

Current dependencies:

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `pydantic[email]` | Request validation |
| `python-dotenv` | `.env` file loading |
| `pytest` | Test runner |
| `httpx` | HTTP client (used by `TestClient`) |

---

## 6. Environment Variables

The codebase does not require any environment variables to run during MVP.
All API keys are loaded from environment only (never hardcoded).

Copy the example file to create your local `.env`:

```bash
cp .env.example .env
```

The `.env` file is in `.gitignore` and will never be committed.
Leave all values empty unless you are integrating a specific external service.

`.env.example` contents (key names only — no values):

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PINECONE_API_KEY=
DATABASE_URL=
SERP_API_KEY=
SECRET_KEY=
```

---

## 7. Running the Development Server

From the repository root (with `.venv` active):

```bash
python3 -m uvicorn backend.app.main:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

The `--reload` flag restarts the server automatically when source files change.

> **Important:** Always run uvicorn from the repository root (`scholarbridge/`), not from inside
> `backend/` — the project uses absolute module imports like `backend.app.main`.

---

## 8. Swagger UI

With the server running, open your browser to:

```
http://127.0.0.1:8000/docs
```

This is the interactive Swagger UI. You can use it to:
- Browse all available endpoints
- Send test requests directly from the browser
- See request and response schemas

The OpenAPI JSON spec is available at:

```
http://127.0.0.1:8000/openapi.json
```

---

## 9. Running Tests

From the repository root (with `.venv` active):

```bash
python3 -m pytest tests/ -v
```

Expected output (current baseline):

```
107 passed, 1 warning in 0.20s
```

The 1 warning is a third-party `httpx`/`starlette` deprecation notice — it is not from project code
and does not affect test results.

### Running a single test file

```bash
python3 -m pytest tests/test_scorer.py -v
```

### Running tests with output on failures only

```bash
python3 -m pytest tests/ -q
```

### Coverage (if you install pytest-cov)

```bash
pip install pytest-cov
python3 -m pytest tests/ --cov=backend --cov-report=term-missing
```

> `pytest-cov` is not in `requirements.txt` — install it separately if needed for development.

---

## 10. Adding a New Scholarship Record

### Where to place it

Place the JSON file under `data/scholarships/` in the appropriate country subfolder:

```
data/scholarships/
├── us/              ← US-based scholarships
├── india/           ← Indian government / diaspora scholarships
├── international/   ← UN, Fulbright, World Bank, DAAD, Chevening, etc.
└── ...
```

Create a new subfolder if the country does not exist yet.

### Required top-level fields

Every scholarship JSON must include these fields. Missing any of them causes the loader to reject the file with an error.

| Field | Type | Example |
|---|---|---|
| `id` | string | `"my-scholarship-2026"` |
| `scholarship_name` | string | `"My Scholarship Program"` |
| `org_name` | string | `"My Foundation"` |
| `source_url` | string | `"https://example.com/scholarship"` |
| `country` | string | `"US"` |
| `source_type` | string | `"foundation"` |
| `award_amount` | number | `10000` |
| `currency` | string | `"USD"` |
| `deadline` | string | `"2026-12-01"` (ISO 8601) |
| `award_year` | number | `2026` |
| `degree_levels` | list | `["masters", "phd"]` |
| `eligible_nationalities` | list | `["IN", "PK"]` or `[]` for any |
| `eligible_visa_types` | list | `["F-1", "J-1"]` or `[]` for any |
| `fields_of_study` | list | `["Computer Science"]` |
| `description` | string | Short description |
| `eligibility_text` | string | Raw eligibility requirements |
| `feature_manifest` | object | See below |
| `last_verified` | string | `"2026-06-01T00:00:00Z"` |
| `created_at` | string | `"2026-06-01T00:00:00Z"` |
| `updated_at` | string | `"2026-06-01T00:00:00Z"` |

### `feature_manifest` structure

```json
{
  "total_features": 3,
  "features": [
    {
      "id": "gpa",
      "label": "Minimum GPA",
      "type": "threshold",
      "student_field": "gpa",
      "min": 3.5,
      "required": true
    },
    {
      "id": "degree_level",
      "label": "Eligible degree levels",
      "type": "enum",
      "student_field": "degree_level",
      "values": ["masters", "phd"],
      "required": true
    },
    {
      "id": "personal_statement",
      "label": "Personal statement required",
      "type": "output",
      "required": true
    }
  ]
}
```

**`total_features` must exactly equal the number of items in the `features` list.**

#### Feature types

| Type | Required extra fields | Matching logic |
|---|---|---|
| `enum` | `student_field`, `values` | student's value must be in `values` |
| `threshold` | `student_field`, `min` | student's value must be `>= min` |
| `boolean` | `student_field` | student's field must be `true` |
| `range` | `student_field`, `min` or `max` | student's value must be within the range |
| `output` | none | always unmatched — goes to `action_checklist` |

> Do **not** use `score_test` — it is explicitly prohibited and will cause a load error.

### Validating your new record

**Option 1 — run the loader script directly:**

```bash
python3 scripts/load_scholarships.py
```

This prints a count of loaded records and raises a detailed error for any invalid file.

**Option 2 — run the test suite:**

```bash
python3 -m pytest tests/test_load_scholarships.py -v
```

**Option 3 — start the server and call `POST /score/all`:**

Start the server and submit a profile — your new scholarship will appear in results if the profile qualifies.

---

## 11. Troubleshooting

### 307 Temporary Redirect

FastAPI automatically redirects `POST /profile` (no trailing slash) to `POST /profile/` (with trailing slash).
To avoid the redirect, always use the trailing slash in `POST` requests:

```bash
# Correct
curl -X POST http://127.0.0.1:8000/profile/ ...

# Will redirect
curl -X POST http://127.0.0.1:8000/profile ...
```

> `GET`, `PATCH`, and `DELETE` requests on `/profile/{id}` do **not** require a trailing slash.

### 422 Unprocessable Entity

This means your request JSON does not match the `StudentProfile` Pydantic model.
The response body will include field-level errors like:

```json
{
  "detail": [
    {"loc": ["body", "gpa"], "msg": "value is not a valid float", "type": "type_error.float"}
  ]
}
```

Check the field names and types in the [API Reference](API.md#sample-student-profile-json).

### Port 8000 already in use

```bash
lsof -i :8000
kill -9 <PID>
```

Or start the server on a different port:

```bash
python3 -m uvicorn backend.app.main:app --reload --port 8001
```

### Module not found

Make sure you are running commands from the repository root (`scholarbridge/`), not from inside `backend/`:

```bash
# Always run from here:
cd /path/to/scholarbridge
python3 -m pytest tests/ -v
python3 -m uvicorn backend.app.main:app --reload
```

### Missing dependencies

If you see `ModuleNotFoundError`:

```bash
source .venv/bin/activate      # make sure the venv is active
pip install -r requirements.txt
```

### Data persists only for the server session

The MVP uses an in-memory store. All profiles are lost when the server restarts.
This is intentional for MVP. PostgreSQL persistence is planned post-MVP.
