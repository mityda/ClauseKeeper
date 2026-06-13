# ClauseKeeper — Website Rebrand & Polish Build Spec

Single build pass. Apply the brand in `brand/BRAND.md` (white bg, navy #0B2237, teal #2DD4BF→#14B8A6, shield logo) across ALL pages. Replace any ⚖️ scales icon with the shield mark (`brand/logo-icon.svg`).

## GLOBAL
1. Replace every shorthand **"docs" → "documents"** (UI copy, headings, buttons, footer). Keep code identifiers/route names as-is.
2. Theme every template to white/navy/teal. Generated documents (privacy/terms/cookies/ai) currently render dark — make them light/branded too.
3. Swap the generic legal/scales icon for the ClauseKeeper shield logo in the header/nav and favicon.
4. Add **Copy HTML** + **Download (.html and .pdf)** controls to each generated document and the bundle page. PDF can be client-side (print-to-PDF stylesheet + a "Download PDF" button using window.print with a @media print sheet) — no new heavy deps. Each doc card gets Copy + Download.

## IMAGE 1 — Footer (landing)
- Build a substantial footer: short brand blurb ("ClauseKeeper keeps your legal documents current as laws change."), columns of links — About, How It Works, Compliance Coverage (GDPR/CCPA/AI Act), Pricing, Contact (service@clausekeeper.app), and a legal disclaimer line ("Not legal advice…"). Spell out "documents".

## IMAGE 2 — Hero (landing)
- Remove "Indie businesses" / any narrowing of business type. Lead on the pain relieved:
  Headline idea: "Legal documents that keep themselves current." Sub: "Privacy, Terms, Cookie & AI-disclosure documents are a moving target. ClauseKeeper writes yours in minutes and keeps them current — so you don't have to."
- Replace "Clause library version 2026.06" with a live **"Last updated: <Month DD, YYYY>"** line (reinforces always-current). Pull the date from CLAUSE_LIBRARY_VERSION/changelog or render today's clause-version date.

## IMAGE 3 — 3 feature cards (landing)
- Keep concise; improve visual polish: clean cards, subtle border/shadow, teal iconography, consistent spacing.
- Reword the 3rd card (hosted/versioned/always-current). REMOVE any "when laws change the library bumps — that's the subscription" framing. NEW copy: "When laws change, we update your documents automatically and notify you. We do the work, so you don't have to."

## IMAGE 4 — Login / access gate
- Reframe like a gated-content preview (reference: LearnHub modal over blurred content) BUT do NOT reveal the real generator. Build a STYLIZED, heavily-blurred frosted backdrop: abstract document silhouettes + teal accents + a small "what you'll get" benefit teaser. No real form fields, no real clause text.
- Centered access card titled **"Already using ClauseKeeper?"** with Sign In, an "or" divider, and a "Start free / Subscribe" route. Professional, premium feel.

## IMAGE 5 — Pricing
- Remove the "Simple, recurring pricing" line/headline.
- Make the FREE SCANNER section more enticing: frame it as a no-risk gap-finder ("See what your site is missing in 30 seconds — free, no signup"), add a clear CTA to /scan.
- ANNUAL reframe (trustworthy, not deceptive): make the annual card LEAD with the monthly-equivalent:
  **$12.42**/mo — small clarifier directly beneath: "billed annually at $149/yr". Show monthly $19/mo as the alternative. Badge: "Best value — Save $79/yr". Keep annual as the highlighted/default plan.
- Keep "no card for the free scanner" trust framing.

## CONSTRAINTS
- No new heavy dependencies. Stay on FastAPI + Jinja2 + vanilla CSS/JS. PDF via print stylesheet.
- Do not break existing routes, auth, Stripe flow, or tests. Run `pytest` — all must pass.
- Keep the legal disclaimer prominent on every generated document.
- Brand tokens centralized in one CSS block/file so future theme tweaks are one place.
