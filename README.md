# steam-mcp

> An [MCP](https://modelcontextprotocol.io) server that exposes the **Steam Web API** to any AI harness — Claude Desktop, Claude Code, Cursor, Cline, Windsurf, or anything that speaks the Model Context Protocol.

Ask your assistant things like *"How many hours have I put into Team Fortress 2?"*, *"What are the most-played games my friend owns?"*, or *"Summarize the reviews for Baldur's Gate 3"* — and it fetches the answer live from Steam.

[![CI](https://github.com/rachittshah/steam-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/rachittshah/steam-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why

The Steam Web API is powerful but sprawling: dozens of interfaces, inconsistent shapes, 64-bit SteamIDs, an undocumented store API, and a mandatory key for anything player-related. `steam-mcp` wraps the useful parts behind a small, well-documented set of **workflow-oriented** MCP tools that return LLM-friendly, token-efficient responses.

## Quickstart

You need a Steam Web API key for player/profile tools. Get one (free) at
<https://steamcommunity.com/dev/apikey>. Store tools (app details, reviews, search) work **without** a key.

Run it straight from GitHub with no install using [`uv`](https://docs.astral.sh/uv/)
(works today — PyPI release pending):

```bash
STEAM_API_KEY=xxxxxxxx uvx --from git+https://github.com/rachittshah/steam-mcp steam-mcp
```

Or install it from source:

```bash
uv pip install git+https://github.com/rachittshah/steam-mcp
# once published to PyPI: uv pip install steam-mcp
```

### Claude Desktop / Claude Code

Add to your MCP config (`claude_desktop_config.json`, or `.mcp.json` for Claude Code):

```json
{
  "mcpServers": {
    "steam": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rachittshah/steam-mcp", "steam-mcp"],
      "env": { "STEAM_API_KEY": "your-key-here" }
    }
  }
}
```

(After a PyPI release the `args` simplify to `["steam-mcp"]`.)

### Cursor / Cline / Windsurf

Point the MCP server command at the same `uvx --from git+... steam-mcp` invocation and
set `STEAM_API_KEY` in the environment. See [`docs/clients.md`](./docs/clients.md) for
per-client instructions.

## Configuration

| Variable              | Required | Default    | Description                                          |
| --------------------- | -------- | ---------- | ---------------------------------------------------- |
| `STEAM_API_KEY`       | for player tools | —  | Steam Web API key.                                   |
| `STEAM_MCP_TIMEOUT`   | no       | `20`       | HTTP request timeout (seconds).                      |
| `STEAM_MCP_LANGUAGE`  | no       | `english`  | Language for localized store responses.              |
| `STEAM_MCP_COUNTRY`   | no       | `US`       | ISO country code for store pricing.                  |

## Tools

The full, generated tool reference lives in [`docs/tools.md`](./docs/tools.md). Highlights:

- **Identity** — `resolve_vanity_url`, `get_player_summary`, `get_player_bans`, `get_steam_level`
- **Library** — `get_owned_games`, `get_recently_played_games`, `get_friend_list`
- **Achievements & stats** — `get_player_achievements`, `get_game_schema`, `get_global_achievement_percentages`, `get_current_player_count`
- **Store** — `get_app_details`, `get_app_reviews`, `search_store`
- **News** — `get_news_for_app`

## Development

```bash
git clone https://github.com/rachittshah/steam-mcp
cd steam-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
ruff check . && mypy src && pytest
```

## Contributing

Contributions welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[MIT](./LICENSE) © Rachitt Shah. Not affiliated with or endorsed by Valve Corporation.
Steam and the Steam logo are trademarks of Valve Corporation.
