# 🚀 LAUNCH WEEK — READY-TO-FIRE POSTS

Status: repo is launch-ready (Docker verified, AGPL, agent-native, MCP server live).
**Two things gate firing: (1) flip repo PUBLIC, (2) create the 8 seed issues (docs/SEED_ISSUES.md).**
Then post these IN THE SAME WEEK to hit GitHub Trending.

Replace `<REPO>` = https://github.com/mityda/ClauseKeeper everywhere once public.

---

## DAY 1 — Show HN (post the REPO link, not the website)
**Title:** `Show HN: ClauseKeeper – Open-source tool to keep your site's legal docs current`

> I kept seeing indie founders ship with a privacy policy copy-pasted from 2021 — stale GDPR, no CCPA, nothing about AI disclosure even though the EU AI Act is phasing in now.
>
> ClauseKeeper is two things: a free, rule-based compliance scanner (paste your policy → 0–100 score + a checklist of missing/stale clauses, no LLM, runs offline) and a generator for Privacy/ToS/Cookie/AI-disclosure docs with conditional clauses per jurisdiction.
>
> Fully self-hostable — `docker compose up`, no API keys for the core. The hosted version just keeps the clause library current for you (open-core). AGPL-3.0.
>
> It's also agent-native: there's an AGENTS.md + an MCP server, so you can assign an issue to Copilot/Cursor, or let an agent scan a policy via MCP.
>
> It's explicitly a *starting point, not legal advice* — I'd rather say that than promise "guaranteed compliance."
>
> Repo: <REPO> — feedback welcome, especially clause rules for non-US/EU jurisdictions.

---

## DAY 1-2 — Reddit r/selfhosted (humble, "I" not "we", ask for a star)
**Title:** `I built an open-source tool to scan & generate your website's legal docs (self-hostable, no LLM)`

> Hey r/selfhosted — I just open-sourced ClauseKeeper. It scans your privacy policy / terms for missing or stale clauses (GDPR, CCPA, cookies, AI disclosure) and gives a 0–100 score, and can generate a fresh set of documents.
>
> Everything runs self-hosted with `docker compose up` — the scanner and generator need zero external keys (the scanner is 100% rule-based, no LLM). SQLite, so there's basically nothing to operate.
>
> AGPL-3.0. If it's useful, a GitHub star genuinely helps. Happy to add rules for jurisdictions I've missed.
>
> Repo: <REPO>

Crossposts: r/opensource, r/webdev, r/programming. Re-post with changelog on each new version.

---

## DAY 2-3 — dev.to / Medium / Hashnode (SEO + Google Discover)
**Title:** `How I built an open-source compliance scanner with FastAPI and zero LLM calls`
(Invest in a clean, high-contrast cover image — Discover is title+thumbnail driven.)

Outline:
1. The problem — legal docs go stale, the law keeps moving (EU AI Act, US state laws)
2. Why rule-based, not an LLM ($0, deterministic, offline, auditable)
3. Architecture — FastAPI + SQLite + Jinja, the clause-rules engine
4. Open-source-as-distribution + open-core (why give the code away)
5. Self-host in 2 minutes
6. Agent-native bonus: AGENTS.md + MCP server
7. CTA: star the repo, try the free scanner

Follow-up listicle a week later: `7 open-source tools every indie founder should self-host in 2026` (include ClauseKeeper).

---

## DAY 2 — Lemmy (selfhosted/opensource community)
Reuse the r/selfhosted post. OSS posts reliably pull 100+ upvotes.

---

## SAME WEEK — X (owned), build-in-public tone
**Thread opener:**
> I open-sourced my compliance SaaS.
>
> Everyone said "you're giving away the product." Here's why it makes it MORE profitable, not less 🧵

> 1/ The code was never the moat. In 2026 anyone can rebuild any SaaS with AI in a weekend. What's hard is *distribution* and *trust*. Open source buys you both — for free.

> 2/ ClauseKeeper scans your site's privacy policy/terms for missing or stale clauses (GDPR, CCPA, AI disclosure) → 0–100 score. Free. Rule-based, no LLM. Try it: clausekeeper.app/scan

> 3/ Self-host the whole thing free: `docker compose up`, no keys. AGPL. <REPO>

> 4/ So what do you pay for? Maintenance. The law keeps moving; the hosted tier keeps your docs current automatically. The code is free — the *watching* is the product.

> 5/ Made it agent-native too: AGENTS.md + an MCP server. Assign an issue to Copilot, or let Cursor ship a PR. Star it if you want to follow along 👇 <REPO>

**Single punchy post (alt):**
> I open-sourced my compliance SaaS. The code is free to self-host. You only pay if you want us to keep your legal docs current as the law changes.
>
> "Give away the code, sell the maintenance."
>
> <REPO>

LinkedIn: the "why I open-sourced it" angle, longer-form, same thread content.

---

## AGENT-NATIVE amplifier (unique hook — few OSS launches have this)
Post separately mid-week:
> Made my open-source repo fully agent-native. Assign a GitHub issue to Copilot and it reads AGENTS.md, fixes it, runs the tests, opens a PR. Also shipped an MCP server so any agent can scan a privacy policy.
>
> This is what "building for the agent age" actually looks like 👇 <REPO>

---

## POST-LAUNCH
- Submit MCP server → OSS MCP Community Registry (auto-lists in GitHub MCP Registry, star-sorted)
- Add CI: the workflow is staged at docs/pending/test.yml.txt — needs a workflow-scope token to push (move to .github/workflows/test.yml)
- awesome-selfhosted PR, alternativeto listing, GitHub topics
