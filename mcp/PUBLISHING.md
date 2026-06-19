# Publishing clausekeeper-mcp to the MCP Registry

The package is **registry-ready**: self-contained, builds a clean wheel, `server.json` written.
Two one-time manual steps remain (they need accounts/logins an agent can't do for you).

## Prerequisites (one-time)
- A **PyPI account** → https://pypi.org/account/register/
- A **PyPI API token** → https://pypi.org/manage/account/token/ (scope: entire account first time)
- The **mcp-publisher** CLI → https://github.com/modelcontextprotocol/registry (install per its README; usually `brew install mcp-publisher` or a Go/release binary)

## Step 1 — Publish the Python package to PyPI
```bash
cd ~/projects/clausekeeper/mcp
uv build                      # produces dist/clausekeeper_mcp-0.1.0-{whl,tar.gz}
# upload (twine or uv publish). With a token:
uv publish --token pypi-XXXXXXXX          # or: twine upload dist/* -u __token__ -p pypi-XXXX
```
Verify it's live: https://pypi.org/project/clausekeeper-mcp/
Test the uvx path that the registry advertises:
```bash
uvx clausekeeper-mcp        # should start the stdio server (Ctrl-C to exit)
```

## Step 2 — Publish to the MCP Registry
The registry verifies you own the `io.github.mityda/*` namespace via GitHub login.
```bash
cd ~/projects/clausekeeper/mcp
mcp-publisher login github          # opens browser, authorize as mityda
mcp-publisher publish               # reads ./server.json
```
After publish it appears at registry.modelcontextprotocol.io and (per GitHub's MCP
Registry) becomes discoverable in VS Code / Copilot, sorted by GitHub stars — so the
launch-week star momentum directly feeds discovery here.

## If you bump the scanner later
`mcp/clausekeeper_core/` is **vendored** from `app/scanner.py` + `app/clause_rules.py`.
When you change the live scanner, re-copy those two files into clausekeeper_core/,
bump the version in `pyproject.toml` AND `server.json`, rebuild, re-publish both steps.

## Notes
- No secrets live in this repo. The PyPI token + GitHub login happen on your machine at publish time only.
- Namespace `io.github.mityda/clausekeeper` is intentional — it ties the registry entry to your GitHub identity, which is how the registry authenticates ownership.
