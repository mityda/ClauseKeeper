"""
ClauseKeeper clause-rules configuration.

This is the heart of the FREE compliance scanner. Each rule is a self-contained,
$0-to-run heuristic: it looks for keyword/phrase signals in a policy document and
decides whether the clause is PRESENT, MISSING, or STALE (present but using
out-of-date language for 2026).

Rule-based on purpose: no paid LLM dependency, deterministic, auditable, and cheap.
To tune the scanner, edit this file only — the scanner engine reads it generically.

Each rule:
  key:        stable id
  label:      human title in the scorecard
  weight:     points contributed to the /100 score when satisfied
  signals:    phrases whose presence indicates the clause EXISTS (case-insensitive)
  stale_signals (optional): phrases that, IF the clause exists, suggest it is
              up-to-date for 2026. If the clause is present but NONE of these
              appear, we flag it STALE.
  why:        short explanation shown to the user
  fix:        one-line guidance on what to add
  category:   grouping for the scorecard
"""

CLAUSE_RULES = [
    {
        "key": "gdpr",
        "label": "GDPR (EU) data-rights language",
        "category": "Privacy regimes",
        "weight": 12,
        "signals": [
            "gdpr", "general data protection regulation", "lawful basis",
            "right to erasure", "right to be forgotten", "data subject",
            "supervisory authority",
        ],
        "stale_signals": ["lawful basis", "data subject rights", "right to erasure"],
        "why": "EU/EEA users trigger GDPR. You must state lawful basis, data-subject rights, and how to exercise them.",
        "fix": "Add a GDPR section covering lawful basis, the 8 data-subject rights, and EU representative/contact.",
    },
    {
        "key": "ccpa",
        "label": "CCPA/CPRA (California) rights",
        "category": "Privacy regimes",
        "weight": 12,
        "signals": [
            "ccpa", "cpra", "california consumer privacy", "do not sell",
            "do not share", "sale of personal information", "california residents",
            "right to opt out",
        ],
        "stale_signals": ["cpra", "do not sell or share", "sensitive personal information", "right to opt out"],
        "why": "California's CPRA (effective successor to CCPA) adds 'do not sell OR share' and sensitive-data rights.",
        "fix": "Add a California section with 'Do Not Sell or Share My Personal Information' and sensitive-PI opt-out.",
    },
    {
        "key": "cookie_consent",
        "label": "Cookie consent / tracking disclosure",
        "category": "Tracking & cookies",
        "weight": 10,
        "signals": [
            "cookie", "cookies", "tracking technolog", "pixel", "local storage",
            "web beacon", "consent banner",
        ],
        "stale_signals": ["consent", "manage cookie", "reject all", "cookie preferences"],
        "why": "You must disclose cookies/trackers and, for EU users, obtain prior consent (not just notice).",
        "fix": "Add a cookie section listing categories and a consent mechanism with a 'Reject all' option.",
    },
    {
        "key": "data_retention",
        "label": "Data-retention policy",
        "category": "Data handling",
        "weight": 9,
        "signals": [
            "retention", "retain your", "how long we keep", "retention period",
            "delete your data", "data is kept",
        ],
        "why": "Modern privacy laws require stating how long you keep personal data and the deletion criteria.",
        "fix": "Add a retention section: state periods (or criteria) and what happens to data after.",
    },
    {
        "key": "ai_disclosure",
        "label": "AI-use disclosure (2026 wedge)",
        "category": "AI & automation (2026)",
        "weight": 14,
        "signals": [
            "artificial intelligence", "automated decision", "machine learning",
            "ai model", "ai-powered", "ai features", "generative ai",
            "profiling", "algorithm",
        ],
        "stale_signals": [
            "eu ai act", "ai act", "automated decision-making", "human review",
            "training data", "ai disclosure", "generative ai",
        ],
        "why": "2026 rules (EU AI Act phased obligations, US state AI laws) require disclosing AI/automated processing and user rights around it.",
        "fix": "Add an AI-disclosure section: what AI you use, automated decisions, human-review rights, and training-data stance.",
    },
    {
        "key": "automated_decision",
        "label": "Automated decision-making & profiling rights",
        "category": "AI & automation (2026)",
        "weight": 8,
        "signals": [
            "automated decision", "profiling", "solely automated",
            "automated processing", "human intervention", "human review",
        ],
        "why": "GDPR Art. 22 + 2026 AI rules give users rights re: decisions made about them by algorithms.",
        "fix": "State whether you make solely-automated decisions and how users can request human review.",
    },
    {
        "key": "contact_dpo",
        "label": "Contact / DPO information",
        "category": "Accountability",
        "weight": 8,
        "signals": [
            "contact us", "data protection officer", "dpo", "privacy@",
            "email us", "reach us", "@",
        ],
        "stale_signals": ["data protection officer", "dpo", "privacy@", "contact"],
        "why": "Users must be able to reach you to exercise rights; EU often expects a DPO/representative contact.",
        "fix": "Add a clear contact email (e.g., privacy@yourdomain) and, if applicable, a DPO/EU rep.",
    },
    {
        "key": "coppa_children",
        "label": "Children's data (COPPA / age limits)",
        "category": "Special categories",
        "weight": 7,
        "signals": [
            "coppa", "children", "under 13", "under 16", "minor",
            "parental consent", "age of", "not directed to children",
        ],
        "why": "COPPA (US) and GDPR-K require handling of minors' data; even 'we don't serve children' must be stated.",
        "fix": "Add a children's-data section: minimum age, no knowing collection, and parental-contact path.",
    },
    {
        "key": "data_sharing",
        "label": "Third-party sharing / sub-processors",
        "category": "Data handling",
        "weight": 6,
        "signals": [
            "third party", "third-party", "service provider", "sub-processor",
            "subprocessor", "share your", "disclose your", "partners",
        ],
        "why": "You must disclose who you share data with (analytics, payment, hosting, AI vendors).",
        "fix": "List categories of recipients/sub-processors (e.g., hosting, analytics, payments, AI providers).",
    },
    {
        "key": "intl_transfer",
        "label": "International data transfers",
        "category": "Privacy regimes",
        "weight": 6,
        "signals": [
            "international transfer", "transfer your data", "outside the eea",
            "standard contractual clauses", "scc", "cross-border", "data transfer",
        ],
        "why": "Transferring EU data abroad requires a lawful transfer mechanism (e.g., SCCs) and disclosure.",
        "fix": "Add a transfers section naming your mechanism (SCCs / adequacy) and destination regions.",
    },
    {
        "key": "last_updated",
        "label": "'Last updated' date / version stamp",
        "category": "Accountability",
        "weight": 8,
        "signals": [
            "last updated", "effective date", "last revised", "version",
            "last modified",
        ],
        "why": "A visible last-updated date is expected and signals the policy is maintained — core to staying compliant.",
        "fix": "Add a 'Last updated: <date>' line at the top and bump it whenever you change the policy.",
    },
]

# Maximum achievable raw score (sum of weights) — used to normalize to /100.
MAX_RAW_SCORE = sum(r["weight"] for r in CLAUSE_RULES)
