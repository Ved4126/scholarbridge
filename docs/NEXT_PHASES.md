# ScholarBridge Next Phases Roadmap

## Current Project Status

* **Backend FastAPI MVP exists**: Provides robust, in-memory APIs for profile management and match scoring.
* **Profile API exists**: Endpoint `/profile/` validates, creates, retrieves, patches, and deletes student profiles.
* **Scholarship loader exists**: Loads and validates local scholarship JSON records from structured folders.
* **Feature matcher exists**: Maps student attributes against criteria specifications like range, enum, threshold, boolean, and output types.
* **Hard prefilters exist**: Filters out ineligible candidates using strict criteria (deadline, nationalities, degree levels, and visa types).
* **M/T scorer exists**: Evaluates matched scholarships using the deterministic scoring formula `Score = (M / T) × 100` rounded to 1 decimal place.
* **Frontend MVP exists**: Premium Next.js App Router application built using Tailwind CSS and TypeScript.
* **Frontend can submit profile and display results**: Integrates forms, progress tracking, and compatibility lists on the results page.
* **Current data is still mostly test/demo scholarship data**: Local mock files are used for testing matching algorithms and UI components.

---

## Phase 11 — Real Scholarship Data Seed

### Goal
Add the first 10–20 real manually verified scholarship JSON files.

### Scope
* Use only official scholarship pages.
* Add JSON files under `data/scholarships/international/`.
* Validate files against `data/schema.json`.
* Include `source_url`, `deadline`, eligibility rules, `feature_manifest`, and output requirements.
* Keep dataset small and high quality.
* No scraping.

### Deliverables
* 10–20 schema-valid scholarship JSON files.
* Updated documentation explaining data source standards.
* Tests confirming scholarships load successfully.
* Manual UI check showing real matches.

### Acceptance Criteria
* All scholarship JSON files pass validation.
* Backend tests pass.
* At least one realistic profile returns at least one real scholarship result.
* Results show score, match label, deadline, source URL, gap analysis, and action checklist.

---

## Phase 12 — Scholarship Data Quality and Explainability

### Goal
Make results more transparent and trustworthy.

### Scope
* Improve explanation standards for `gap_analysis` and `action_checklist`.
* Document feature labeling conventions.
* Define what makes a good scoring feature.
* Define what belongs as an output feature.
* Improve consistency across scholarship records.

### Deliverables
* Data quality checklist.
* Explanation conventions.
* Updated scholarship authoring guide.

### Acceptance Criteria
* A developer can add a scholarship consistently.
* Users can understand why a scholarship matched.
* Output requirements are clearly separated from eligibility scoring.

---

## Phase 13 — Frontend QA and Premium Polish

### Goal
Make the MVP demo-ready and visually polished.

### Scope
* Mobile responsiveness.
* Loading states.
* Error states.
* Empty states.
* Results card clarity.
* Form usability.
* Accessibility review.
* Browser checks in Chrome and Safari.

### Deliverables
* UI QA checklist.
* Known issues list.
* Screenshots or manual verification notes.

### Acceptance Criteria
* Home, profile, and results pages work on desktop and mobile.
* No red Next.js error overlay.
* No broken profile-to-results flow.
* Clear messaging for loading, error, and no-match states.

---

## Phase 14 — Local Profile and Results Persistence

### Goal
Make user results survive refresh during MVP testing without adding auth or database.

### Scope
* Use `localStorage` or `sessionStorage` only.
* Save latest profile.
* Save latest scoring results.
* Add start-over/edit-profile behavior.
* Do not add backend persistence.

### Deliverables
* Documented storage strategy.
* Defined storage keys.
* Clear reset behavior.

### Acceptance Criteria
* User can refresh results page without losing latest results.
* User can edit profile and rescore.
* User can clear/start over.

---

## Phase 15 — Larger Scholarship Expansion

### Goal
Expand the manually curated dataset after the first seed is stable.

### Scope
* Grow from 10–20 scholarships to 50–100.
* Prioritize scholarships for international students in the US.
* Organize by degree level, field, nationality, financial need, merit, leadership, research, and entrepreneurship.
* Avoid duplicates.
* Continue using only official sources.

### Deliverables
* Expanded scholarship dataset.
* Duplicate prevention checklist.
* Data review checklist.

### Acceptance Criteria
* Dataset remains schema-valid.
* No duplicate source URLs.
* Search/matching remains fast enough for MVP.
* Results remain explainable.

---

## Phase 16 — Deployment Preparation

### Goal
Prepare ScholarBridge for portfolio/demo sharing.

### Scope
* Deployment documentation only at this stage.
* Document frontend and backend deployment options.
* Document environment variables.
* Document production CORS considerations.
* Document demo flow.
* Do not deploy yet unless explicitly approved later.

### Deliverables
* Deployment readiness checklist.
* Environment variable guide.
* Demo script outline.

### Acceptance Criteria
* A reviewer can understand how to run the app locally.
* A future deployment phase has clear prerequisites.
* No accidental production secrets or test files are committed.

---

## Recommended Phase Order

1. **Phase 11 — Real Scholarship Data Seed**
2. **Phase 12 — Scholarship Data Quality and Explainability**
3. **Phase 13 — Frontend QA and Premium Polish**
4. **Phase 14 — Local Profile and Results Persistence**
5. **Phase 16 — Deployment Preparation**
6. **Phase 15 — Larger Scholarship Expansion**

### Why this order?
* **Real data comes first** because matching is the primary product value. Testing algorithms with actual files reveals edge cases early.
* **Explainability follows** because users must trust results before visual details are finished.
* **UI polish follows** once real results exist and explanations are verified.
* **Persistence improves demo usability** for testers who refresh pages or adjust forms.
* **Deployment prep comes before large expansion** to ensure the codebase can be demonstrated online before loading hundreds of entries.
* **Larger expansion is safer** after data quality rules, schema conventions, and layout restrictions are stabilized.
