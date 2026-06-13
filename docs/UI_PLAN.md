# UI_PLAN.md — ScholarBridge Phase 10 Frontend Plan

> **Document Type:** Frontend Planning — Phase 10
> **Status:** Updated — awaiting approval before any code is written
> **Prerequisite:** Backend Phases 0–9 complete. 107 tests passing.
> **Last Updated:** June 12, 2026

---

## Table of Contents

1. [Frontend Goal](#1-frontend-goal)
2. [Premium Design Goal](#2-premium-design-goal)
3. [Recommended Stack](#3-recommended-stack)
4. [Visual Style Direction](#4-visual-style-direction)
5. [Color Direction](#5-color-direction)
6. [Typography Direction](#6-typography-direction)
7. [MVP Pages](#7-mvp-pages)
8. [Page Details](#8-page-details)
9. [API Integration Plan](#9-api-integration-plan)
10. [Component Plan](#10-component-plan)
11. [UX Principles](#11-ux-principles)
12. [User Flow](#12-user-flow)
13. [Out of Scope](#13-out-of-scope)
14. [Accessibility Requirements](#14-accessibility-requirements)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Open Questions](#16-open-questions)

---

## 1. Frontend Goal

Build a simple, student-facing UI that connects directly to the existing FastAPI backend.

The frontend's only job during MVP:
1. Collect a student profile via a form
2. Submit it to `POST /profile/` and `POST /score/all`
3. Display ranked scholarship results with score, label, gap analysis, and action checklist

No auth. No dashboard. No saved state between sessions. No marketing pages.
The backend is the source of truth — the UI only renders what the API returns.

---

## 2. Premium Design Goal

ScholarBridge must feel like a **serious financial and education platform**, not a class project.

International students applying for scholarships are making high-stakes decisions about funding
their education — often with $50,000–$90,000 per year on the line. The UI must reflect that weight.
It must feel **trustworthy, polished, and competent** from the first second.

**Design north star:**
> A student opening ScholarBridge for the first time should feel the same confidence they would
> feel opening a well-designed fintech or edtech product — not a generic CRUD app.

**What "premium" means for this product:**
- Clean and uncluttered — every element earns its space
- Visually confident — strong typography hierarchy, intentional spacing
- Trustworthy — consistent design language, no cheap-looking components
- Student-first — language and layout choices that reduce anxiety, not add to it
- Transparent — scores, requirements, and gaps explained, never hidden

**What "premium" does not mean for MVP:**
- Not flashy or animation-heavy
- Not complex — simplicity is the premium choice here
- Not overcrowded with features
- Not making claims the backend cannot support

---

## 3. Recommended Stack

| Technology | Choice | Reason |
|---|---|---|
| **Framework** | Next.js 14 (App Router) | React server components, built-in routing, TypeScript support, easy deployment |
| **Styling** | Tailwind CSS | Utility-first, mobile-first by default, excellent for consistent design systems |
| **Language** | TypeScript | Catches type mismatches against API response shapes at build time |
| **HTTP client** | Fetch API (native) | No extra dependency for MVP |
| **State** | React `useState` / `useReducer` | No global state manager needed for a 3-page MVP |
| **Form** | React Hook Form | Handles validation, error display, and field registration cleanly |
| **Font** | Inter (via `next/font/google`) | Modern, highly legible, widely trusted in fintech/edtech products |
| **Package manager** | npm | Consistent with standard Next.js setup |

> Do not use SWR, React Query, Redux, or Zustand during MVP. The data flow is simple enough
> that native `useState` + `fetch` is sufficient.

---

## 4. Visual Style Direction

The visual language is **clean fintech/edtech-inspired** — premium but minimal.

| Principle | Implementation |
|---|---|
| **Whitespace-first** | Generous padding inside cards and sections. Content breathes. Nothing crammed. |
| **Rounded cards** | `border-radius: 16px` or Tailwind `rounded-2xl` for all cards. Soft, not sharp. |
| **Subtle shadows** | `box-shadow` that lifts cards gently. Not dramatic drop shadows. `shadow-sm` / `shadow-md` in Tailwind. |
| **Soft gradients** | Used sparingly — hero section background only. Not on cards or buttons. |
| **Clear hierarchy** | One H1 per page, one primary action per section. Nothing competes for attention. |
| **No clutter** | If an element cannot be justified, it is removed. |
| **No excessive animation** | Hover state transitions at 150ms max. No scroll-triggered animations, no particle effects. |
| **Consistent spacing** | Use an 8px spacing grid throughout (Tailwind's default scale works). |
| **Card-based sections** | Form sections, result cards, and info panels use a consistent card container style. |

---

## 5. Color Direction

| Role | Color | Notes |
|---|---|---|
| **Primary** | Deep navy `#1E3A5F` or `#0F2D54` | Trust, stability, authority. Used for headings, primary buttons, and navbar. |
| **Accent** | Emerald green `#059669` or gold `#D97706` | Opportunity, success. Used for CTAs and Strong Match badges. Emerald preferred. |
| **Background** | Soft off-white `#F8FAFC` or light blue-gray `#F1F5F9` | Prevents harshness of pure white. Used as page background. |
| **Card surface** | Pure white `#FFFFFF` | Cards lift off the soft background. |
| **Border** | Light gray `#E2E8F0` | Subtle card borders and dividers. |
| **Text primary** | Near-black `#0F172A` | Main body and heading text. |
| **Text secondary** | Slate `#64748B` | Labels, captions, microcopy. |
| **Error** | Accessible red `#DC2626` | Backend 422 errors. Must meet 4.5:1 contrast on white background. |
| **Strong Match badge** | Green `bg-emerald-100` / `text-emerald-800` | Score >= 90% |
| **Good Match badge** | Blue `bg-blue-100` / `text-blue-800` | Score 70–89% |
| **Possible Match badge** | Amber `bg-amber-100` / `text-amber-800` | Score 40–69% |
| **Deadline — urgent** | Red or amber | When deadline is within 30 days |
| **Deadline — normal** | Slate | When deadline is > 30 days away |

> Color is never the only signal — all badges use both color and text label.
> All color choices must pass WCAG AA contrast checks.

---

## 6. Typography Direction

| Element | Style | Tailwind classes (approximate) |
|---|---|---|
| **Page H1** | Bold, 36–48px, navy | `text-4xl font-bold text-slate-900` |
| **Section heading H2** | Semibold, 24–28px | `text-2xl font-semibold text-slate-800` |
| **Card title** | Semibold, 18–20px | `text-lg font-semibold text-slate-900` |
| **Body text** | Regular, 16px | `text-base text-slate-700` |
| **Form label** | Medium, 14px | `text-sm font-medium text-slate-700` |
| **Microcopy / helper** | Regular, 13px, muted | `text-xs text-slate-500` |
| **Error text** | Regular, 13px, red | `text-xs text-red-600` |
| **Badge text** | Semibold, 12px | `text-xs font-semibold` |
| **Font family** | Inter (via `next/font/google`) | `font-sans` after configuring Tailwind config |

**Typography rules:**
- Never use a decorative or playful font (no Pacifico, Lobster, display serifs)
- Never use all-caps for body text
- Line height should be comfortable: `leading-relaxed` for body, `leading-tight` for headings
- Use font weight intentionally — bold only for headings and key numbers

---

## 7. MVP Pages

| Route | Page | Purpose |
|---|---|---|
| `/` | Home | Entry point — one strong headline, trust indicators, single CTA |
| `/profile` | Profile Form | Collect student data, grouped into sections, submit to backend |
| `/results` | Results | Display ranked scholarship cards returned by scorer |

No other routes are planned for MVP.

---

## 8. Page Details

### 8.1 Home Page (`/`)

**Purpose:** Establish trust immediately. Explain what ScholarBridge does in one sentence. Drive the user
to the profile form.

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR  — ScholarBridge logo (left)                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  HERO SECTION (soft gradient background)            │
│                                                     │
│  [H1] Find scholarships you actually qualify for.   │
│  [Sub] Profile-based matching for international     │
│  students in the US. Transparent scores. No guessing│
│                                                     │
│  [ Find Scholarships → ]   (primary CTA button)     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  TRUST INDICATOR STRIP                              │
│  ✓ Profile-based matching                           │
│  ✓ Transparent eligibility scores                   │
│  ✓ Official source links                            │
│  ✓ No applications taken here                       │
└─────────────────────────────────────────────────────┘
```

**Rules:**
- H1 is a single confident statement about the product's value — not a tagline
- Subheading specifically mentions international students and transparency
- One CTA only — "Find Scholarships" — linking to `/profile`
- Trust indicator strip uses checkmark icons and short factual phrases
- No testimonials, stats, marketing copy, or growth-hacking language
- No image placeholders or stock photos

---

### 8.2 Profile Form Page (`/profile`)

**Purpose:** Collect the student profile in a structured, low-anxiety form experience.

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR                                             │
├─────────────────────────────────────────────────────┤
│  Page heading: "Tell us about yourself"             │
│  Subheading: "We'll match your profile against..."  │
│                                                     │
│  FORM PROGRESS INDICATOR  ●●●○○○  (3 of 6 sections) │
│                                                     │
│  ┌─── SECTION CARD: Personal ────────────────────┐ │
│  │  Full name, Date of birth, Nationality,        │ │
│  │  Home country, Gender (opt), Home city (opt)   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── SECTION CARD: Academic ────────────────────┐ │
│  │  Degree level, Field of study, Major,          │ │
│  │  University, State, GPA, GPA scale,            │ │
│  │  Graduation year, Test scores (opt)            │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── SECTION CARD: Visa & Enrollment ───────────┐ │
│  │  Visa type, Enrollment status,                 │ │
│  │  First-generation student (opt)               │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── SECTION CARD: Achievements ────────────────┐ │
│  │  Published research, Conference presentations, │ │
│  │  Patents, Leadership roles (opt),              │ │
│  │  Entrepreneurship experience, Volunteer (opt)  │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── SECTION CARD: Financial Need ──────────────┐ │
│  │  Financial need level,                         │ │
│  │  Income bracket (opt), Dependents (opt)        │ │
│  │  [Microcopy: This information helps filter...] │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─── SECTION CARD: Preferences (optional) ──────┐ │
│  │  Career goals, Intended industry,              │ │
│  │  Willing to return home, Languages,            │ │
│  │  Preferred scholarship types                   │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  [ Find My Scholarships → ]  (primary submit btn)  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Form sections** (maps directly to `StudentProfile` fields from `docs/API.md § 1`):

| Section | Required fields | Optional fields |
|---|---|---|
| **Personal** | `full_name`, `date_of_birth`, `nationality`, `home_country` | `gender`, `home_city`, `dual_citizenship` |
| **Academic** | `degree_level`, `field_of_study`, `major`, `university_name`, `university_state`, `gpa`, `gpa_scale`, `expected_graduation_year` | `minor`, `gre`, `gmat`, `toefl`, `ielts`, `sat`, `act`, `previous_degrees` |
| **Visa & Enrollment** | `visa_type`, `enrollment_status` | `first_generation_student` |
| **Achievements** | `published_research`, `conference_presentations`, `patents`, `entrepreneurship_experience` | `research_papers`, `academic_awards`, `previous_scholarships`, `leadership_roles`, `volunteer_hours`, `sports_achievements`, `artistic_achievements` |
| **Financial Need** | `financial_need_level` | `family_income_bracket`, `dependents`, `current_funding_sources` |
| **Preferences** | *(all optional)* | `career_goals`, `intended_industry`, `willing_to_return_home_country`, `languages`, `preferred_scholarship_types` |

**Form UX details:**

- Each section is a distinct card with a section title — no single long scrolling form
- Required fields are marked with `*` and a subtle note at the top: "Fields marked * are required"
- Optional fields are labeled "(optional)" inline on the label
- **Microcopy examples:**
  - Below `financial_need_level`: "This helps filter scholarships with financial need requirements. It is never shared externally."
  - Below `gpa`: "Enter your GPA on your institution's scale (e.g. 3.8 / 4.0)."
  - Below `nationality`: "Use ISO 3166-1 alpha-2 country code (e.g. IN for India, CN for China, NG for Nigeria)."
- Inline validation errors appear below the specific field that failed (not at the top of the page)
- Error text is red, accessible, associated with the input via `aria-describedby`
- Submit button shows a loading spinner while API calls are in flight
- List fields (`leadership_roles`, `languages`, `academic_awards`, etc.) accept comma-separated input for MVP — split by the frontend before sending

---

### 8.3 Results Page (`/results`)

**Purpose:** Display ranked scholarship cards in a polished, scannable layout that helps students
prioritize and act.

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR                                             │
├─────────────────────────────────────────────────────┤
│  "Your Scholarship Matches"                         │
│  Profile completeness: 85%   [ Edit Profile ]       │
│                                                     │
│  N scholarships matched your profile.               │
│                                                     │
│  ┌─── SCHOLARSHIP CARD ──────────────────────────┐ │
│  │  [Strong Match ●] [Deadline: Dec 31 · 202 days]│ │
│  │                                                │ │
│  │  Scholarship Name                              │ │
│  │  Organisation Name                             │ │
│  │                                                │ │
│  │  Score: 83.3%  ████████░░ (visual bar)         │ │
│  │                                                │ │
│  │  Why you matched:                              │ │
│  │    ✓ Degree level matches                      │ │
│  │    ✓ Entrepreneurship experience confirmed     │ │
│  │                                                │ │
│  │  ▼ What you're missing (gap analysis)          │ │
│  │    · GPA >= 3.5  (yours: 3.2)                  │ │
│  │    · First-generation student not confirmed    │ │
│  │                                                │ │
│  │  ▼ What to prepare (action checklist)          │ │
│  │    ☐ Personal statement required               │ │
│  │                                                │ │
│  │  [ Apply / Official Source → ]                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  (more cards below...)                              │
│                                                     │
│  Footer note:                                       │
│  "Scores are based on your profile. Always verify   │
│   eligibility directly on the official source."     │
└─────────────────────────────────────────────────────┘
```

**Each scholarship card must display:**

| Element | Source field | Display detail |
|---|---|---|
| Match label badge | `match_label` | Color-coded pill: Strong Match (green), Good Match (blue), Possible Match (amber) |
| Deadline badge | `deadline` | ISO date + days remaining. Red if <= 30 days, amber if 31–60, normal if > 60 |
| Scholarship name | `name` | Prominent, 18–20px semibold |
| Organisation | `org_name` | Secondary, 14px muted |
| Score | `score` | Large numeric display + visual progress bar (e.g., `83.3%`) |
| "Why you matched" | *(derived)* | Short summary of matched features — 2–3 bullet points max |
| Gap analysis | `gap_analysis` | Collapsible panel: "What you're missing". Each item shows `label` + `requirement` + student value where non-null |
| Action checklist | `action_checklist` | Collapsible panel: "What to prepare". Each item is a UI-only checkbox (not persisted) |
| Apply link | `source_url` | Prominent button: "Apply / Official Source →". Opens in new tab. `rel="noopener noreferrer"`. |

**Empty state:** If the backend returns an empty list (`[]`), show a friendly card explaining:
- "No scholarships matched your current profile above the 40% threshold"
- Suggestions: fill in more optional fields, check profile completeness
- Button to go back and edit profile

**Footer note on every results page:**
> "Match scores are based on the information in your profile.
> Always verify eligibility and deadlines directly on the official scholarship website before applying."

This note is non-negotiable — it ensures the product never implies a scholarship guarantee.

---

## 9. API Integration Plan

### Endpoints used

| Endpoint | When | Purpose |
|---|---|---|
| `POST /profile/` | On form submit | Create and store the student profile; receive `profile_id` |
| `POST /score/all` | Immediately after profile creation | Score all scholarships and return ranked results |
| `GET /profile/{profile_id}/completeness` | On results page | Show completeness percentage |

### Sequence on form submit

```
User clicks "Find My Scholarships"
    │
    ▼
Validate required fields client-side (React Hook Form)
    │── client validation fails → show inline errors, do not call API
    │
    ▼
POST /profile/                        ← trailing slash required
    body: { ...StudentProfile fields }
    │── 422 → display field-level errors inline, stop
    │── network error → show ErrorAlert with retry button
    │── 201 → receive { profile_id, completeness, message }
    │
    ▼
POST /score/all
    body: { profile_id }
    │── 404 → show ErrorAlert (profile not found — should not occur in normal flow)
    │── network error → show ErrorAlert with retry button
    │── 200 → receive list of ScoringResult objects
    │
    ▼
Navigate to /results
    Pass results + completeness via sessionStorage or React context
    Render ScholarshipCard for each result
```

### TypeScript interfaces

```typescript
// Mirrors ScoringResult from backend/app/scorer/models.py
interface ScoringResult {
  scholarship_id: string;
  name: string;
  org_name: string;
  score: number;
  match_label: "Strong Match" | "Good Match" | "Possible Match" | "Below Threshold";
  deadline: string | null;
  source_url: string;
  gap_analysis: FeatureMatchDetail[];
  action_checklist: string[];
}

// Mirrors FeatureMatchDetail from backend/app/scorer/models.py
interface FeatureMatchDetail {
  field: string;
  label: string;
  requirement: string;
  student_value: unknown;
}

// Mirrors CreateProfileResponse from backend/app/api/profile_router.py
interface CreateProfileResponse {
  profile_id: string;
  completeness: number;
  message: string;
}
```

### Base URL configuration

```
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Configured via `.env.local` (local dev) or the deployment platform's environment settings.

### Important: trailing slash on POST /profile/

`POST /profile/` requires a trailing slash. Without it, FastAPI returns `307 Temporary Redirect`.

```typescript
const response = await fetch(`${API_BASE}/profile/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(profileData),
});
```

---

## 10. Component Plan

All components live under `frontend/components/`. Pages compose components — pages contain no UI logic.
API calls live in `frontend/lib/api.ts` — never inside components.

### Layout components

| Component | File | Responsibility |
|---|---|---|
| `AppShell` | `components/AppShell.tsx` | Top-level wrapper providing consistent page padding and max-width container |
| `Navbar` | `components/Navbar.tsx` | Logo left, product name, optional nav links. Sticky on scroll. |

### Home page components

| Component | File | Responsibility |
|---|---|---|
| `HeroSection` | `components/HeroSection.tsx` | H1, subheading, CTA button. Soft gradient background. |
| `TrustIndicatorStrip` | `components/TrustIndicatorStrip.tsx` | Row of 4 short trust phrases with checkmark icons |

### Profile form components

| Component | File | Responsibility |
|---|---|---|
| `ProfileFormSection` | `components/ProfileFormSection.tsx` | Reusable card container for one form section (Personal, Academic, etc.). Accepts `title` and `children`. |
| `FormProgress` | `components/FormProgress.tsx` | Visual progress indicator showing which sections are filled. Props: `completed: number`, `total: number`. |

### Results page components

| Component | File | Responsibility |
|---|---|---|
| `ScholarshipCard` | `components/ScholarshipCard.tsx` | Full scholarship result card. Receives one `ScoringResult` as props. Composed of sub-components below. |
| `MatchScoreBadge` | `components/MatchScoreBadge.tsx` | Color-coded pill showing `match_label`. Props: `score: number`, `match_label: string`. |
| `DeadlineBadge` | `components/DeadlineBadge.tsx` | Shows deadline date + days remaining with urgency color. Props: `deadline: string | null`. |
| `GapAnalysisPanel` | `components/GapAnalysisPanel.tsx` | Collapsible "What you're missing" panel. Props: `items: FeatureMatchDetail[]`. |
| `ActionChecklistPanel` | `components/ActionChecklistPanel.tsx` | Collapsible "What to prepare" panel with UI-only checkboxes. Props: `items: string[]`. |

### Shared utility components

| Component | File | Responsibility |
|---|---|---|
| `LoadingSkeleton` | `components/LoadingSkeleton.tsx` | Skeleton placeholder cards shown while API calls are in-flight. No spinner-only states. |
| `ErrorAlert` | `components/ErrorAlert.tsx` | Top-level or inline error banner. Props: `message: string`, `onRetry?: () => void`. |
| `EmptyState` | `components/EmptyState.tsx` | Friendly message when no results are returned. Props: `message: string`, `actionLabel?: string`, `onAction?: () => void`. |

---

## 11. UX Principles

| Principle | Implementation |
|---|---|
| **Student-first language** | "Find scholarships you qualify for" not "Run scoring algorithm". Use plain English throughout. |
| **Transparent scoring** | Show the score number and the label. Explain what contributes to the score in the "Why you matched" section. Never hide the score. |
| **Never guarantee awards** | No language like "You will win" or "You qualify." Use "You matched" or "This scholarship is likely eligible based on your profile." |
| **Always link to source** | Every card has a prominent "Apply / Official Source" link. The UI is a discovery tool, not an application portal. |
| **Encourage verification** | Footer note on results page is mandatory. Students must be reminded to verify eligibility directly. |
| **Sensitive fields explained** | Financial need fields include microcopy explaining what the data is used for and that it is not shared. |
| **Optional fields are truly optional** | Never block submission because optional fields are empty. Form must be submittable with only required fields. |
| **Mobile-first experience** | Form sections stack vertically on mobile. Cards are full-width on small screens. |
| **Accessible contrast** | All text/background combinations meet WCAG AA 4.5:1 minimum. Error red meets contrast on white. |
| **Keyboard navigation** | Every interactive element is reachable via Tab. Forms submit on Enter. Modals/panels close on Escape. |
| **No anxiety patterns** | No countdown timers, no "X other students are searching now," no urgency manufactured by the UI (only real deadline urgency from the API). |

---

## 12. User Flow

```
/ (Home)
  │
  └─→ "Find Scholarships" button
          │
          ▼
    /profile (Profile Form — 6 card sections)
          │
          │  User fills required fields
          │  Optionally fills optional fields
          │  Clicks "Find My Scholarships"
          │
          │── Client validation fails ──→ inline field errors, stay on /profile
          │
          ▼
    POST /profile/ (201)
          │
          │── 422 error ──→ inline field-level errors from backend, stay on /profile
          │── network error ──→ ErrorAlert with retry, stay on /profile
          │
          ▼
    POST /score/all (200)
          │
          │── network error ──→ ErrorAlert with retry, stay on /profile
          │
          ▼
    /results (Results Page)
          │
          ├─→ User scans scholarship cards sorted by score (descending)
          │       · MatchScoreBadge + score % immediately visible
          │       · DeadlineBadge shows urgency
          │       · Expands GapAnalysisPanel → sees what requirements are unmet
          │       · Expands ActionChecklistPanel → sees what to prepare
          │       · Clicks "Apply / Official Source" → new tab → official scholarship page
          │
          └─→ "Edit Profile" → back to /profile → resubmit
```

---

## 13. Out of Scope

The following are explicitly **not planned** for Phase 10 MVP UI:

| Out of Scope | Reason |
|---|---|
| Login / authentication | No user accounts in backend |
| User dashboard | Requires persistent session |
| Saved scholarships | Requires database persistence |
| Scholarship comparison view | Post-MVP feature |
| Payments or premium tier | Not in PRD |
| ML-based recommendations | Backend uses rule-based scoring only |
| Chatbot or AI assistant | Post-MVP, not in PRD |
| Web scraping of live scholarships | Static JSON backend only |
| Admin portal | No admin roles |
| Email notifications | Post-MVP |
| Essay generation or AI writing assistance | Post-MVP |
| Social sharing | Post-MVP |
| Multi-language UI | Post-MVP |
| Analytics or event tracking | No users yet |
| Dark mode toggle | Post-MVP polish |
| Scholarship bookmarking | No persistence in MVP |

---

## 14. Accessibility Requirements

WCAG 2.1 AA is the minimum standard. Per `docs/AI_RULES.md § 5`.

| Requirement | Implementation |
|---|---|
| **Mobile-first layout** | Tailwind responsive prefixes applied from smallest breakpoint up (`sm:`, `md:`, `lg:`) |
| **Keyboard accessible** | All interactive elements reachable via Tab, activated via Enter/Space |
| **Labels on all inputs** | Every `<input>` and `<select>` has an associated `<label>`. No placeholder-as-label. |
| **Error messages tied to fields** | `aria-describedby` associates `<ErrorAlert>` text with the specific failing input |
| **Focus states visible** | `focus:ring-2 focus:ring-offset-2` applied to all buttons, inputs, and links |
| **Color is not the only indicator** | Match label badges use both color and text. Deadline urgency uses text in addition to color. |
| **Links that open new tabs** | `aria-label="[Scholarship name] — official source (opens in new tab)"` |
| **Sufficient color contrast** | All foreground/background pairs >= 4.5:1 (normal text), >= 3:1 (large text / UI components) |
| **No motion without preference** | Transitions respect `prefers-reduced-motion` media query |
| **Semantic HTML** | `<main>`, `<nav>`, `<section>`, `<article>`, `<header>`, `<footer>` used correctly |
| **Form landmark** | Profile form wrapped in `<form>` with accessible submit button |
| **Skip to main content** | A visually hidden skip link at the top of every page for keyboard users |

---

## 15. Acceptance Criteria

### Functional

| # | Criterion | How to verify |
|---|---|---|
| AC-01 | User can fill required profile fields and submit successfully | Manual: submit a valid profile, receive results |
| AC-02 | Backend 422 validation errors display inline on the specific field | Manual: submit `gpa: 5.0`, see GPA field error |
| AC-03 | Network errors show an `ErrorAlert` banner with a retry button | Manual: stop backend, submit form |
| AC-04 | User can see ranked scholarship cards with score %, label, deadline, and apply link | Manual: verify card content against API response |
| AC-05 | User can open `source_url` in a new tab | Manual: click Apply button |
| AC-06 | Gap analysis is visible and shows the correct requirements | Manual: expand gap analysis, verify labels match API response |
| AC-07 | Action checklist is visible and shows the correct preparation items | Manual: expand action checklist, verify items |
| AC-08 | Empty state appears when no scholarships score above 40% | Manual: use a profile that matches no scholarships |
| AC-09 | Edit Profile button navigates back to `/profile` | Manual: click Edit Profile on results page |
| AC-10 | `python3 -m pytest tests/ -v` still passes (no backend regressions) | Run tests after frontend is set up |

### Design

| # | Criterion | How to verify |
|---|---|---|
| AC-11 | UI looks professional enough to show in a demo — not a basic class project | Visual review by a person unfamiliar with the codebase |
| AC-12 | User can complete the profile form without confusion | Usability test with one observer |
| AC-13 | Results are easy to scan and compare (score and label immediately visible without scrolling) | Visual review on a 375px screen |
| AC-14 | Match scores are visually clear — number + label + color badge all present | Visual review |
| AC-15 | Official source links are obvious (not a text link buried in the card) | Visual review |
| AC-16 | No clutter above the fold on the home page | Visual review on 375px and 1280px |
| AC-17 | No false claims, guarantees, or overpromising language anywhere in the UI | Copy review |

### Accessibility

| # | Criterion | How to verify |
|---|---|---|
| AC-18 | Mobile layout (375px) is clean and usable | Browser DevTools responsive mode |
| AC-19 | Desktop layout (1280px) is clean and usable | Browser at full width |
| AC-20 | All form inputs are keyboard accessible | Tab through entire form, submit with Enter |
| AC-21 | All interactive elements have visible focus states | Tab through page, verify no invisible focus rings |
| AC-22 | Color contrast passes WCAG AA | Browser accessibility audit (Lighthouse or axe DevTools) |

---

## 16. Open Questions

These questions should be resolved before implementation begins:

| # | Question | Impact |
|---|---|---|
| OQ-01 | Where will the frontend be hosted? (Vercel, Netlify, self-hosted) | Affects `NEXT_PUBLIC_API_BASE_URL` strategy and CORS policy on the backend |
| OQ-02 | Will the backend be deployed or remain local-only during UI testing? | Determines whether CORS `allow_origins=["*"]` needs to be tightened |
| OQ-03 | Should results persist across page refreshes? | If yes: `sessionStorage`. If no: results lost on refresh (acceptable for MVP). |
| OQ-04 | Should list fields (`academic_awards`, `leadership_roles`, `languages`) appear in the form? | If yes: comma-separated text input for MVP. If no: they default to `[]` silently. |
| OQ-05 | Date of birth: native date picker or plain `YYYY-MM-DD` text input? | Date pickers add complexity; plain text with format hint is simpler for MVP. |
| OQ-06 | Is the "Why you matched" section derived on the frontend or returned by the backend? | Currently the backend returns `gap_analysis` (unmatched) but not a "matched features" list. If needed, the frontend can derive matched features from `gap_analysis` being absent for a feature — or the backend can be extended in a future phase. |

---

*Phase 10 plan updated June 12, 2026 — premium design direction added.*
*Backend phases 0–9 complete. No frontend code written yet. Awaiting approval to proceed.*
