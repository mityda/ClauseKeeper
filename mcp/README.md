# ClauseKeeper MCP Server

`clausekeeper-mcp` exposes [ClauseKeeper](../README.md)'s deterministic compliance scanner as Model Context Protocol (MCP) tools for Claude Desktop, Cursor, and other MCP hosts.

It is a thin wrapper around the real ClauseKeeper scanner in `app/scanner.py` and rule library in `app/clause_rules.py`:

- no LLM calls
- no API keys
- no paid services
- stdio transport via the official Python `mcp` SDK

## Tools

- `scan_policy_text(text: str)` — scans pasted policy/legal text with `app.scanner.scan_text` and returns the score, grade, counts, categories, and missing/stale clause checklist.
- `scan_policy_url(url: str)` — fetches a URL, strips HTML with ClauseKeeper's `html_to_text`, then scans the visible text.
- `list_clause_rules()` — returns the clause rules and categories from `app/clause_rules.py`.

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

## Publishing metadata

No `server.json` is included here because the current OSS MCP Community Registry / GitHub MCP Registry metadata format should be confirmed against the registry documentation at publication time. When publishing, add the registry-required metadata file with the package name, description, license, repository URL, runtime command, and tool list.

## Main project

See the main ClauseKeeper project at [../README.md](../README.md).
