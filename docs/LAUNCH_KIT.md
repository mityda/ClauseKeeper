# ClauseKeeper — Open-Source Launch Kit

Playbook source: Starter Story / Nevo (posties, $17K MR). Goal of launch week: drive
maximum traffic in the shortest window → hit **GitHub Trending** → stars → word-of-mouth
+ SEO compounding forever. **Fire all of these in the SAME week.**

## Pre-launch checklist (do these first)
- [ ] Repo flipped **public** on GitHub
- [ ] README renders well (it's the real landing page) ✅ done
- [ ] LICENSE present (AGPL-3.0) ✅ done
- [ ] `docker compose up` verified on a machine **with Docker installed** (NOT verified here — this Mac has no Docker; do this on launch box or trust the standard Dockerfile)
- [ ] 5–8 GitHub issues created and tagged `good first issue` (drafts below)
- [ ] Discord server created; #general #self-hosting #contributing #showcase channels
- [ ] HackerNews account aged ≥2 weeks
- [ ] Reddit account with some karma (post in other subs first)
- [ ] dev.to / Medium / Hashnode accounts ready

---

## 1. Show HN (post link to the GitHub repo, NOT the website)

**Title:** `Show HN: ClauseKeeper – Open-source tool to keep your site's legal docs current`

**Body:**
> I kept watching indie founders ship with a copy-pasted privacy policy from 2021 — stale GDPR language, no CCPA, and nothing about AI disclosure even though the EU AI Act is now phasing in.
>
> ClauseKeeper is two things: a free, rule-based compliance scanner (paste your policy → 0–100 score + checklist of missing/stale clauses, no LLM, runs offline) and a generator for Privacy/ToS/Cookie/AI-disclosure documents with conditional clauses per jurisdiction.
>
> It's fully self-hostable (`docker compose up`, no API keys needed for the core). The hosted version just keeps the clause library current for you. AGPL-3.0.
>
> It's explicitly a *starting point, not legal advice* — I'd rather be honest about that than promise "guaranteed compliance."
>
> Repo: <github link> — would love feedback on the clause rules, especially from anyone in a non-US/EU jurisdiction.

---

## 2. Reddit — r/selfhosted (primary), crosspost r/opensource, r/webdev

**Title:** `I built an open-source tool to scan & generate your website's legal documents (self-hostable, no LLM)`

**Body:** (humble, building-in-public, use "I" not "we", ask for a star)
> Hey r/selfhosted — I just open-sourced ClauseKeeper. It scans your privacy policy / terms for missing or stale clauses (GDPR, CCPA, cookies, AI disclosure) and gives you a 0–100 score, and it can generate a fresh set of documents.
>
> Everything runs self-hosted with `docker compose up` — the scanner and generator need zero external keys or API calls (the scanner is 100% rule-based, no LLM). SQLite for storage so there's basically nothing to operate.
>
> It's AGPL-3.0. If it's useful, a GitHub star really helps me out. Happy to answer anything about the clause engine or add rules for jurisdictions I've missed.
>
> Repo: <github link>

> **Re-post every time there's a new version** with the changelog. r/selfhosted welcomes it.

---

## 3. dev.to / Medium / Hashnode article (SEO + Google Discover traffic)

**Title:** `How I built an open-source compliance scanner with FastAPI and zero LLM calls`
**Cover image:** clean, high-contrast (Discover feed is title+thumbnail driven — invest here)

Outline:
1. The problem — legal docs go stale, the law keeps moving (EU AI Act, US state laws)
2. Why rule-based, not an LLM (cost $0, deterministic, runs offline, auditable)
3. Architecture walkthrough — FastAPI + SQLite + Jinja, the clause-rules engine
4. The open-source-as-distribution decision (link the repo throughout)
5. How to self-host it in 2 minutes
6. CTA: star the repo, try the free scanner

Follow-up listicle (a week later): `7 open-source tools every indie founder should self-host in 2026` (include ClauseKeeper). Listicles farm stars + trending.

---

## 4. Lemmy

Post the same r/selfhosted content to a Lemmy instance's selfhosted/opensource community. Per the playbook, OSS posts on Lemmy reliably pull 100+ upvotes.

---

## 5. Owned channels (same week)

- X: thread version of the dev.to article, link to GitHub
- LinkedIn: the "why I open-sourced it" angle
- The ClauseKeeper X writer cron can amplify — point it at the GitHub repo during launch week

---

## Seed GitHub Issues (create these, tag `good first issue`)

1. **Add clause rules for Canada (PIPEDA)** — extend `app/clause_rules.py` with PIPEDA detection + a generated-doc section.
2. **Add clause rules for Brazil (LGPD)** — same pattern as GDPR, new jurisdiction.
3. **Add clause rules for Australia (Privacy Act)** — detection + generator section.
4. **Improve scanner: detect a missing "last updated" date** — heuristic in `app/scanner.py`.
5. **Add a `--json` output mode to the scanner** for CI/automation use.
6. **Translate the generated Privacy Policy to Spanish** — template work in `templates/`.
7. **Add a dark-mode stylesheet** to `static/style.css`.
8. **Document deploying to Fly.io / Railway** in `docs/SELF_HOSTING.md` (alt to Render).

Each issue: short description, point to the file, label `good first issue` + `help wanted`.
This is THE step most people skip — pre-made issues are how you actually get contributions.

---

# Agent-Native Launch Track (GitHub Agent HQ + Cursor/Graphite)

Research (mid-2026, CONFIRMED from official sources):
- **Cursor's "forge"** = Cursor acquired **Graphite** (Dec 2025), a GitHub-synced
  code-review/PR platform; **Cursor Cloud Agents in Graphite** (Mar 2026) let agents
  open/review/merge PRs in-browser. It is NOT a standalone GitHub-replacement repo host
  (as of this research). It works THROUGH GitHub PRs/issues — so good GitHub repo
  conventions are what matter.
- **GitHub Agent HQ** (Oct 2025): agents native to GitHub flow; Copilot coding agent
  works assigned issues; reads AGENTS.md + .github/copilot-instructions.md.
- **GitHub Copilot app** GA (Jun 2026): agent-native desktop, cloud automations.
- **GitHub MCP Registry** (Sep 2025): MCP servers discovered + sorted by stars.
- **Agent Finder / ARD** (Jun 2026): ranks AI resources from a curated catalog.

## What we shipped to capitalize (DONE)
- `AGENTS.md` (root) — full agent context: architecture, commands, constraints, do-not-touch.
- `.github/copilot-instructions.md` — Copilot-cloud-agent focused.
- `.github/instructions/clause-rules.instructions.md` — path-specific guidance.
- `.github/pull_request_template.md` + `.github/ISSUE_TEMPLATE/good_first_issue.md`.

## Launch-day agent-native levers (TODO during launch week)
1. Create the 8 seed issues as **agent-assignable** (clear Goal/Files/Acceptance/Test).
   Pin one: "Try assigning this to Copilot or opening it in Cursor."
2. Add a README "Use with AI agents" section: "open in Cursor", "assign an issue to
   Copilot", "agent context lives in AGENTS.md".
3. **Evaluate `clausekeeper-mcp`** — an MCP server exposing scan/clause-check tools.
   If built, publish → OSS MCP Community Registry → auto-appears in GitHub MCP Registry
   (sorted by stars = launch-week star momentum compounds). HIGH-LEVERAGE, own track.
4. Submit to GitHub Agent Finder / AI-resources catalog if submissions open.
5. Ensure CI is fast + green (agents need fast feedback); add a GitHub Actions test workflow.
6. Cross-post the build-in-public angle: "I made my OSS repo agent-native — assign an
   issue to Copilot and watch it ship" (strong dev-twitter / HN hook).

NOTE: No confirmed Cursor/Graphite public OSS discovery feed to exploit — GitHub remains
the canonical launch surface. Don't move hosting; make the GitHub repo agent-perfect.
