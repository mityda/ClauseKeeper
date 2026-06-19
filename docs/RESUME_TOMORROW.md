# 🌅 RESUME TOMORROW — ClauseKeeper Launch (token handoff)

**Where we stopped:** Everything launch-ready and pushed. Token was pasted in chat but
Hermes' secret-redactor masked it (good — it can't be leaked), so I couldn't run the
GitHub API calls. Plan: Mike drops the token into a file via terminal, I read it by path.

## Step 1 — Mike runs this in the Mac terminal (one line)
```bash
printf '%s' 'PASTE_TOKEN_HERE' > ~/.ck_launch_token && chmod 600 ~/.ck_launch_token && echo saved
```
Then tell C-3PO "token's in." (Use a FRESH fine-grained token if the old one was revoked —
repo: mityda/ClauseKeeper, perms: Contents + Issues + Workflows + Administration, all R/W.)

## Step 2 — C-3PO executes (reads token from ~/.ck_launch_token by PATH, never types it)
1. Create 6 labels: `good first issue`, `help wanted`, `agent-friendly`, `clause-rules`, `tests`, `docs`
2. Create the **8 seed issues** (content below / in docs/SEED_ISSUES.md) — TOP PRIORITY per Mike
3. Push CI workflow: move `docs/pending/test.yml.txt` → `.github/workflows/test.yml` and push
   (the keychain PAT lacks `workflow` scope; this token has it)
4. Flip repo **PUBLIC** via API (token has Administration) — or Mike taps the button
5. Submit MCP server to OSS MCP Community Registry
6. **DELETE the token file:** `rm ~/.ck_launch_token`
7. Hand Mike the ready-to-fire posts (docs/LAUNCH_POSTS.md): Show HN, r/selfhosted, dev.to, Lemmy, X thread
8. Remind Mike to REVOKE the token after launch (GitHub → Settings → that token → Delete)

## The 8 seed issues (also in docs/SEED_ISSUES.md)
1. Add clause rules for Canada (PIPEDA)
2. Add clause rules for Brazil (LGPD)
3. Add clause rules for Australia (Privacy Act / APPs)
4. Scanner: detect a missing "last updated" date
5. Add a --json output mode to the scanner
6. Translate the generated Privacy Policy to Spanish
7. Add a dark-mode stylesheet
8. Document deploying to Fly.io / Railway

## State at handoff
- Repo: github.com/mityda/ClauseKeeper (PRIVATE), main @ d6c7966+
- Docker self-host VERIFIED (Colima). Open-core pricing LIVE in prod. 31/31 tests.
- Agent-native: AGENTS.md, copilot-instructions, PR/issue templates, MCP server all pushed.
- X content engine now dual-track (product + build-in-public).
- Secret sweep: clean history, safe to go public.
