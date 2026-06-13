# ScholarBridge Scholarship Data Authoring & Verification Guide

This guide defines the procedures for researching, authoring, reviewing, and validating scholarship JSON data records for ScholarBridge. All data files must adhere strictly to these rules.

---

## 1. Purpose

The core value of ScholarBridge is to deliver accurate, transparent eligibility match compatibility results to international students. To guarantee that students only see opportunities they qualify for, the underlying scholarship dataset must be of high quality, manually curated, and verified against official sources.

---

## 2. Data Source Rules

All scholarship records must originate from verified official sources.
* **Official Pages Only**: Only use official scholarship pages, or pages published directly by the offering foundation, corporate sponsor, government entity, or university department.
* **No Scraping**: All data records must be manually collected and curated. Automating or scraping scholarship directories is strictly prohibited.
* **No Third-Party Listicles/Blogs**: Unofficial blog posts, comparison articles, or directory sites must not be used as primary sources.
* **Exact source_url**: The `source_url` field must point directly to the primary official application instructions page or official guidelines document, enabling students to verify details independently.

---

## 3. Required Scholarship Fields

Every JSON file representing a scholarship record must reside in a subfolder under `data/scholarships/` (e.g., `data/scholarships/international/` or `data/scholarships/us/`) and must contain all properties defined as required in the schema:

| Property | JSON Type | Description |
|---|---|---|
| `id` | String | Unique identifier (lowercase, alphanumeric, underscores only). |
| `scholarship_name` | String | Official full name of the scholarship. |
| `org_name` | String | Official name of the offering organization/sponsor. |
| `source_url` | String | Fully qualified URL pointing to the official source guidelines page. |
| `country` | String | Primary country of origin or "International". |
| `source_type` | String | Category of the source (e.g., `foundation`, `university`, `government`). |
| `award_amount` | Number \| null | Award value in specified currency, or `null` if variable/unspecified. |
| `currency` | String \| null | ISO 3-letter currency code (e.g., `"USD"`, `"INR"`), or `null`. |
| `deadline` | String \| null | Application deadline formatted as `"YYYY-MM-DD"`. |
| `award_year` | String \| Integer \| null | Year the award takes effect. |
| `degree_levels` | Array[String] | Degree eligibility values (e.g., `["undergrad", "masters", "phd", "postdoc"]`). |
| `eligible_nationalities` | Array[String] | ISO country codes, or `["Any"]` if open to all nationalities. |
| `eligible_visa_types` | Array[String] | Eligible US student visas (e.g., `["F-1", "J-1"]`), or `["Any"]`. |
| `fields_of_study` | Array[String] | Matching disciplines list (e.g., `["Computer Science", "Engineering"]`). |
| `description` | String | Short overview of the scholarship opportunity. |
| `eligibility_text` | String | Raw eligibility criteria text copied directly from the official source page. |
| `feature_manifest` | Object | Manifest defining total features and spec matching lists. |
| `last_verified` | String | ISO 8601 UTC date-time indicating when the source was last manually checked. |
| `created_at` | String | ISO 8601 UTC date-time of file creation. |
| `updated_at` | String | ISO 8601 UTC date-time of file last edit. |

---

## 4. Hard Prefilter Fields

Before the scoring pipeline calculates compatibility, ScholarBridge applies hard pre-filters. If a student profile fails any of these pre-filters, the scholarship is rejected immediately:

1. **Deadline**:
   - The application deadline must not be expired.
   - Evaluated as passing if the deadline date is in the future.
2. **Nationality/Citizenship**:
   - Matches if student's `nationality` is in `eligible_nationalities` OR if `eligible_nationalities` contains `"Any"`.
3. **Degree Level**:
   - Matches if student's `degree_level` is in `degree_levels`.
4. **Visa**:
   - Matches if student's `visa_type` is in `eligible_visa_types` OR if `eligible_visa_types` contains `"Any"`.

---

## 5. Scoring Feature Rules

Once a scholarship passes hard pre-filters, its compatibility score is evaluated using a deterministic scoring formula:

$$\text{Score} = \frac{M}{T} \times 100$$

* **M (Matched Features)**: The number of features in the `feature_manifest` that the student profile successfully matches.
* **T (Total Features)**: The total number of features declared in the manifest.
* **Rounding**: Stored scores are rounded to exactly 1 decimal place (e.g. `66.7`).
* **Age Limit**: Age limit criteria is a **scoring feature** using type `range` targeting the `age` student field. It is **not** a hard pre-filter. A student who exceeds the age limit or lacks age details will only receive a lower compatibility score (unmatched feature), but is not completely filtered out.

---

## 6. Output Feature Rules

Output features represent application requirements that cannot be automatically matched or verified based on database facts (e.g., writing components, recommendations, interviews).

* **Contribution to scoring**: Output features **count toward T** (Total Features) but **contribute 0 to M** (Matched Features). They are always unmatched by design.
* **Action Checklist**: Every output feature declared in the manifest is automatically extracted and populated into the card's `action_checklist` panel in the UI.
* **Examples**:
  - `essay` / `personal_statement`
  - `recommendation_letters`
  - `transcripts`
  - `interview`

---

## 7. Feature Type Conventions

Features in `feature_manifest.features` must specify one of the following types:

1. **`enum`**:
   - Student value must match one of the items in the `values` array.
   - Requires: `"student_field"`, `"values"`.
2. **`threshold`**:
   - Student value must be greater than or equal to the `min` threshold.
   - Requires: `"student_field"`, `"min"`.
3. **`boolean`**:
   - Student field value must be `true`.
   - Requires: `"student_field"`.
4. **`range`**:
   - Student value must be between `min` and `max` (inclusive). If only `min` or only `max` is provided, matches single-sided bounds.
   - Requires: `"student_field"`, `"min"` and/or `"max"`.
5. **`output`**:
   - Represents application deliverables. Never matches.
   - Requires: No student field or criteria values.

---

## 8. Naming Conventions

* **Scholarship File Names**: Lowercase, alphanumeric, separating words with underscores, matching the scholarship ID. Example: `data/scholarships/international/fulbright_foreign_student.json` for ID `"fulbright_foreign_student"`.
* **Feature IDs**: Short lowercase string representing the feature (e.g. `"gpa"`, `"essay"`, `"leadership_roles"`, `"patents"`).
* **Labels**: Clean, human-readable strings displayed directly in the UI as the feature name (e.g. `"Minimum GPA"`, `"Personal statement required"`, `"Conference presentations"`).
* **Organization Names**: Official legal names without unnecessary prefixes or suffixes (e.g. `"Fulbright Program"` instead of `"The Official Fulbright Program Office"`).

---

## 9. Review Checklist for Every Scholarship

Before adding a new scholarship JSON record, check off the following steps:
- [ ] Primary source is the official university/foundation site (no blog listicles).
- [ ] `id` matches the filename.
- [ ] `source_url` is exact and active.
- [ ] `eligible_nationalities` contains standard ISO 3166-1 alpha-2 codes or `["Any"]`.
- [ ] `eligible_visa_types` matches standard codes (e.g. `"F-1"`, `"J-1"`, `"Any"`).
- [ ] `total_features` matches the length of the `features` array.
- [ ] All output features use the type `"output"`.
- [ ] The `age` limit configuration uses the type `"range"` targeting the student field `"age"`.
- [ ] The JSON parses correctly and matches `data/schema.json`.

---

## 10. Example Scholarship JSON Skeleton

```json
{
  "id": "example_merit_award",
  "scholarship_name": "Example Global Merit Award",
  "org_name": "Example Foundation",
  "source_url": "https://example.org/scholarship",
  "country": "International",
  "source_type": "foundation",
  "award_amount": 10000,
  "currency": "USD",
  "deadline": "2026-12-01",
  "award_year": 2026,
  "degree_levels": [
    "masters",
    "phd"
  ],
  "eligible_nationalities": [
    "IN",
    "CN"
  ],
  "eligible_visa_types": [
    "F-1"
  ],
  "fields_of_study": [
    "Computer Science",
    "Data Science"
  ],
  "description": "A merit award for incoming Master's and PhD students studying computer science disciplines.",
  "eligibility_text": "Must be an international student on an F-1 visa. Must maintain a GPA of 3.5+. Personal essay and transcript required.",
  "feature_manifest": {
    "total_features": 4,
    "features": [
      {
        "id": "degree_level",
        "label": "Eligible degree levels",
        "type": "enum",
        "student_field": "degree_level",
        "values": ["masters", "phd"],
        "required": true
      },
      {
        "id": "gpa",
        "label": "Minimum GPA",
        "type": "threshold",
        "student_field": "gpa",
        "min": 3.5,
        "required": true
      },
      {
        "id": "essay",
        "label": "Personal statement",
        "type": "output",
        "required": true
      },
      {
        "id": "transcript",
        "label": "Official transcripts",
        "type": "output",
        "required": true
      }
    ]
  },
  "last_verified": "2026-06-12T00:00:00Z",
  "created_at": "2026-06-12T00:00:00Z",
  "updated_at": "2026-06-12T00:00:00Z"
}
```

---

## 11. Common Mistakes to Avoid

1. **Mismatched total_features**: Setting `total_features` to a number different from the actual length of the `features` array. This triggers loader exceptions.
2. **Missing required fields**: Forgetting properties like `created_at`, `updated_at`, or `currency`.
3. **Invalid dates**: Not formatting the deadline as `"YYYY-MM-DD"`.
4. **Scoring outputs**: Attempting to create boolean criteria for writing submissions (e.g. `has_submitted_essay`). Writing deliverables must use type `"output"`.
5. **Age as pre-filter**: Placing age limits directly in `degree_levels` or custom pre-filter arrays. Age must be configured as a manifest feature.

---

## 12. Validation Steps

After authoring a scholarship record, run the following verification steps:

1. **Schema Check**:
   Validate your new JSON file using the built-in loader script:
   ```bash
   python3 scripts/load_scholarships.py
   ```
2. **Backend Integrity Tests**:
   Run the pytest suite to confirm that loading tests are still healthy:
   ```bash
   python3 -m pytest tests/test_load_scholarships.py -v
   ```
3. **UI Integration**:
   Launch the backend server (`python3 -m uvicorn backend.app.main:app --reload`), open the frontend app, submit a matching student profile, and verify the scholarship displays correctly with its score, badges, gap details, and preparation checklists.
