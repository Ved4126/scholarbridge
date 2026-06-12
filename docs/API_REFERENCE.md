# API Reference

This document outlines the available endpoints in the ScholarBridge MVP backend.

---

## 1. Health Check
### `GET /health`
**Purpose:** Verify that the FastAPI server is running.
- **Request Body:** None
- **Example Response:**
  ```json
  {
    "status": "ok",
    "version": "0.1.0"
  }
  ```
- **Status Codes:** `200 OK`

---

## 2. Profiles
### `POST /profile`
**Purpose:** Create a new student profile and store it in-memory.
- **Request Body:** `StudentProfile` (JSON)
- **Example Request:**
  ```json
  {
    "full_name": "Jane Doe",
    "nationality": "IN",
    "gpa": 3.8,
    "degree_level": "masters"
  }
  ```
- **Example Response:**
  ```json
  {
    "profile_id": "uuid-string",
    "completeness": 45.0,
    "message": "Profile created successfully"
  }
  ```
- **Status Codes:** `201 Created`, `422 Unprocessable Entity`

### `GET /profile/{profile_id}`
**Purpose:** Retrieve an existing profile by ID.
- **Request Body:** None
- **Example Response:** `StudentProfile` JSON object.
- **Status Codes:** `200 OK`, `404 Not Found`

### `PATCH /profile/{profile_id}`
**Purpose:** Partially update an existing profile.
- **Request Body:** JSON dictionary of fields to update.
- **Example Request:**
  ```json
  { "gpa": 3.9 }
  ```
- **Example Response:** The updated `StudentProfile`.
- **Status Codes:** `200 OK`, `404 Not Found`, `422 Unprocessable Entity`

### `DELETE /profile/{profile_id}`
**Purpose:** Delete a profile (and implicitly invalidate cached scores).
- **Request Body:** None
- **Example Response:**
  ```json
  { "message": "Profile deleted" }
  ```
- **Status Codes:** `200 OK`, `404 Not Found`

### `GET /profile/{profile_id}/completeness`
**Purpose:** Get the completeness score of a profile.
- **Request Body:** None
- **Example Response:**
  ```json
  {
    "profile_id": "uuid-string",
    "completeness": 85.5
  }
  ```
- **Status Codes:** `200 OK`, `404 Not Found`

---

## 3. Scorer
### `POST /score/all`
**Purpose:** Score all scholarships in the data catalogue against a student's profile, cache the results, and return the ranked list (scores >= 40, max 20).
- **Request Body:**
  ```json
  { "profile_id": "uuid-string" }
  ```
- **Example Response:** A list of `ScoringResult` objects.
- **Status Codes:** `200 OK`, `404 Not Found` (if profile invalid).

### `POST /score/single`
**Purpose:** Score exactly one specific scholarship against the profile, bypassing hard pre-filters to return raw Match/Tractability metrics.
- **Request Body:**
  ```json
  {
    "profile_id": "uuid-string",
    "scholarship_id": "specific-scholarship-id"
  }
  ```
- **Example Response:** A single `ScoringResult` object.
- **Status Codes:** `200 OK`, `404 Not Found`

### `GET /score/cached/{profile_id}`
**Purpose:** Retrieve the last cached scoring results for a profile without re-running the scoring engine.
- **Request Body:** None
- **Example Response:** A list of `ScoringResult` objects.
- **Status Codes:** `200 OK`, `404 Not Found` (if no cache exists, or profile deleted).
