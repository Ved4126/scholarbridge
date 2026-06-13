# Scholarship Record Review Checklist v1

**Document Type:** Quality Assurance Tool  
**Status:** Active — Post-MVP Phase 2+ Preparation  
**Repository:** https://github.com/Ved4126/scholarbridge  
**Last Updated:** June 12, 2026  

---

## Purpose

This checklist ensures every scholarship record added to the ScholarBridge corpus meets quality standards before merging. Use this document during peer review and final approval stages per `DATA_COLLECTION_PROCESS.md` Step 7.

**Target Corpus Size (v1):** 50 verified scholarships  
**Review Requirement:** Each new record requires two independent reviews  

---

## Quick Review Summary

Complete all sections below for each scholarship record under review:

```markdown
Record ID: _________________  
Scholarship Name: ________________________  
Source URL: ___________________________________  
Reviewer Initials: _________   Date: ___________  
Corresponding Record File: data/scholarships/[country]/[id].json  

## Overall Assessment [ ] APPROVED FOR MERGE   [ ] REVISIONS REQUIRED
```

---

## Section 1: Source Legitimacy Verification (5 minutes)

Confirm the scholarship originates from a legitimate source per `SCHOLARSHIP_SOURCE_CRITERIA.md` Sections 2-3.

### Tier Classification [ ] TIER 1    [ ] TIER 2   [ ] FLAGGED FOR REVIEW
**Tier:** Primary sources preferred; secondary acceptable with documentation  
```markdown
[ ] Source is a university financial aid page (.edu domain)
[ ] Source is government program (Fulbright, DAAD, Chevening, etc.)
[ ] Source is non-profit organization official website (.org/.net)
[ ] Source is corporate/foundation scholarship portal

OR

[ ] Source is educational platform with link to primary source
[ ] Source requires additional verification documentation noted below:
_________________________________________________________
```

### Red Flag Check [ ] NONE FOUND   [ ] ISSUES IDENTIFIED (see Section 6 for details)
```markdown
- [ ] No "free scholarship" spam indicators present
- [ ] Physical address or legitimate contact info visible on source page
- [ ] Domain structure matches organization's known website pattern
- [ ] No requests for payment fees to apply mentioned

If issues found, document in Section 6 below. If unresolved after investigation:
[ ] Record excluded from MVP corpus due to legitimacy concerns
```

---

## Section 2: Required Fields Completeness (3 minutes)

Verify all mandatory fields per `ARCHITECTURE.md` Section 5 and `data/schema.json`:

### Field-by-Field Verification [ ] All Present   [ ] Missing Items Listed Below:
```markdown
[ ] id — Unique identifier, lowercase kebab-case format verified
[ ] name — Full scholarship title (no abbreviations like "Scholarship" alone)
[ ] org_name — Organization's official full legal or trade name
[ ] country — ISO 3166-1 alpha-2 code (e.g., "US", not "United States")
[ ] source_url — Direct link to primary scholarship page, no redirects needed

Optional but recommended:
[ ] last_verified — Date in YYYY-MM-DD format; today's date for new records
```

### Notes Field [ ] Not Used   [ ] Contains Contextual Information:
_________________________________________________________

---

## Section 3: Feature Manifest Accuracy (10 minutes)

Ensure the `feature_manifest` accurately represents scholarship eligibility per `ARCHITECTURE.md` Sections 5-6 and `AI_RULES.md` Section 8.

### Eligibility Criteria Coverage [ ] Complete   [ ] Gaps Identified Below
```markdown
For each criterion from source page, verify it's represented in feature_manifest:

[ ] Nationality restrictions (if any) → enum type with ISO codes or empty list for open
[ ] Degree level requirements → enum type with accepted values  
[ ] Visa type requirements → enum type if specified; omit if not mentioned
[ ] GPA minimums → threshold type with gte operator and correct value

Additional criteria to check:
[ ] Field of study restrictions (if applicable)
[ ] Age range (range type, NOT hard filter per AI_RULES.md Section 8)
```

### Feature Type Validation [ ] Correct   [ ] Errors Found Below
```markdown
- [ ] No score_test features included (deferred per PRD.md Section 4.5 and AI_RULES.md Section 8)
- [ ] All feature types are from MVP set: enum, threshold, boolean, output, range only
- [ ] Field names in manifest match StudentProfile.to_feature_vector() keys exactly

Output-type features check (for action_checklist):
[ ] Each output type has a description field with task instructions from source
[ ] Output fields use custom names not conflicting with profile schema fields
```

### T Calculation Verification:
- [ ] Total feature count (T) includes all manifest entries including outputs
- [ ] M/T score calculation will be accurate when scoring runs against this record

---

## Section 4: Deadline and Award Information (2 minutes)

Verify application timeline details are correctly captured.

### Deadline Handling [ ] Correct   [ ] Issues Below
```markdown
[ ] Future deadline present in ISO format (YYYY-MM-DD); time zone noted if specified
[ ] Rolling admissions scholarship marked with null or appropriate note
[ ] Multiple deadlines listed as array of objects per schema requirements

Award information:
[ ] Amount disclosed and correctly typed (number for exact, string for range)
[ ] "Not specified" used appropriately when amount is genuinely unavailable
```

### Acceptance Criteria [ ] Open   [ ] Restricted
```markdown
- [ ] accepted_nationalities array empty [] means open to all nationalities per PRD.md Section 4.5
- [ ] Non-empty array contains only ISO codes matching source page restrictions
[ ] Empty or non-existent field in scholarship metadata (not feature_manifest) indicates no restriction

Degree/Visa acceptance:
[ ] accepted_degree_levels and/or accepted_visa_types arrays present if restrictions exist  
[ ] Empty arrays [] indicate open to all for that criterion per PRD.md Section 4.5
```

---

## Section 5: JSON Schema Compliance (3 minutes)

Validate the record conforms to `data/schema.json` requirements.

### Validation Steps [ ] Passed   [ ] Errors Found Below
```markdown
1. Run against schema validator or manually verify each required field type:
[ ] id is string and unique within corpus
[ ] name, org_name are non-empty strings (no truncation)
[ ] country uses 2-character ISO code only
[ ] source_url starts with https://

2. Check for prohibited content in comments/metadata:
[ ] No references to ML systems, vector databases, or scraping tools
[ ] No API keys or secrets embedded anywhere
```

### Schema Validator Command (for automated checking):
```bash
python scripts/load_scholarships.py --dir data/scholarships/ 2>&1 | grep -A5 "Rejected.*"
# Should show no rejections for this record if valid
```

---

## Section 6: Ambiguity and Edge Case Handling (7 minutes)

Document any unclear or unusual aspects of the scholarship.

### Documented Ambiguities [ ] None   [ ] Listed Below:
```markdown
If eligibility text is vague, document here with exact quotes from source:

Example format:
- "Field": field_of_study
  - Source quote: "[paste ambiguous text]"
  - Interpretation used in feature_manifest: "[your interpretation or 'excluded']"
  - Confidence level: [ ] High   [ ] Medium   [ ] Low (consider excluding if low)

Other ambiguities to note:
_________________________________________________________
```

### Missing Information Assessment [ ] Acceptable   [ ] Requires Exclusion
```markdown
Per SCHOLARSHIP_SOURCE_CRITERIA.md Section 5, determine if missing info blocks inclusion:

[ ] Deadline not listed but rolling admissions language present → Include with null deadline
[ ] Award amount undisclosed → Include as "Not specified" or omit from manifest  
[ ] Critical eligibility (nationality/degree) unclear after investigation → EXCLUDE and document reason below:
_________________________________________________________
```

### Red Flag Resolution [ ] Resolved   [ ] Still Present — Record Excluded
If red flags were identified in Section 1, verify resolution here:
```markdown
- [ ] Contacted organization via listed email/phone; confirmed scholarship exists (attach notes)
- [ ] Found Wayback Machine archive confirming historical legitimacy of program
- [ ] Cross-referenced with news articles or university announcements mentioning this specific award

If red flags remain unresolved after reasonable investigation:
[ ] Record excluded from MVP corpus per SCHOLARSHIP_SOURCE_CRITERIA.md Section 6
```

---

## Section 7: Diversity and Coverage Check (2 minutes)

Ensure the new record adds value to corpus diversity.

### Geographic Distribution [ ] Adds Value   [ ] Duplicate Region Only
```markdown
Current regional breakdown of corpus (approximate):
- US-based scholarships: ___ records  
- India home-country: ____ records  
- China home-country: ____ records  
- South Korea home-country: ____ records  
- Nigeria home-country: ____ records  
- International programs (UN, Fulbright, etc.): ____ records

This record adds to region(s) below:
[ ] US-based scholarship pool
[ ] India scholarships
[ ] Other Asia-Pacific region
[ ] Africa/Global south representation
```

### Award Type Diversity [ ] Adds Variety   [ ] Similar Profile Only
```markdown
- [ ] Different award amount range than existing records in same country
- [ ] Different degree level focus (undergrad vs grad)  
- [ ] Different field of study emphasis (STEM, humanities, etc.)
- [ ] Different organization type (government, private foundation, corporate, university)

Notes on corpus balance: _________________________________________________
```

---

## Section 8: Final Approval Signatures (1 minute)

Both reviewers must sign off before merging to main branch.

### Reviewer 1 Signature: _________________  
**Name:** ________________________  
**Date:** ___________  

I confirm this record meets all criteria in `SCHOLARSHIP_SOURCE_CRITERIA.md`, `DATA_COLLECTION_PROCESS.md`, and `ARCHITECTURE.md` Section 5. No prohibited systems or ambiguous values are included per `AI_RULES.md`.

### Reviewer 2 Signature: _________________  
**Name:** ________________________  
**Date:** ___________  

I have independently verified the source URL, reviewed feature_manifest accuracy against extracted eligibility text, and confirm no red flags remain unresolved. Approved for merge to main branch.

---

## Section 9: Merge Notes (Optional)

Additional context for future maintainers reviewing this record:
```markdown
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

### Related Records or Cross-References [ ] None   [ ] Listed Below:
```markdown
If similar scholarships exist, note here to avoid duplicates during corpus expansion.
Example: "Similar scholarship from same organization already in US directory with ID..."
```

---

## Quick Reference: Pass/Fail Criteria Summary

**APPROVE MERGE if ALL of the following are true:**
- [ ] Source legitimacy verified (Tier 1 or Tier 2 per criteria)  
- [ ] All required fields present and correctly typed  
- [ ] Feature_manifest accurately represents source eligibility text  
- [ ] No score_test features included; only MVP feature types used  
- [ ] Deadline handling appropriate for scholarship type  
- [ ] Ambiguities documented but not blocking inclusion (or resolved)  
- [ ] Red flags either absent or reasonably investigated and cleared  

**EXCLUDE if ANY of the following apply:**
- Source is from prohibited list (`SCHOLARSHIP_SOURCE_CRITERIA.md` Section 3)  
- Critical eligibility information cannot be verified after investigation  
- Payment fees required to apply (unless explicitly stated by scholarship itself as legitimate fee structure)  
- Red flags remain unresolved despite reasonable effort  

---

## References
- `SCHOLARSHIP_SOURCE_CRITERIA.md`: Source acceptance rules and red flag definitions  
- `DATA_COLLECTION_PROCESS.md`: Step-by-step collection workflow including field mapping guidance  
- `ARCHITECTURE.md` Sections 5-6: Scholarship schema and feature manifest design  
- `AI_RULES.md` Section 8: Scoring rules (feature types, age handling)  
