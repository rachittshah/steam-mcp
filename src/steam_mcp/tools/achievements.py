"""Achievement and game-stat tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..formatting import bullet, format_unix, heading, table, truncate
from ..runtime import get_client, resolve_steamid
from ._common import tool_errors
from .users import READONLY, SteamIdArg

if TYPE_CHECKING:
    from mcp.server import MCPServer

AppIdArg = Annotated[
    int,
    Field(
        description="The Steam application id (appid), e.g. 440 for Team Fortress 2. "
        "Use search_store to find an appid from a game name.",
        examples=[440, 570, 1091500],
        ge=1,
    ),
]


def register(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_player_achievements(steam_id: SteamIdArg, appid: AppIdArg) -> str:
        """Show a player's achievement progress in one game.

        Returns overall completion (unlocked / total) and a list of unlocked
        achievements with dates. The profile must be public and must own the
        game. Requires an API key.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        data = await client.get_player_achievements(steam64, appid)
        stats = data.get("playerstats", data)
        if not stats.get("success", True):
            return (
                f"No achievement data for appid {appid}: {stats.get('error', 'unknown')}. "
                "The game may have no achievements, or the profile is private."
            )
        achievements = stats.get("achievements", [])
        if not achievements:
            return f"appid {appid} has no achievements, or none are visible for {steam64}."
        unlocked = [a for a in achievements if a.get("achieved")]
        game_name = stats.get("gameName", f"appid {appid}")
        header = heading(f"{game_name}: {len(unlocked)}/{len(achievements)} achievements")
        recent = sorted(unlocked, key=lambda a: a.get("unlocktime", 0), reverse=True)[:40]
        rows = [
            [a.get("name") or a.get("apiname", "—"), format_unix(a.get("unlocktime"))]
            for a in recent
        ]
        body = table(["Unlocked achievement", "Date"], rows)
        return truncate(f"{header}\n\n{body}")

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_global_achievement_percentages(appid: AppIdArg) -> str:
        """Show how rare each achievement is across all players of a game.

        Returns achievements sorted from rarest to most common (global unlock
        percentage). Great for "what's the rarest achievement in X?". No API
        key required.
        """
        client = get_client()
        achievements = await client.get_global_achievement_percentages(appid)
        if not achievements:
            return f"No global achievement stats for appid {appid} (it may have no achievements)."
        achievements.sort(key=lambda a: a.get("percent", 0))
        rarest = achievements[:15]
        common = achievements[-5:]
        rare_rows = [[a["name"], f"{a['percent']:.1f}%"] for a in rarest]
        common_rows = [[a["name"], f"{a['percent']:.1f}%"] for a in reversed(common)]
        return truncate(
            "\n\n".join(
                [
                    heading(f"Achievement rarity for appid {appid}"),
                    heading("Rarest", 3),
                    table(["Achievement", "% of players"], rare_rows),
                    heading("Most common", 3),
                    table(["Achievement", "% of players"], common_rows),
                ]
            )
        )

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_current_player_count(appid: AppIdArg) -> str:
        """Get the number of players currently in a game, right now.

        Returns the live concurrent player count for an app. Great for
        "how many people are playing X right now?". No API key required. Use
        search_store to find the appid from a game name.
        """
        client = get_client()
        count = await client.get_current_player_count(appid)
        if count is None:
            return f"No live player count available for appid {appid}."
        return f"appid {appid} currently has **{count:,}** players in-game."

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_game_schema(appid: AppIdArg) -> str:
        """Get a game's achievement and stat definitions (its schema).

        Returns the game's display name, the count and names of its
        achievements, and any tracked stats. Use this to learn what
        achievements exist before checking a player's progress. Requires an
        API key.
        """
        client = get_client()
        data = await client.get_schema_for_game(appid)
        game = data.get("game", data)
        name = game.get("gameName") or f"appid {appid}"
        stats = game.get("availableGameStats", {})
        achievements = stats.get("achievements", [])
        tracked = stats.get("stats", [])
        lines = [
            heading(f"Schema: {name}"),
            bullet("AppID", appid),
            bullet("Version", game.get("gameVersion", "—")),
            bullet("Achievements", len(achievements)),
            bullet("Tracked stats", len(tracked)),
        ]
        if achievements:
            rows = [
                [a.get("displayName", a.get("name", "—")), a.get("name", "—")]
                for a in achievements[:60]
            ]
            lines += ["", table(["Achievement", "API name"], rows)]
        return truncate("\n".join(lines))
