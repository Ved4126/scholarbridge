# Scholarship Source Criteria v1

**Document Type:** Data Acquisition Policy  
**Status:** Active — Post-MVP Phase 2+ Preparation  
**Repository:** https://github.com/Ved4126/scholarbridge  
**Last Updated:** June 12, 2026  

---

## Purpose

This document defines acceptable scholarship sources for the ScholarBridge corpus. All records must originate from **official, verifiable channels**. Fake scholarships, aggregator spam pages, and unverifiable claims are strictly prohibited per `AI_RULES.md` Section 3 (no live scraping during MVP).

---

## Acceptable Scholarship Sources

### Tier 1: Primary Sources (Preferred)
These sources provide the highest reliability. Records from these sources require minimal verification beyond URL confirmation.

| Source Type | Examples | Verification Required |
|-------------|----------|----------------------|
| **University Financial Aid Offices** | Official .edu pages under "Scholarships" or "Financial Aid" sections | Confirm domain ends in `.edu` and page is maintained by university (check footer for contact info) |
| **Government Scholarship Programs** | Fulbright, DAAD, Chevening, PTDF, TETFund official portals | Verify URL matches organization's known domain pattern; check for government seal or official branding |
| **Non-Profit Organization Scholarships** | Rotary Club, United Way, local community foundations (official websites) | Confirm .org/.net domain with contact information visible on page |
| **Corporate/Foundation Scholarship Pages** | Coca-Cola Scholars, Gates Foundation scholarships via foundation.org domains | Verify URL matches organization's official website pattern |

### Tier 2: Secondary Sources (Acceptable with Documentation)
These sources may be used when primary source URLs are unavailable or unclear. Requires additional verification steps per Section 3 below.

| Source Type | Examples | Additional Requirements |
|-------------|----------|------------------------|
| **Educational Platforms** | Fastweb, Scholarship.com, College Board (Scholarships section) | Must link directly to the scholarship's primary source; cannot rely solely on platform description |
| **News Organization Features** | NPR "Money" segment scholarships, local newspaper listings | Article must include direct URL and contact information for verification |

### Tier 3: Unacceptable Sources (Prohibited)
These sources are strictly prohibited per `KNOWN_LIMITATIONS.md` Section 17 (mock/test data only during MVP):

| Source Type | Why Prohibited |
|-------------|----------------|
| **Scholarship Aggregator Spam Pages** | Sites with hundreds of scholarships, no contact info, generic templates |
| **"Free Scholarship" Landing Pages** | Pop-up heavy sites requiring email for "application forms" that lead nowhere |
| **Social Media Posts Only** | Facebook/Instagram posts without official website links |
| **Unverified Blog Posts** | Personal blogs or forums listing scholarships without source URLs |
| **Expired Scholarships Without Archive Links** | Dead links with no Wayback Machine archive available |

---

## Verification Requirements (All Sources)

Every scholarship record must pass these verification checks before being added to the corpus:

### 1. Primary Source Confirmation
- [ ] The page URL matches a known official domain for the awarding organization
- [ ] Contact information (email, phone, address) is visible on the source page or footer
- [ ] Physical mailing address exists and appears legitimate (not just "PO Box" without city/state/country)

### 2. Eligibility Transparency Check
- [ ] The scholarship clearly states eligibility criteria in human-readable text
- [ ] Application deadline(s) are explicitly stated with dates
- [ ] Award amount or funding range is disclosed (even if approximate: "$5,000–$10,000")

### 3. Accessibility Verification
- [ ] The page loads without JavaScript errors blocking content
- [ ] Contact information can be found within 2 clicks from the homepage
- [ ] No paywall or login requirement to view basic eligibility info

---

## Data Collection Workflow (No Scraping)

**IMPORTANT:** Do not use web scrapers, Playwright, Scrapy, or automated tools during MVP. All data must be manually collected and verified per `AI_RULES.md` Section 3 (no live scraping).

### Manual Collection Steps:
1. **Navigate to the scholarship page** using a browser
2. **Copy all relevant text content** into a local document for review
3. **Capture screenshots** of key sections (eligibility, deadline, award amount) as backup verification
4. **Verify contact information** by attempting to reach via email or phone if listed
5. **Document the source URL** and any archive URLs (Wayback Machine)

### Data Entry Template:
Use this structure when manually collecting scholarship data:

```markdown
## Scholarship Information

- **Name:** [Full official name]
- **Organization:** [Awarding organization full name]
- **Source URL:** [Direct link to primary source page]
- **Archive URL (if available):** [Wayback Machine or alternative archive]
- **Country of Origin:** [ISO 3166-1 alpha-2 code, e.g., "US", "IN"]

## Eligibility Criteria (from source)

[Copy exact text from the scholarship page describing who can apply]

## Application Details

- **Deadline(s):** [List all deadlines with dates and time zones if specified]
- **Award Amount:** [$X or range like "$5,000–$10,000"]
- **Application Method:** [Online portal / email submission / mail-in forms]
```

---

## Handling Missing Information

### Deadlines Not Listed
If a scholarship page does not explicitly state a deadline:

1. Check for "rolling admissions" language — if present, mark as `deadline: null` in the record
2. Look for application cycles (e.g., "Fall semester applications open annually") — document this pattern
3. If no information exists after thorough review, **do not add** the scholarship to MVP corpus

### Award Amount Not Disclosed
- Document as `"amount": null` with note explaining why unknown
- Scholarships without disclosed amounts are acceptable but should be flagged for future verification

---

## Handling Ambiguous Eligibility

When eligibility criteria are unclear or poorly worded:

1. **Cross-reference** the scholarship on multiple pages (FAQ, requirements section, application portal)
2. **Document ambiguity** in a comments field with exact quotes from source text
3. **Do not infer** eligibility — only include what is explicitly stated
4. If critical information cannot be verified after 30 minutes of research, skip the record

### Examples:
- "Open to international students" → Acceptable (means no nationality restrictions)
- "For deserving candidates" without definition → Document as vague; consider excluding from MVP corpus
- "Must have strong academic standing" → Too subjective for rules-based matching; exclude or note limitation

---

## Avoiding Fake and Unverifiable Records

### Red Flags Indicating Potential Scams:
| Indicator | Action Required |
|-----------|------------------|
| No physical address listed | Exclude from corpus |
| Email-only contact with generic domain (e.g., @gmail.com) for a claimed organization | Verify via official website; exclude if cannot confirm legitimacy |
| "Winner selected" or lottery-style language without clear selection criteria | Exclude — these are typically scams |
| Requests payment fees to apply | **Exclude immediately** — legitimate scholarships never charge application fees (unless specified by the scholarship itself) |
| Vague eligibility like "for anyone who wants it" with no stated requirements | Document as suspicious; exclude from MVP corpus |

### Verification Checklist Before Adding:
- [ ] Can I find this organization's official website independently of the scholarship page?
- [ ] Does the scholarship URL follow a logical domain structure for that organization?
- [ ] Is there at least one other reference to this scholarship on reputable sites (news, university pages)?

---

## Review Process Before Merging

Every new scholarship record must pass review by:

1. **Self-review** — Complete all checklist items in `SCHOLARSHIP_RECORD_REVIEW_CHECKLIST.md`
2. **Peer verification** — Have another team member verify the source URL loads and contains expected content
3. **Schema validation** — Ensure JSON conforms to `data/schema.json` requirements per `ARCHITECTURE.md` Section 5

### Merge Approval:
Records are merged when both reviewers confirm via comment in pull request or documented sign-off for manual merges.

---

## Target Corpus Size (v1)

- **Goal:** 50 verified scholarships across multiple countries and award amounts
- **Minimum diversity requirement:** At least one scholarship from each country represented in `data/scholarships/` directories (US, IN, CN, KR, NG, international programs)
- **Quality over quantity** — Each record must pass full verification process

---

## References
- `AI_RULES.md` Section 3: MVP First Rule (no scraping during MVP)  
- `KNOWN_LIMITATIONS.md`: Mock/test data only constraint  
- `ARCHITECTURE.md` Section 5: Scholarship schema requirements  
