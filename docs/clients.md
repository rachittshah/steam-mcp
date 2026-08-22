# Connecting steam-mcp to MCP clients

`steam-mcp` speaks the Model Context Protocol over **stdio**, so any MCP client
can launch it. The recommended launch command is `uvx steam-mcp` (no install
step — [uv](https://docs.astral.sh/uv/) fetches and runs it), or `steam-mcp` if
you installed it into an environment.

Set `STEAM_API_KEY` in the server's environment for player/profile tools. Get a
free key at <https://steamcommunity.com/dev/apikey>. Store tools work without one.

> **Until a PyPI release**, replace `uvx steam-mcp` everywhere below with
> `uvx --from git+https://github.com/rachittshah/steam-mcp steam-mcp` (in JSON:
> `"command": "uvx"`, `"args": ["--from", "git+https://github.com/rachittshah/steam-mcp", "steam-mcp"]`).

---

## Claude Desktop

Edit `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "steam": {
      "command": "uvx",
      "args": ["steam-mcp"],
      "env": { "STEAM_API_KEY": "your-key-here" }
    }
  }
}
```

Restart Claude Desktop. The tools appear under the 🔌 menu.

## Claude Code

Project-scoped: add an `.mcp.json` at your repo root (same shape as above), or
run:

```bash
claude mcp add steam --env STEAM_API_KEY=your-key-here -- uvx steam-mcp
```

## Cursor

Settings → **MCP** → *Add new MCP server*, or edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "steam": {
      "command": "uvx",
      "args": ["steam-mcp"],
      "env": { "STEAM_API_KEY": "your-key-here" }
    }
  }
}
```

## Cline / Roo Code (VS Code)

Open the Cline **MCP Servers** panel → *Configure MCP Servers*, and add the same
`steam` entry to the `mcpServers` object.

## Windsurf

Edit `~/.codeium/windsurf/mcp_config.json` with the same `steam` entry.

## Generic / any MCP client

Run the server directly:

```bash
STEAM_API_KEY=xxxx uvx steam-mcp          # stdio (default)
STEAM_API_KEY=xxxx uvx steam-mcp sse      # SSE transport
STEAM_API_KEY=xxxx uvx steam-mcp streamable-http
```

---

## Verifying the connection

Ask the assistant something that uses a key-free tool first, e.g.
*"Search the Steam store for Hades and show the appid."* If that works but
profile tools don't, your `STEAM_API_KEY` isn't being passed through — confirm
it's set in the `env` block above, not just your shell.
