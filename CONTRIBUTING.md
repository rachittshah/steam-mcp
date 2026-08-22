# Contributing to steam-mcp

Thanks for your interest! This project wraps the Steam Web API as MCP tools.
Contributions — new tools, bug fixes, docs — are welcome.

## Development setup

```bash
git clone https://github.com/rachittshah/steam-mcp
cd steam-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Checks (run before opening a PR)

```bash
ruff check src/ tests/       # lint
ruff format src/ tests/      # format
mypy src/                    # types
pytest                       # tests
```

All four must pass; CI runs them on Python 3.10–3.12.

## Adding a tool

1. Add the underlying request to `src/steam_mcp/client.py` (async, typed, with
   an actionable `SteamAPIError` on failure).
2. Add the tool to the relevant module in `src/steam_mcp/tools/` using the
   `@mcp.tool(annotations=READONLY)` + `@tool_errors` pattern.
3. Write a thorough docstring: what it does, when to use it, whether it needs a
   key, and what it returns. The docstring **is** the tool description the model
   sees — make it workflow-oriented.
4. Return concise, human-readable markdown; wrap large output in `truncate(...)`.
5. Add tests (mock HTTP with `respx`) and regenerate docs:
   `python scripts/gen_tool_docs.py`.

## Design principles

- **Workflows over endpoints.** Prefer tools that complete a task; guide the
  model between tools via docstrings (e.g. "use `search_store` to find an appid").
- **Token-frugal responses.** Names over numeric ids; sensible `limit` defaults.
- **Actionable errors.** Every failure should tell the model what to do next.
- **Read-only.** This server never mutates Steam state.

## Reporting bugs

Open an issue with the tool name, the input you passed, and the output you got
(redact your API key). Include whether the target profile was public/private.
