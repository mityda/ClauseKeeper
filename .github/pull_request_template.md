## Summary

<!-- What changed and why? -->

## Test plan

- [ ] Ran `pytest` or `uv run pytest` from the repo root
- [ ] Added/updated tests for behavior changes
- [ ] Smoke-tested affected user-facing routes, if applicable

## Product constraints

- [ ] No LLM dependency or required AI/API service was added to the core scanner/generator/self-host path
- [ ] Self-hosted mode still works without external keys or Stripe
- [ ] AGPL/open-core boundary is respected (free/self-host vs paid cloud behavior is not blurred)

## Legal document safety

- [ ] If touching generators or hosted document templates, the “not legal advice” disclaimer is preserved
- [ ] If touching generated docs, the last-updated date and clause library version stamp are preserved
- [ ] I considered whether this changes legal-domain wording and documented the rationale

## Security / privacy

- [ ] No secrets, `.env`, SQLite DBs, customer data, or real legal documents are committed
- [ ] Security/privacy impact considered and described above
- [ ] Stripe webhook/signature logic and auth cookie security are unchanged, or changes are explicitly explained

## Docs

- [ ] Updated docs/agent instructions when commands, behavior, deployment, or contributor workflow changed
