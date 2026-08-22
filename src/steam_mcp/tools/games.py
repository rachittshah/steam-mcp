"""Library tools: owned games and recently played."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..formatting import format_playtime, heading, table, truncate
from ..runtime import get_client, resolve_steamid
from ._common import tool_errors
from .users import READONLY, SteamIdArg

if TYPE_CHECKING:
    from mcp.server import MCPServer


def register(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_owned_games(
        steam_id: SteamIdArg,
        limit: Annotated[
            int, Field(default=20, ge=1, le=200, description="Max games to list.")
        ] = 20,
        sort: Annotated[
            str,
            Field(
                default="playtime",
                description="Ordering: 'playtime' (most hours first), 'recent' "
                "(most played in last 2 weeks), or 'name' (A-Z).",
            ),
        ] = "playtime",
    ) -> str:
        """List the games a player owns, with total playtime per game.

        Returns a ranked table plus library-wide totals (game count and summed
        hours). The profile's game details must be public. Requires an API key.

        Use `sort='recent'` to answer "what have they been playing lately?" and
        `limit` to control response size.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        data = await client.get_owned_games(steam64)
        games = data.get("games", [])
        count = data.get("game_count", len(games))
        if not games:
            return (
                f"No games visible for {steam64}. The library is private, or the "
                "account owns nothing. (Game details visibility must be Public.)"
            )

        total_minutes = sum(g.get("playtime_forever", 0) for g in games)
        if sort == "name":
            games.sort(key=lambda g: g.get("name", "").lower())
        elif sort == "recent":
            games.sort(key=lambda g: g.get("playtime_2weeks", 0), reverse=True)
        else:
            games.sort(key=lambda g: g.get("playtime_forever", 0), reverse=True)

        rows = []
        for g in games[:limit]:
            rows.append(
                [
                    g.get("name", f"appid {g.get('appid')}"),
                    str(g.get("appid", "—")),
                    format_playtime(g.get("playtime_forever")),
                    format_playtime(g.get("playtime_2weeks")) if g.get("playtime_2weeks") else "—",
                ]
            )
        header = heading(
            f"{count} games · {format_playtime(total_minutes)} total "
            f"(showing top {min(limit, len(games))} by {sort})"
        )
        tbl = table(["Game", "AppID", "Playtime", "Last 2wk"], rows)
        return truncate(f"{header}\n\n{tbl}")

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_recently_played_games(
        steam_id: SteamIdArg,
        count: Annotated[
            int, Field(default=10, ge=1, le=50, description="Number of recent games.")
        ] = 10,
    ) -> str:
        """List games a player has played in the last two weeks.

        Returns each game with its 2-week and lifetime playtime. The profile
        must be public. Requires an API key.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        data = await client.get_recently_played_games(steam64, count)
        games = data.get("games", [])
        if not games:
            return f"{steam64} has no games played in the last 2 weeks (or the profile is private)."
        rows = [
            [
                g.get("name", f"appid {g.get('appid')}"),
                str(g.get("appid", "—")),
                format_playtime(g.get("playtime_2weeks")),
                format_playtime(g.get("playtime_forever")),
            ]
            for g in games
        ]
        header = heading(f"Recently played by {steam64}")
        tbl = table(["Game", "AppID", "Last 2wk", "Lifetime"], rows)
        return truncate(f"{header}\n\n{tbl}")
