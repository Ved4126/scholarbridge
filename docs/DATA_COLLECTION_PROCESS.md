# Scholarship Data Collection Process v1

**Document Type:** Operational Procedure  
**Status:** Active — Post-MVP Phase 2+ Preparation  
**Repository:** https://github.com/Ved4126/scholarbridge  
**Last Updated:** June 12, 2026  

---

## Purpose

This document defines the operational workflow for adding verified scholarship records to the ScholarBridge corpus. All data collection must follow this process to ensure consistency, accuracy, and compliance with `AI_RULES.md` (no scraping during MVP).

**Target Corpus Size:** 50 verified scholarships  
**Workflow Status:** Manual entry only — no automated tools permitted  

---

## Pre-Collection Checklist

Before beginning data collection for any scholarship:

1. [ ] Confirm the source meets criteria in `SCHOLARSHIP_SOURCE_CRITERIA.md`
2. [ ] Verify you have 30+ minutes available for thorough review (not rushed)
3. [ ] Prepare a local document or spreadsheet to capture information before entering JSON
4. [ ] Ensure your browser has developer tools open (for inspecting page elements if needed)

---

## Step-by-Step Collection Workflow

### Step 1: Source Verification (5 minutes)

Navigate to the scholarship source URL and confirm:

```markdown
Source URL: _________________

Organization Name: ________________________

Contact Email/Phone visible on page? [ ] Yes   [ ] No

Physical Address listed? [ ] Yes   [ ] No

Notes about legitimacy concerns: ___________________________________
```

**If any red flags from `SCHOLARSHIP_SOURCE_CRITERIA.md` Section 6 are present, STOP and do not proceed.**

---

### Step 2: Extract Required Fields (10 minutes)

Copy the following information directly from the source page. Use exact wording where possible for eligibility criteria.

```markdown
## Basic Information

- **Scholarship Name:** [Full official name as displayed on site]
- **Organization/Program Name:** ________________________
- **Country of Origin (ISO code):** _________________ (e.g., US, IN)
- **Source URL:** ___________________________________
- **Archive URL (if available):** _______________________

## Eligibility Criteria

Copy exact text describing who can apply:

[Paste full eligibility section here]

Key criteria to identify for feature_manifest:
  - Nationality restrictions? [ ] Yes   [ ] No (open)
    If yes, list countries: ___________________________________

  - Degree level requirements? [ ] Undergraduate   [ ] Masters   
    [ ] PhD   [ ] Postdoc   [ ] Open
   
  - Visa type requirements? [ ] F-1 only   [ ] J-1 only  
    [ ] Both   [ ] Other (specify): ________________________

  - GPA minimum: _________________
    
  - Age range specified? [ ] Yes: ______ to ________   
    [ ] No age restriction
    
  - Field of study restrictions? ___________________________________
    
  - Major-specific requirements? ___________________________________

## Application Details

- **Application Deadline:** ________________________ (include time zone if listed)
- **Award Amount(s):** _________________ or "Not specified"
- **Number of awards available:** _________________
- **Selection criteria mentioned?** [ ] Academic merit   [ ] Financial need  
  [ ] Community service   [ ] Diversity   [ ] Other: ________________________

## Application Requirements (for action_checklist)

List all required materials/documents:
1. _______________________________________________________
2. _______________________________________________________
3. _______________________________________________________
4. _______________________________________________________
5. _______________________________________________________

Notes about essays, interviews, or other non-auto-evaluated requirements:
_________________________________________________________
```

---

### Step 3: Convert Eligibility Text to Feature Manifest (10 minutes)

Translate the extracted eligibility criteria into JSON feature manifest format per `ARCHITECTURE.md` Section 5.

#### Mapping Guidelines:

| Source Language | JSON Type Example | Notes |
|-----------------|-------------------|--------|
| "Must be a US citizen" or similar nationality requirement | `"type": "enum", "field": "nationality", ...`, `"values": ["US"]` | Use ISO 3166-1 alpha-2 codes only |
| "Open to all nationalities" (no restriction mentioned) | Omit from manifest entirely OR use empty `accepted_nationalities: []` in scholarship metadata | Empty list means open to all per PRD.md Section 4.5 |
| "For master's students" or similar degree requirement | `"type": "enum", "field": "degree_level", ...`, `"values": ["masters"]` | Map text like "graduate student" → `phd` if appropriate, else document ambiguity |
| "Minimum GPA of 3.0" | `"type": "threshold", "field": "gpa", "operator": "gte", "minimum": 3.0` | Use exact number from source; round to one decimal place max |
| "For undergraduates only" or similar age range like "ages 18-25" | `"type": "range", "field": "age", ...`, `"minimum": 18, "maximum": 25` | Age is NOT a hard filter — it's evaluated as feature per PRD.md Section 4.5 and AI_RULES.md Section 8 |
| "Must have F-1 visa" or similar | `"type": "enum", "field": "visa_type", ...`, `"values": ["F-1"]` | Map text like "international student on US visa" → `other` if not specific |
| "Demonstrated financial need required" | `"type": "boolean", "field": "demonstrated_financial_need"` | Boolean true/false based on requirement presence |
| "Essay about your goals required" or similar non-evaluated item | `"type": "output", "field": "<custom_field>", ...`, `"description": "[from source]"` | Use custom field names for output types not in profile schema; these populate action_checklist only |

#### Field Name Mapping Reference:

Use these exact `StudentProfile` fields from `profile_agent.py`:
- `nationality` → nationality requirements  
- `degree_level` → degree level restrictions  
- `visa_type` → visa type requirements  
- `gpa` → GPA thresholds  
- `age` (optional) → age range if specified in scholarship  
- `field_of_study` → field of study matching (use `"type": "enum"` with values list or omit for open fields)

#### Handling Ambiguous Eligibility:

If the source text is unclear about a requirement:
1. Document the ambiguity in comments within your local draft JSON
2. **Do not guess** — only include what can be verified from explicit statements
3. If critical information cannot be resolved after 30 minutes, skip this scholarship for MVP corpus

---

### Step 4: Validate Against Schema (5 minutes)

Before creating the final JSON file:

1. Open `data/schema.json` and review required fields
2. Ensure your draft includes all mandatory fields with correct types
3. Verify no prohibited systems are referenced (no ML, vector DB mentions in comments)

---

### Step 5: Create Final Record File (5 minutes)

Create a new JSON file at the appropriate country directory:

```bash
# Example paths based on scholarship origin:
data/scholarships/us/your-scholarship-id.json          # US-based scholarships  
data/scholarships/in/ag-khan-foundation-international-scholarship.json  # India home-country
data/scholarships/international/fulbright-program.json   # International programs

# File naming convention:
- Use lowercase with hyphens (kebab-case) for IDs
- No spaces or special characters except hyphen and underscore
- Example: "aga-khan-foundation-international-scholarship" not "Aga Khan Scholarship 2026"
```

---

### Step 6: Self-Review Checklist (5 minutes)

Complete this checklist before submitting for peer review:

```markdown
## DATA COLLECTION PROCESS — SELF REVIEW CHECKLIST

**Scholarship:** ________________________  
**Source URL:** ___________________________________  

### Source Verification [ ] Complete   [ ] Not Done
- [ ] Domain matches organization's official website pattern
- [ ] Contact information (email/phone/address) is visible on page or footer
- [ ] No red flags from SCHOLARSHIP_SOURCE_CRITERIA.md Section 6

### Field Completeness [ ] All Present   [ ] Missing Items Listed Below:
- [ ] id field present and follows naming convention
- [ ] name field contains full scholarship title (no abbreviations)
- [ ] org_name matches organization's official name
- [ ] country uses ISO 3166-1 alpha-2 code (e.g., "US", not "United States")
- [ ] source_url is direct link to primary source page (not aggregator or news article only)
- [ ] last_verified date in ISO format (YYYY-MM-DD); today's date if newly added
- [ ] deadline present and valid future date OR null with explanation for rolling admissions

### Feature Manifest Quality [ ] Accurate   [ ] Needs Revision:
- [ ] All eligibility criteria from source are represented in feature_manifest
- [ ] Each feature has correct type (enum/threshold/boolean/output/range)
- [ ] Field names match StudentProfile.to_feature_vector() output exactly
- [ ] No score_test features included (deferred per AI_RULES.md Section 8 and PRD.md Section 4.5)
- [ ] Output-type features have descriptions from source text for action_checklist

### Ambiguity Handling [ ] Resolved   [ ] Documented:
- [ ] All ambiguous criteria documented in comments or notes field (if available)
- [ ] No guessed values — only explicitly stated requirements included
- [ ] Missing non-critical information noted but not blocking inclusion if acceptable per source criteria

### Schema Compliance [ ] Valid   [ ] Issues to Fix:
- [ ] JSON is valid and parseable (no syntax errors)
- [ ] All required fields from data/schema.json are present with correct types
- [ ] No prohibited content in comments or metadata sections

## Peer Review Status: _________________  
**Reviewer Name:** ________________________  

### Verification Steps Completed by Peer:
- [ ] Reviewed source URL and confirmed page loads correctly
- [ ] Verified contact information matches what's on the scholarship page
- [ ] Cross-checked feature_manifest against extracted eligibility text from Step 2
- [ ] Confirmed no prohibited systems or ambiguous values included

## Merge Approval: _________________  
**Approved by:** ________________________  

### Notes for Future Reviewers:
_________________________________________________________
```

---

### Step 7: Submit for Peer Review (Ongoing)

1. Create a pull request with your new scholarship record file(s)
2. Tag at least one other team member or use project's review workflow
3. Address any feedback before merging to main branch

**Note:** During MVP, all merges may require explicit approval from maintainers per `AI_RULES.md` Section 10 (Definition of Done).

---

## Post-Merge Documentation

After a scholarship is merged:

1. Update this document's "Corpus Inventory" section with the new record
2. Note any interesting patterns or edge cases encountered during collection
3. Flag for future review if source URL changes or deadline approaches expiration

---

## References
- `SCHOLARSHIP_SOURCE_CRITERIA.md`: Source acceptance rules  
- `ARCHITECTURE.md` Section 5: Scholarship schema definition  
- `AI_RULES.md` Section 8: Scoring rules (feature types, age handling)  
