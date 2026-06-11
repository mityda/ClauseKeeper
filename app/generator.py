"""
ClauseKeeper document generator (the PAID product).

Takes structured business inputs and assembles four documents:
  - Privacy Policy
  - Terms of Service
  - Cookie Policy
  - 2026 AI-Disclosure Addendum

Generation is template-based with CONDITIONAL clauses driven by the inputs
(jurisdiction toggles, cookies y/n, AI features y/n). Every document carries a
'not legal advice' disclaimer, a 'last updated' date, and a clause-version stamp
(CLAUSE_LIBRARY_VERSION) — this version stamp + changelog is what justifies the
recurring "always-current" subscription.

No paid LLM dependency: deterministic string assembly.
"""
from datetime import date

# Bump this whenever clause language is updated for new regulations.
# The changelog below is surfaced in docs and the dashboard to justify recurring billing.
CLAUSE_LIBRARY_VERSION = "2026.06"

CLAUSE_CHANGELOG = [
    ("2026.06", "Added EU AI Act phased-obligation language and US state AI-disclosure clauses."),
    ("2026.03", "Updated CCPA references to CPRA 'do not sell or share' + sensitive-PI opt-out."),
    ("2026.01", "Added data-retention criteria language and international-transfer SCC references."),
    ("2025.09", "Initial clause library: GDPR, CCPA, cookies, contact/DPO, COPPA."),
]

DISCLAIMER = (
    "This document was generated from a template by ClauseKeeper and is provided for "
    "informational purposes only. It does NOT constitute legal advice and is not a "
    "substitute for review by a qualified attorney in your jurisdiction. You are "
    "responsible for ensuring this document is accurate and complete for your business."
)


def _today() -> str:
    return date.today().isoformat()


def _li(items):
    return "\n".join(f"<li>{i}</li>" for i in items)


def _build_privacy_policy(d: dict) -> str:
    biz = d["business_name"]
    site = d["website"]
    email = d["contact_email"]
    juris = d["jurisdictions"]  # set of codes: 'eu','ca','us','uk','other'
    data_types = d["data_collected"]  # list of strings
    uses_cookies = d["uses_cookies"]
    uses_ai = d["uses_ai"]

    parts = []
    parts.append(f"<h1>Privacy Policy</h1>")
    parts.append(f"<p><strong>Last updated:</strong> {_today()} &nbsp;|&nbsp; "
                 f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>")
    parts.append(f"<p>This Privacy Policy explains how <strong>{biz}</strong> "
                 f"(\"we\", \"us\") collects, uses, and protects personal data when you "
                 f"use <a href=\"{site}\">{site}</a>.</p>")

    parts.append("<h2>1. Information We Collect</h2>")
    parts.append("<p>We collect the following categories of personal data:</p>")
    parts.append(f"<ul>{_li(data_types)}</ul>")

    parts.append("<h2>2. How We Use Your Data</h2>")
    parts.append("<ul>"
                 "<li>To provide and operate our services</li>"
                 "<li>To communicate with you about your account or requests</li>"
                 "<li>To comply with legal obligations</li>"
                 "<li>To improve and secure our services</li>"
                 "</ul>")

    # --- Conditional: GDPR (EU/UK) ---
    if "eu" in juris or "uk" in juris:
        parts.append("<h2>3. Your Rights Under the GDPR (EU/UK)</h2>")
        parts.append("<p>Our <strong>lawful basis</strong> for processing is consent and/or "
                     "legitimate interest and/or performance of a contract, depending on the "
                     "activity. As a data subject you have the right to:</p>")
        parts.append("<ul>"
                     "<li>Access your personal data</li>"
                     "<li>Rectify inaccurate data</li>"
                     "<li>Erasure ('right to be forgotten')</li>"
                     "<li>Restrict or object to processing</li>"
                     "<li>Data portability</li>"
                     "<li>Withdraw consent at any time</li>"
                     "<li>Lodge a complaint with a supervisory authority</li>"
                     "</ul>")
        parts.append(f"<p>To exercise these rights, contact us at "
                     f"<a href=\"mailto:{email}\">{email}</a>.</p>")

    # --- Conditional: CCPA/CPRA (California) ---
    if "ca" in juris or "us" in juris:
        parts.append("<h2>4. California Privacy Rights (CCPA/CPRA)</h2>")
        parts.append("<p>If you are a California resident, you have the right to know, delete, "
                     "and correct your personal information, and the right to opt out of the "
                     "<strong>sale or sharing</strong> of personal information. We also honor "
                     "limits on the use of <strong>sensitive personal information</strong>.</p>")
        parts.append(f"<p>To exercise these rights, including "
                     f"<strong>\"Do Not Sell or Share My Personal Information,\"</strong> "
                     f"email <a href=\"mailto:{email}\">{email}</a>.</p>")

    # --- Conditional: Cookies ---
    if uses_cookies:
        parts.append("<h2>5. Cookies & Tracking</h2>")
        parts.append("<p>We use cookies and similar tracking technologies. See our separate "
                     "Cookie Policy for details and your consent options, including the ability "
                     "to reject non-essential cookies.</p>")

    # --- Conditional: AI ---
    if uses_ai:
        parts.append("<h2>6. Automated Processing & AI</h2>")
        parts.append("<p>We use artificial intelligence and/or automated processing in parts of "
                     "our service. Where any decision producing legal or similarly significant "
                     "effects is made by solely automated means, you have the right to request "
                     "<strong>human review</strong>. See our AI-Disclosure Addendum for full "
                     "details, including our position on training data and the EU AI Act.</p>")

    parts.append("<h2>7. Data Retention</h2>")
    parts.append("<p>We retain personal data only as long as necessary for the purposes "
                 "described, to comply with legal obligations, resolve disputes, and enforce "
                 "agreements. When data is no longer needed, we delete or anonymize it.</p>")

    parts.append("<h2>8. Third Parties & Sub-processors</h2>")
    parts.append("<p>We may share data with service providers who process it on our behalf "
                 "(e.g., hosting, analytics, payment processing"
                 + (", and AI providers" if uses_ai else "")
                 + "). We require them to protect your data.</p>")

    if "eu" in juris or "uk" in juris:
        parts.append("<h2>9. International Data Transfers</h2>")
        parts.append("<p>Where we transfer personal data outside the EEA/UK, we rely on "
                     "appropriate safeguards such as Standard Contractual Clauses (SCCs) or an "
                     "adequacy decision.</p>")

    parts.append("<h2>10. Children's Privacy</h2>")
    parts.append("<p>Our services are not directed to children under 13 (or the applicable age "
                 "in your jurisdiction), and we do not knowingly collect their personal data. "
                 "If you believe a child has provided us data, contact us for removal.</p>")

    parts.append("<h2>11. Contact Us</h2>")
    parts.append(f"<p>Questions or requests? Email <a href=\"mailto:{email}\">{email}</a>.</p>")

    return "\n".join(parts)


def _build_terms(d: dict) -> str:
    biz = d["business_name"]
    site = d["website"]
    email = d["contact_email"]
    parts = [
        "<h1>Terms of Service</h1>",
        f"<p><strong>Last updated:</strong> {_today()} &nbsp;|&nbsp; "
        f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>",
        f"<p>These Terms govern your use of <a href=\"{site}\">{site}</a>, operated by "
        f"<strong>{biz}</strong>. By using our services you agree to these Terms.</p>",
        "<h2>1. Use of Service</h2>",
        "<p>You agree to use the service lawfully and not to misuse, disrupt, or attempt "
        "unauthorized access to it.</p>",
        "<h2>2. Accounts</h2>",
        "<p>You are responsible for safeguarding your account credentials and for activity "
        "under your account.</p>",
        "<h2>3. Intellectual Property</h2>",
        f"<p>All content and trademarks of {biz} remain our property. You retain rights to "
        "content you submit, granting us a license to operate the service.</p>",
        "<h2>4. Payment & Subscriptions</h2>",
        "<p>Paid features are billed as described at purchase. Subscriptions renew until "
        "cancelled. Fees are non-refundable except where required by law.</p>",
        "<h2>5. Disclaimers</h2>",
        "<p>The service is provided \"as is\" without warranties of any kind to the maximum "
        "extent permitted by law.</p>",
        "<h2>6. Limitation of Liability</h2>",
        "<p>To the extent permitted by law, we are not liable for indirect, incidental, or "
        "consequential damages arising from your use of the service.</p>",
        "<h2>7. Termination</h2>",
        "<p>We may suspend or terminate access for breach of these Terms.</p>",
        "<h2>8. Changes</h2>",
        "<p>We may update these Terms; material changes will be posted with a new effective "
        "date.</p>",
        "<h2>9. Contact</h2>",
        f"<p>Questions? Email <a href=\"mailto:{email}\">{email}</a>.</p>",
    ]
    return "\n".join(parts)


def _build_cookie_policy(d: dict) -> str:
    biz = d["business_name"]
    email = d["contact_email"]
    if not d["uses_cookies"]:
        return ("<h1>Cookie Policy</h1>"
                f"<p><strong>Last updated:</strong> {_today()} | "
                f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>"
                f"<p><strong>{biz}</strong> does not use non-essential cookies or tracking "
                "technologies. Only strictly necessary cookies required for the site to "
                "function may be used.</p>")
    return "\n".join([
        "<h1>Cookie Policy</h1>",
        f"<p><strong>Last updated:</strong> {_today()} &nbsp;|&nbsp; "
        f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>",
        f"<p>This Cookie Policy explains how <strong>{biz}</strong> uses cookies and similar "
        "technologies.</p>",
        "<h2>1. What Are Cookies</h2>",
        "<p>Cookies are small files stored on your device. We also use similar technologies "
        "such as pixels, web beacons, and local storage.</p>",
        "<h2>2. Categories We Use</h2>",
        "<ul>"
        "<li><strong>Strictly necessary</strong> — required for the site to function.</li>"
        "<li><strong>Functional</strong> — remember your preferences.</li>"
        "<li><strong>Analytics</strong> — help us understand usage.</li>"
        "<li><strong>Marketing</strong> — used to deliver relevant content (consent required).</li>"
        "</ul>",
        "<h2>3. Your Choices & Consent</h2>",
        "<p>For users in the EU/UK and similar regimes, we obtain prior consent for "
        "non-essential cookies. You can <strong>reject all</strong> non-essential cookies and "
        "change your cookie preferences at any time via our consent banner.</p>",
        "<h2>4. Contact</h2>",
        f"<p>Questions? Email <a href=\"mailto:{email}\">{email}</a>.</p>",
    ])


def _build_ai_disclosure(d: dict) -> str:
    biz = d["business_name"]
    email = d["contact_email"]
    juris = d["jurisdictions"]
    if not d["uses_ai"]:
        return ("<h1>AI-Disclosure Addendum (2026)</h1>"
                f"<p><strong>Last updated:</strong> {_today()} | "
                f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>"
                f"<p><strong>{biz}</strong> does not currently use artificial intelligence or "
                "automated decision-making to process personal data in a way that produces "
                "legal or similarly significant effects. This addendum will be updated if that "
                "changes.</p>")
    parts = [
        "<h1>AI-Disclosure Addendum (2026)</h1>",
        f"<p><strong>Last updated:</strong> {_today()} &nbsp;|&nbsp; "
        f"<strong>Clause library version:</strong> {CLAUSE_LIBRARY_VERSION}</p>",
        f"<p>This addendum discloses how <strong>{biz}</strong> uses artificial intelligence "
        "(AI) and automated processing, in line with emerging 2026 obligations including the "
        "EU AI Act's phased requirements and US state AI-transparency laws.</p>",
        "<h2>1. Where We Use AI</h2>",
        "<p>We use AI and/or machine-learning systems to power certain features of our "
        "service (for example, generation, recommendation, classification, or support).</p>",
        "<h2>2. Automated Decision-Making</h2>",
        "<p>Where decisions producing legal or similarly significant effects are made by "
        "<strong>solely automated</strong> means, you have the right to obtain <strong>human "
        "intervention</strong>, express your view, and contest the decision. Contact "
        f"<a href=\"mailto:{email}\">{email}</a> to request human review.</p>",
        "<h2>3. AI Transparency</h2>",
        "<p>When you interact directly with an AI system (e.g., a chatbot or generated "
        "content), we disclose that you are interacting with AI, consistent with EU AI Act "
        "transparency obligations.</p>",
        "<h2>4. Training Data</h2>",
        "<p>We disclose our position on training data: we do <strong>not</strong> use your "
        "personal content to train third-party foundation models without a lawful basis and, "
        "where required, your consent. Update this statement to match your actual practice.</p>",
    ]
    if "eu" in juris:
        parts.append("<h2>5. EU AI Act</h2>")
        parts.append("<p>We monitor our systems against the EU AI Act's risk classifications "
                     "and phased obligations and will update our practices as deadlines take "
                     "effect.</p>")
    parts.append("<h2>6. Contact</h2>")
    parts.append(f"<p>Questions about our AI use? Email "
                 f"<a href=\"mailto:{email}\">{email}</a>.</p>")
    return "\n".join(parts)


def generate_documents(d: dict) -> dict:
    """Return {doc_key: {title, html_body}} for all four documents."""
    docs = {
        "privacy": {"title": "Privacy Policy", "body": _build_privacy_policy(d)},
        "terms": {"title": "Terms of Service", "body": _build_terms(d)},
        "cookies": {"title": "Cookie Policy", "body": _build_cookie_policy(d)},
        "ai": {"title": "AI-Disclosure Addendum", "body": _build_ai_disclosure(d)},
    }
    return docs
