"""MCPServer server assembly.

Creates the ``MCPServer`` instance, registers every tool group, and exposes
``build_server`` / ``mcp`` for both programmatic use and the CLI entry point.
"""

from __future__ import annotations

from mcp.server import MCPServer

from .tools import register_all

INSTRUCTIONS = """\
Tools for querying Steam via the Steam Web API and storefront.

Typical workflows:
- "How much have I played <game>?" -> search_store (name -> appid), then
  get_owned_games or get_player_achievements.
- "Tell me about <game>" -> search_store, then get_app_details / get_app_reviews.
- "Who is <profile>?" -> get_player_summary (accepts vanity names & URLs).

Most player/profile tools need a Steam Web API key (STEAM_API_KEY). Store tools
(search_store, get_app_details, get_app_reviews, get_news_for_app,
get_global_achievement_percentages) work without one. Accounts can be given as a
SteamID64, STEAM_x:y:z, [U:1:w], profile URL, or custom URL name.
"""


def build_server() -> MCPServer:
    mcp = MCPServer(name="steam-mcp", instructions=INSTRUCTIONS)
    register_all(mcp)
    return mcp


mcp = build_server()
