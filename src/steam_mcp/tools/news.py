"""News tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..formatting import format_unix, heading, truncate
from ..runtime import get_client
from ._common import tool_errors
from .achievements import AppIdArg
from .users import READONLY

if TYPE_CHECKING:
    from mcp.server import MCPServer


def register(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_news_for_app(
        appid: AppIdArg,
        count: Annotated[
            int, Field(default=5, ge=1, le=20, description="Number of news items.")
        ] = 5,
    ) -> str:
        """Get the latest news / patch notes for a game.

        Returns recent announcements with title, source feed, date, a short
        excerpt, and a link. No API key required. Use search_store to find the
        appid from a game name.
        """
        client = get_client()
        items = await client.get_news_for_app(appid, count=count, maxlength=400)
        if not items:
            return f"No news found for appid {appid}."
        blocks = [heading(f"Latest news for appid {appid}")]
        for n in items:
            excerpt = " ".join((n.get("contents") or "").split())
            if len(excerpt) > 300:
                excerpt = excerpt[:300].rstrip() + "…"
            blocks.append(
                "\n".join(
                    [
                        "",
                        f"### {n.get('title', 'Untitled')}",
                        f"_{n.get('feedlabel', '')} · {format_unix(n.get('date'))}_",
                        excerpt,
                        n.get("url", ""),
                    ]
                )
            )
        return truncate("\n".join(blocks))
