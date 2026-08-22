"""Identity tools: resolve names, profiles, bans, level, and friends."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from mcp.types import ToolAnnotations
from pydantic import Field

from .. import steamid as sid
from ..formatting import (
    bullet,
    community_visibility,
    format_unix,
    heading,
    persona_state,
    table,
    truncate,
)
from ..runtime import get_client, resolve_steamid
from ._common import tool_errors

if TYPE_CHECKING:
    from mcp.server import MCPServer

READONLY = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
)

SteamIdArg = Annotated[
    str,
    Field(
        description=(
            "A Steam account, in any form: a 17-digit SteamID64 "
            "(e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a "
            "full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell')."
        ),
        examples=["76561197960287930", "gabelogannewell", "STEAM_1:0:11101"],
    ),
]


def register(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def resolve_vanity_url(
        vanity: Annotated[
            str,
            Field(
                description="The custom URL name, e.g. 'gabelogannewell' from "
                "steamcommunity.com/id/gabelogannewell.",
                examples=["gabelogannewell", "robinwalker"],
            ),
        ],
    ) -> str:
        """Resolve a Steam custom (vanity) URL name to its SteamID64.

        Use this when you only have a person's custom URL name and need the
        numeric id that other tools consume. Requires an API key.

        Returns the SteamID64 in all common formats, or a not-found message.
        """
        client = get_client()
        steam64 = await client.resolve_vanity_url(vanity.strip())
        if steam64 is None:
            return (
                f"No account found for vanity name '{vanity}'. It may be spelled "
                "differently or the profile may use a numeric URL."
            )
        return "\n".join(
            [
                heading(f"Resolved '{vanity}'"),
                bullet("SteamID64", steam64),
                bullet("SteamID2", sid.steam64_to_steam2(steam64)),
                bullet("SteamID3", sid.steam64_to_steam3(steam64)),
                bullet("Profile", f"https://steamcommunity.com/profiles/{steam64}"),
            ]
        )

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_player_summary(steam_id: SteamIdArg) -> str:
        """Fetch a player's public profile summary.

        Returns persona name, online state, profile visibility, account
        creation date, country, and the game they're currently playing (if
        public). Private profiles return limited fields. Requires an API key.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        players = await client.get_player_summaries([steam64])
        if not players:
            return f"No profile found for SteamID64 {steam64} (it may be deleted)."
        p = players[0]
        lines = [
            heading(p.get("personaname", "Unknown")),
            bullet("SteamID64", steam64),
            bullet("Profile", p.get("profileurl", "—")),
            bullet("Status", persona_state(p.get("personastate"))),
            bullet("Visibility", community_visibility(p.get("communityvisibilitystate"))),
            bullet("Created", format_unix(p.get("timecreated"))),
        ]
        if p.get("loccountrycode"):
            lines.append(bullet("Country", p["loccountrycode"]))
        if p.get("gameextrainfo"):
            playing = p["gameextrainfo"]
            if p.get("gameid"):
                playing += f" (appid {p['gameid']})"
            lines.append(bullet("Now playing", playing))
        if p.get("avatarfull"):
            lines.append(bullet("Avatar", p["avatarfull"]))
        return "\n".join(lines)

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_player_bans(steam_id: SteamIdArg) -> str:
        """Check a player's VAC, game, economy, and community ban status.

        Useful for trust/reputation questions. Requires an API key.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        players = await client.get_player_bans([steam64])
        if not players:
            return f"No ban data found for SteamID64 {steam64}."
        b = players[0]
        return "\n".join(
            [
                heading(f"Ban status for {steam64}"),
                bullet("VAC banned", b.get("VACBanned", False)),
                bullet("VAC bans", b.get("NumberOfVACBans", 0)),
                bullet("Game bans", b.get("NumberOfGameBans", 0)),
                bullet("Days since last ban", b.get("DaysSinceLastBan", 0)),
                bullet("Community banned", b.get("CommunityBanned", False)),
                bullet("Economy ban", b.get("EconomyBan", "none")),
            ]
        )

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_steam_level(steam_id: SteamIdArg) -> str:
        """Get a player's Steam community level. Requires an API key."""
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        level = await client.get_steam_level(steam64)
        if level is None:
            return f"Steam level for {steam64} is unavailable (profile may be private)."
        return f"SteamID64 {steam64} is Steam level **{level}**."

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_friend_list(
        steam_id: SteamIdArg,
        limit: Annotated[
            int,
            Field(default=30, ge=1, le=100, description="Max friends to enrich with names."),
        ] = 30,
    ) -> str:
        """List a player's friends, newest-friended first, with names.

        The friend list must be public. Names are resolved in one batch call.
        Requires an API key.
        """
        client = get_client()
        steam64 = await resolve_steamid(client, steam_id)
        friends = await client.get_friend_list(steam64)
        if not friends:
            return f"No public friends found for {steam64} (list may be private)."
        friends.sort(key=lambda f: f.get("friend_since", 0), reverse=True)
        shown = friends[:limit]
        ids = [int(f["steamid"]) for f in shown]
        summaries = {int(p["steamid"]): p for p in await client.get_player_summaries(ids)}
        rows = []
        for f in shown:
            sid64 = int(f["steamid"])
            name = summaries.get(sid64, {}).get("personaname", "—")
            rows.append([name, str(sid64), format_unix(f.get("friend_since"))])
        header = heading(f"{len(friends)} friends (showing {len(shown)})")
        return truncate(f"{header}\n\n{table(['Name', 'SteamID64', 'Friends since'], rows)}")
