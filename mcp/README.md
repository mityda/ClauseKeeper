# ClauseKeeper MCP Server

<!-- mcp-name: io.github.mityda/clausekeeper -->
mcp-name: io.github.mityda/clausekeeper

`clausekeeper-mcp` exposes [ClauseKeeper](../README.md)'s deterministic compliance scanner as Model Context Protocol (MCP) tools for Claude Desktop, Cursor, and other MCP hosts.

It is a thin wrapper around a vendored copy of the real ClauseKeeper scanner in `clausekeeper_core/scanner.py` and rule library in `clausekeeper_core/clause_rules.py`:

- no LLM calls
- no API keys
- no paid services
- stdio transport via the official Python `mcp` SDK

## Tools

- `scan_policy_text(text: str)` — scans pasted policy/legal text with the vendored ClauseKeeper scanner and returns the score, grade, counts, categories, and missing/stale clause checklist.
- `scan_policy_url(url: str)` — fetches a URL, strips HTML with ClauseKeeper's `html_to_text`, then scans the visible text.
- `list_clause_rules()` — returns the vendored clause rules and categories.

## Run locally

From the main ClauseKeeper repository:

```bash
cd mcp
uv run clausekeeper-mcp
```

`uv run` creates/uses the local project environment and installs the `mcp` SDK dependency automatically. Because this is a stdio MCP server, `uv run clausekeeper-mcp` waits for an MCP client on stdin/stdout.

You can also install it into an explicit virtual environment:

```bash
cd mcp
uv venv
uv pip install --python .venv/bin/python -e .
.venv/bin/clausekeeper-mcp
```

Or run it directly:

```bash
cd /path/to/clausekeeper/mcp
uv run python server.py
```

## MCP host configuration

Use an absolute path to this `mcp` directory.

### Claude Desktop

Add this to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "clausekeeper": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/clausekeeper/mcp",
        "run",
        "clausekeeper-mcp"
      ]
    }
  }
}
```

### Cursor or other MCP hosts

Use the same server definition in your MCP settings:

```json
{
  "mcpServers": {
    "clausekeeper": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/clausekeeper/mcp",
        "run",
        "clausekeeper-mcp"
      ]
    }
  }
}
```

If your host does not support `uv --directory`, use the installed console script from a virtual environment instead:

```json
{
  "mcpServers": {
    "clausekeeper": {
      "command": "/absolute/path/to/clausekeeper/mcp/.venv/bin/clausekeeper-mcp",
      "args": []
    }
  }
}
```

## Keeping the vendored scanner in sync

The `clausekeeper_core/` package is vendored from the main app's `app/scanner.py` and `app/clause_rules.py` so the MCP package is self-contained for PyPI/registry installs. When the scanner or clause rules change in `app/`, update the matching vendored files here and re-run the MCP self-containment and parity checks.

## Publishing metadata

No `server.json` is included here because the current OSS MCP Community Registry / GitHub MCP Registry metadata format should be confirmed against the registry documentation at publication time. When publishing, add the registry-required metadata file with the package name, description, license, repository URL, runtime command, and tool list.

## Main project

See the main ClauseKeeper project at [../README.md](../README.md).
