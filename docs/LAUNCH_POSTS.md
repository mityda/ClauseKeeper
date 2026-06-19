# 🚀 ClauseKeeper — READY-TO-FIRE LAUNCH POSTS

**Repo is LIVE & PUBLIC:** https://github.com/mityda/ClauseKeeper
**Site:** https://clausekeeper.app  ·  **Free scanner:** https://clausekeeper.app/scan

Fire these **in the same week** to stack traffic → hit GitHub Trending. Order below is the recommended sequence. Just copy/paste.

═══════════════════════════════════════════
## ① SHOW HN (HackerNews) — post FIRST, weekday morning ET
═══════════════════════════════════════════
**Submit at:** https://news.ycombinator.com/submit
**URL field:** https://github.com/mityda/ClauseKeeper
**Title:**
```
Show HN: ClauseKeeper – Open-source tool to keep your site's legal docs current
```
**Text field (optional but recommended):**
```
I kept seeing indie founders ship with a privacy policy copy-pasted from 2021 — stale GDPR, no CCPA, nothing about AI disclosure even though the EU AI Act is phasing in now.

ClauseKeeper is two things: a free, rule-based compliance scanner (paste your policy → 0–100 score + a checklist of missing/stale clauses, no LLM, runs offline) and a generator for Privacy/ToS/Cookie/AI-disclosure docs with conditional clauses per jurisdiction.

Fully self-hostable — `docker compose up`, no API keys for the core. The hosted version just keeps the clause library current for you (open-core). AGPL-3.0.

It's also agent-native: there's an AGENTS.md + an MCP server, so you can assign an issue to Copilot/Cursor, or let an agent scan a policy via MCP.

It's explicitly a starting point, not legal advice — I'd rather say that than promise "guaranteed compliance."

Feedback welcome, especially clause rules for non-US/EU jurisdictions.
```
> 💡 After posting, DON'T upvote-beg. Reply fast and thoughtfully to every comment in the first 2 hrs — engagement drives the ranking.

═══════════════════════════════════════════
## ② REDDIT r/selfhosted — same day or next
═══════════════════════════════════════════
**Submit at:** https://www.reddit.com/r/selfhosted/submit
**Title:**
```
I built an open-source tool to scan & generate your website's legal docs (self-hostable, no LLM)
```
**Body:**
```
Hey r/selfhosted — I just open-sourced ClauseKeeper. It scans your privacy policy / terms for missing or stale clauses (GDPR, CCPA, cookies, AI disclosure) and gives a 0–100 score, and can generate a fresh set of documents.

Everything runs self-hosted with `docker compose up` — the scanner and generator need zero external keys (the scanner is 100% rule-based, no LLM). SQLite, so there's basically nothing to operate.

AGPL-3.0. If it's useful, a GitHub star genuinely helps. Happy to add rules for jurisdictions I've missed.

Repo: https://github.com/mityda/ClauseKeeper
```
**Crossposts (same text):** r/opensource, r/webdev, r/programming, r/SaaS
> 💡 r/selfhosted welcomes OSS self-promo. Re-post with a changelog on every new version.

═══════════════════════════════════════════
## ③ LEMMY — same day (selfhosted/opensource community)
═══════════════════════════════════════════
**Where:** lemmy.world → c/selfhosted or c/opensource
Reuse the exact r/selfhosted title + body above. OSS posts reliably pull 100+ upvotes.

═══════════════════════════════════════════
## ④ X / TWITTER THREAD — build-in-public tone
═══════════════════════════════════════════
**Post 1 (hook):**
```
I open-sourced my compliance SaaS.

Everyone said "you're giving away the product."

Here's why it makes it MORE profitable, not less 🧵
```
**Post 2:**
```
1/ The code was never the moat. In 2026 anyone can rebuild any SaaS with AI in a weekend.

What's actually hard is distribution and trust.

Open source buys you both — for free.
```
**Post 3:**
```
2/ ClauseKeeper scans your site's privacy policy/terms for missing or stale clauses (GDPR, CCPA, AI disclosure) → 0–100 score.

Free. Rule-based. No LLM.

Try it: https://clausekeeper.app/scan
```
**Post 4:**
```
3/ Self-host the whole thing free: `docker compose up`, no keys.

AGPL-3.0.

https://github.com/mityda/ClauseKeeper
```
**Post 5:**
```
4/ So what do you pay for? Maintenance.

The law keeps moving; the hosted tier keeps your docs current automatically.

The code is free — the *watching* is the product.
```
**Post 6 (CTA):**
```
5/ Made it agent-native too: AGENTS.md + an MCP server.

Assign an issue to Copilot, or let Cursor ship a PR.

Star it if you want to follow along 👇
https://github.com/mityda/ClauseKeeper
```
**Single-post alt (if you don't want a thread):**
```
I open-sourced my compliance SaaS. The code is free to self-host. You only pay if you want us to keep your legal docs current as the law changes.

"Give away the code, sell the maintenance."

https://github.com/mityda/ClauseKeeper
```

═══════════════════════════════════════════
## ⑤ AGENT-NATIVE AMPLIFIER — post mid-week, standalone (unique hook)
═══════════════════════════════════════════
**X / LinkedIn:**
```
Made my open-source repo fully agent-native.

Assign a GitHub issue to Copilot → it reads AGENTS.md, fixes it, runs the tests, opens a PR.

Also shipped an MCP server so any agent can scan a privacy policy.

This is what "building for the agent age" actually looks like 👇
https://github.com/mityda/ClauseKeeper
```

═══════════════════════════════════════════
## ⑥ DEV.TO / MEDIUM ARTICLE — day 2-3 (SEO + Google Discover)
═══════════════════════════════════════════
**Title:** `How I built an open-source compliance scanner with FastAPI and zero LLM calls`
(Invest in a clean, high-contrast cover image — Discover is title+thumbnail driven.)
Outline: problem (laws move) → why rule-based not LLM ($0/deterministic/offline) → architecture (FastAPI+SQLite+Jinja+clause engine) → open-source-as-distribution & open-core → self-host in 2 min → agent-native (AGENTS.md + MCP) → CTA star + scan.
Follow-up listicle a week later: `7 open-source tools every indie founder should self-host in 2026` (include ClauseKeeper).

═══════════════════════════════════════════
## POST-LAUNCH AMPLIFIERS
═══════════════════════════════════════════
- Submit MCP server → OSS MCP Community Registry (registry-ready: see mcp/server.json; needs PyPI publish + `mcp-publisher` login — one-time)
- PR to awesome-selfhosted (huge directory)
- List on alternativeto.net (as alternative to Termly / iubenda / TermsFeed)
- GitHub topics already set (gdpr, compliance, fastapi, mcp, open-core, …)

## LINKS CHEAT-SHEET
- Repo: https://github.com/mityda/ClauseKeeper
- Issues (8 open, #1 pinned): https://github.com/mityda/ClauseKeeper/issues
- Site: https://clausekeeper.app · Scanner: https://clausekeeper.app/scan
