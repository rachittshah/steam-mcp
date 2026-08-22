# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of `steam-mcp`: 14 read-only MCP tools over the Steam Web API
  and storefront.
  - Identity: `resolve_vanity_url`, `get_player_summary`, `get_player_bans`,
    `get_steam_level`, `get_friend_list`.
  - Library: `get_owned_games`, `get_recently_played_games`.
  - Achievements & stats: `get_player_achievements`,
    `get_global_achievement_percentages`, `get_game_schema`.
  - Store: `search_store`, `get_app_details`, `get_app_reviews`.
  - News: `get_news_for_app`.
- Flexible SteamID handling (SteamID64/2/3, profile URLs, vanity names).
- Token-frugal, human-readable responses with truncation to a character budget.
- Actionable, model-facing error messages.
- Test suite (respx-mocked) and CI on Python 3.10–3.12.
- Generated tool reference (`docs/tools.md`) and per-client setup guide
  (`docs/clients.md`).
