---
applyTo: "app/clause_rules.py,app/scanner.py,tests/test_scanner.py"
---

# Clause rules and scanner instructions

`app/scanner.py` is intentionally deterministic and rule-based. It lowercases and whitespace-normalizes raw text, then evaluates every rule from `app/clause_rules.py`. Do not add LLM calls, embeddings, network calls, or paid API dependencies to this path.

## Rule structure

Each `CLAUSE_RULES` item is a dict with:

- `key`: stable machine id. Do not rename casually; tests/UI may rely on it.
- `label`: human-readable scorecard title.
- `category`: grouping used in scan results.
- `weight`: integer score contribution.
- `signals`: lowercase phrases; any match means the clause exists.
- `stale_signals` (optional): lowercase phrases that prove the clause is current enough. If `signals` match but none of these match, scanner returns `needs_update` and awards half credit.
- `why`: user-facing explanation.
- `fix`: user-facing one-line remediation guidance.

`MAX_RAW_SCORE` must remain `sum(r["weight"] for r in CLAUSE_RULES)`.

## Adding a jurisdiction or new legal regime safely

1. Add targeted rules in `app/clause_rules.py`; do not special-case jurisdiction logic in `app/scanner.py` unless the generic rule model cannot express it.
2. Keep signal phrases lowercase because scanner matching is case-insensitive by lowercasing input, not each signal.
3. Prefer precise phrases over broad words to avoid false positives.
4. Use `stale_signals` when older language should receive partial credit but be flagged as needing update.
5. Keep weights proportional to existing rules; changing weights changes all scores.
6. Add/update `tests/test_scanner.py` with representative text that proves `present`, `missing`, and/or `needs_update` behavior.
7. Run `uv run pytest` from the repo root and keep the full suite passing.

## Scanner engine expectations

- Preserve the status semantics: `missing`, `needs_update`, `present`.
- Preserve deterministic output shape consumed by templates/API: `score_100`, `score_10`, `grade`, `verdict`, `word_count`, `counts`, `results`, `by_category`, `missing_or_stale`.
- Keep HTML extraction lightweight and local.
- Do not introduce hidden randomness, background calls, telemetry, or external document processing.
