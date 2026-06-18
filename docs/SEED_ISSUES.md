# Seed Issues — copy/paste into GitHub (tag each `good first issue` + `help wanted`)

These are scoped for AI coding agents (Copilot/Cursor) AND human contributors.
Each has Goal / Files / Acceptance / Test so an agent can be assigned and ship a PR.
**Pin issue #1** with the note: "👋 New here? Try assigning this to GitHub Copilot or opening it in Cursor."

---

## 1. [good first issue] Add clause rules for Canada (PIPEDA)
**Goal:** Detect & generate PIPEDA (Canadian privacy law) clauses.
**Files:** `app/clause_rules.py` (add rule), `app/scanner.py` (auto-picks up rules), `tests/test_scanner.py` (add a case).
**Acceptance:** Scanner flags missing PIPEDA language on a Canadian-context policy; a new rule entry exists; tests pass.
**Test:** `pytest tests/test_scanner.py`
**Agent tip:** read `AGENTS.md` and `.github/instructions/clause-rules.instructions.md` first.

## 2. [good first issue] Add clause rules for Brazil (LGPD)
**Goal:** Same pattern as GDPR, for Brazil's LGPD.
**Files:** `app/clause_rules.py`, `tests/test_scanner.py`.
**Acceptance:** New LGPD rule; scanner detects presence/absence; tests pass.
**Test:** `pytest tests/test_scanner.py`

## 3. [good first issue] Add clause rules for Australia (Privacy Act)
**Goal:** Detection + generated-doc section for the Australian Privacy Act / APPs.
**Files:** `app/clause_rules.py`, `tests/test_scanner.py`.
**Acceptance:** New rule; detection works; tests pass.
**Test:** `pytest tests/test_scanner.py`

## 4. [good first issue] Scanner: detect a missing "last updated" date
**Goal:** Flag policies that have no last-updated date stamp.
**Files:** `app/scanner.py`, `tests/test_scanner.py`.
**Acceptance:** A policy with no date is flagged; one with a date is not.
**Test:** `pytest tests/test_scanner.py`

## 5. [good first issue] Add a `--json` output mode to the scanner
**Goal:** Let the scanner emit machine-readable JSON (for CI/automation).
**Files:** `app/scanner.py` (or a small CLI wrapper).
**Acceptance:** Running with `--json` prints valid JSON with score + results.
**Test:** `pytest` (add a small test asserting JSON shape)

## 6. [good first issue] Translate the generated Privacy Policy to Spanish
**Goal:** Offer a Spanish-language Privacy Policy template.
**Files:** `templates/` (doc templates), `app/generator.py` if a language toggle is needed.
**Acceptance:** Generator can output a Spanish privacy policy; existing tests pass.
**Test:** `pytest`

## 7. [good first issue] Add a dark-mode stylesheet
**Goal:** Respect `prefers-color-scheme: dark`.
**Files:** `static/style.css`.
**Acceptance:** Site is legible in dark mode; no layout breakage.
**Test:** manual (screenshot in PR)

## 8. [good first issue] Document deploying to Fly.io / Railway
**Goal:** Add alt-deploy guides beyond Render.
**Files:** `docs/SELF_HOSTING.md`.
**Acceptance:** Clear step-by-step for at least one of Fly.io or Railway.
**Test:** n/a (docs)

---

## Labels to create first
- `good first issue` (default GitHub label exists)
- `help wanted` (default exists)
- `agent-friendly` (new — color #7057ff) — "well-scoped for AI coding agents"
- `clause-rules` (new) · `docs` (default) · `tests` (new)
