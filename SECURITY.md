# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub's
[private vulnerability reporting](https://github.com/rachittshah/steam-mcp/security/advisories/new)
rather than opening a public issue. You'll get an acknowledgement within a few days.

## Scope & handling of secrets

- `steam-mcp` reads your `STEAM_API_KEY` from the environment only. It is never
  logged, echoed in tool output, or sent anywhere except to `api.steampowered.com`
  over HTTPS.
- All tools are **read-only** — the server performs no writes or purchases and
  never mutates Steam account state.
- Never paste your API key into an issue or PR. If you accidentally expose it,
  revoke and regenerate it at <https://steamcommunity.com/dev/apikey>.

## Supported versions

The latest released version receives fixes. Pre-1.0, only `main` is supported.
