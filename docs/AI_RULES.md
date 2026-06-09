# AI_RULES.md — ScholarBridge AI Governance Rules

> **Enforcement Level: Mandatory**
> These rules govern every AI agent, every contributor, and every code session on the ScholarBridge
> project. Violating these rules is a blocker. No exceptions during MVP.

---

## 1. Read-First Requirement

Before writing a single line of application code, every AI agent and every contributor **must** read the
following documents in full:

1. `docs/AI_RULES.md` (this file)
2. `docs/PRD.md`
3. `docs/ARCHITECTURE.md`
4. `docs/PLAN.md`

These four files are the **sole source of truth** for this project. If any of them are missing, **STOP**
immediately and create them before proceeding.

---

## 2. Golden Rules

| Rule | Enforcement |
|---|---|
| Do not rewrite working code unnecessarily. | Hard block |
| Do not add frameworks because they are trendy. | Hard block |
| Do not create mock production functionality. | Hard block |
| Do not hardcode scholarship-specific logic in the scorer. | Hard block |
| Do not hardcode user-specific logic in the matcher. | Hard block |
| Do not commit secrets of any kind. | Hard block |
| Never commit `.env` files. | Hard block |
| Never expose API keys in code or logs. | Hard block |
| Never delete large sections of code without written explanation. | Hard block |
| If two implementations satisfy the same requirement, choose the simpler one. Complexity requires explicit justification. | Hard block |
| Before creating any new top-level folder, explain why it is needed and why existing folders are insufficient, then wait for approval. | Hard block |

---

## 3. MVP First Rule

The following systems are **prohibited** until MVP is declared complete:

| Prohibited System | Why |
|---|---|
| ML ranking (LightGBM, LambdaRank) | No training data exists yet |
| RLHF feedback loops | Requires real user sessions |
| Pinecone or Weaviate vector databases | No embeddings generated yet |
| Vector similarity search | MVP uses exact feature matching |
| Agent orchestration (LangGraph, CrewAI) | MVP agents are stateless functions |
| Multi-agent systems | One-agent-at-a-time during MVP |
| Live web scraping (Playwright, Scrapy) | MVP uses static JSON data only |
| Recommendation engines | Requires user behavior data |
| Analytics dashboards | No users yet |
| PostgreSQL persistence | MVP uses JSON files |
| Redis caching | Not needed at MVP scale |
| BGE-M3 or text-embedding-3-large embeddings | Vector search is post-MVP |

**The MVP must work before any of the above is introduced.**

---

## 4. Phase Discipline

- AI agents **must** work exactly one PLAN.md phase at a time.
- Skipping phases is prohibited.
- Jumping ahead to a later phase is prohibited.
- At the end of each phase, the agent **must STOP** and wait for explicit human approval.
- The agent must report: Current Phase | Repository Findings | Files Changed | Verification | Tests | Blockers | Next Recommended Phase.

---

## 5. UI Rules

When the frontend phase is active (per PLAN.md), the following rules govern UI development:

**Required:**
- Mobile-first layout
- Accessibility-first (WCAG 2.1 AA minimum)
- Clean scholarship cards displaying:
  - Eligibility score (e.g., `78%`)
  - Match label (Strong Match / Good Match / Possible Match)
  - Application deadline
  - Source URL (clickable, opens in new tab)
  - Action checklist (output-type features listed as tasks)
  - Gap analysis (which required features the student does not satisfy)

**Prohibited:**
- Fancy animations or CSS transitions unrelated to usability
- Marketing language or growth-hacking copy
- Dashboard clutter (more than 3 widgets above the fold)

---

## 6. Backend Rules

All backend code **must** conform to the following:

- Framework: **FastAPI** only
- Validation: **Pydantic v2** only — no raw dict manipulation
- Language: **Typed Python** — all functions must have full type annotations
- Testability: Every business logic function must be callable independently (no side effects embedded in routes)
- Separation of concerns: API routes (`api/`) may **never** contain business logic. Business logic lives in `scorer/` and `agents/`.
- All exceptions must be handled — no bare `except:` clauses

---

## 7. Data Rules

Every scholarship record in `data/scholarships/` **must** contain:

| Required Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (UUID or slug) |
| `name` | string | Full scholarship name |
| `org_name` | string | Awarding organization |
| `country` | string | ISO 3166-1 alpha-2 country code |
| `source_url` | string | Canonical URL for the scholarship |
| `last_verified` | date string | ISO 8601 date of last manual verification |
| `deadline` | date string | ISO 8601 application deadline |
| `feature_manifest` | object | Structured eligibility requirements (see ARCHITECTURE.md) |

Records missing any of the above fields **must not** be loaded into the system. Schema validation runs at load time and rejects non-conforming records loudly (not silently).

---

## 8. Scoring Rules

The scoring formula is:

```
Score = (M / T) × 100
```

Where:
- **M** = Number of scholarship features the student's profile satisfies
- **T** = Total number of features in the scholarship's `feature_manifest`

**Enforcement:**
- Output-type features (essays, recommendation letters, writing samples) **always** contribute `0` to M but **always** count toward T.
- Hard pre-filters (`deadline`, `citizenship`, `degree`, `visa`) run **before** scoring. A scholarship that fails a hard pre-filter never reaches the M/T calculation.
- **Age is NOT a hard pre-filter.** If a scholarship specifies an age requirement and the student profile does not include age, the scholarship remains eligible. The age feature is evaluated in the feature manifest and counted as unmatched — the score decreases naturally. Missing age must never block a scholarship.
- The scorer must never special-case individual scholarships. Logic must be driven by the feature manifest structure.
- Results below 40% score must be excluded from the returned ranked list.
- `score_test` is a **deferred feature type** — it is not implemented during MVP. Specification is not finalized. Do not implement `score_test` in any MVP code.

---

## 9. Secret Management Rules

| Item | Rule |
|---|---|
| `.env` file | Never commit. Always in `.gitignore`. |
| `.env.example` | Always commit. Contains key names only, no values. |
| `ANTHROPIC_API_KEY` | Load from environment only |
| `OPENAI_API_KEY` | Load from environment only |
| `PINECONE_API_KEY` | Load from environment only (post-MVP) |
| `DATABASE_URL` | Load from environment only |
| `SERP_API_KEY` | Load from environment only |
| `SECRET_KEY` | Load from environment only |

---

## 10. Definition of Done

A task or phase is **complete only if all of the following are true**:

- [ ] Code runs without error
- [ ] Tests pass (`pytest` suite, 0 failures)
- [ ] API behavior has been demonstrated (curl output or test output shown)
- [ ] PRD requirements for this phase are satisfied
- [ ] ARCHITECTURE.md structure has not been violated
- [ ] PLAN.md phase deliverables are all present
- [ ] No prohibited system (Section 3) has been introduced

---

## 11. Commit Message Standard

All commits must follow this format:

```
[phase-N] short description of what changed

- Detail 1
- Detail 2
```

Example: `[phase-2] Add Pydantic v2 student profile model with completeness scoring`

---

*Last updated: June 09, 2026 — Governance update v1.1 (approved changes: anti-complexity rule, repo protection rule, age handling, score_test deferral, scholarship count requirement removed)*
