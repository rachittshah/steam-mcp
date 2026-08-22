"""Storefront tools: app details, reviews, and search. No API key required."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from ..formatting import bullet, format_playtime, heading, table, truncate
from ..runtime import get_client
from ._common import tool_errors
from .achievements import AppIdArg
from .users import READONLY

if TYPE_CHECKING:
    from mcp.server import MCPServer


def _join(items: list[dict], key: str = "description") -> str:
    return ", ".join(i.get(key, "") for i in items) if items else "—"


def _search_price(item: dict) -> str:
    """Format a storesearch result's price (given in minor currency units)."""
    final = item.get("price", {}).get("final")
    if not final:
        return "Free" if item.get("price") is not None else "—"
    return f"{final / 100:.2f}"


def register(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def search_store(
        term: Annotated[
            str,
            Field(
                description="Free-text game/app name to search for on the Steam store.",
                examples=["baldur's gate 3", "portal", "counter-strike"],
                min_length=1,
            ),
        ],
        limit: Annotated[int, Field(default=10, ge=1, le=25, description="Max results.")] = 10,
    ) -> str:
        """Search the Steam store by name and return matching apps with appids.

        This is the entry point for most store workflows: turn a game name the
        user mentioned into the appid that get_app_details, get_app_reviews, and
        the stats tools require. No API key required.
        """
        client = get_client()
        items = await client.search_store(term)
        if not items:
            return f"No store results for '{term}'. Try a shorter or corrected term."
        rows = [
            [it.get("name", "—"), str(it.get("id", "—")), _search_price(it)] for it in items[:limit]
        ]
        header = heading(f"Store results for '{term}'")
        return truncate(f"{header}\n\n{table(['Name', 'AppID', 'Price'], rows)}")

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_app_details(appid: AppIdArg) -> str:
        """Get full store details for a game/app by appid.

        Returns type, description, developers/publishers, release date, price,
        genres, platforms, Metacritic score, and review recommendation count.
        No API key required. Use search_store first if you only have a name.
        """
        client = get_client()
        d = await client.get_app_details(appid)
        price = (
            "Free" if d.get("is_free") else d.get("price_overview", {}).get("final_formatted", "—")
        )
        discount = d.get("price_overview", {}).get("discount_percent", 0)
        if discount:
            price = f"{price} (-{discount}%)"
        platforms = d.get("platforms", {})
        plats = ", ".join(p for p in ("windows", "mac", "linux") if platforms.get(p)) or "—"
        lines = [
            heading(d.get("name", f"appid {appid}")),
            bullet("AppID", d.get("steam_appid", appid)),
            bullet("Type", d.get("type", "—")),
            bullet("Release", d.get("release_date", {}).get("date", "—")),
            bullet("Price", price),
            bullet("Developers", ", ".join(d.get("developers", [])) or "—"),
            bullet("Publishers", ", ".join(d.get("publishers", [])) or "—"),
            bullet("Genres", _join(d.get("genres", []))),
            bullet("Platforms", plats),
        ]
        if d.get("metacritic"):
            lines.append(bullet("Metacritic", d["metacritic"].get("score", "—")))
        if d.get("recommendations"):
            lines.append(bullet("Recommendations", f"{d['recommendations'].get('total', 0):,}"))
        if d.get("short_description"):
            lines += ["", d["short_description"]]
        return truncate("\n".join(lines))

    @mcp.tool(annotations=READONLY)
    @tool_errors
    async def get_app_reviews(
        appid: AppIdArg,
        review_type: Annotated[
            str,
            Field(
                default="all",
                description="Filter: 'all', 'positive', or 'negative'.",
            ),
        ] = "all",
        limit: Annotated[
            int, Field(default=8, ge=1, le=20, description="Number of recent reviews to show.")
        ] = 8,
    ) -> str:
        """Summarize store reviews for a game and show a sample of recent ones.

        Returns the overall review label (e.g. "Very Positive"), positive/total
        counts, and a sample of recent reviews with their up/down vote and the
        reviewer's playtime. No API key required.
        """
        client = get_client()
        data = await client.get_app_reviews(appid, review_type=review_type, num_per_page=limit)
        summary = data.get("query_summary", {})
        total = summary.get("total_reviews", 0)
        pos = summary.get("total_positive", 0)
        pct = f"{(pos / total * 100):.0f}%" if total else "—"
        lines = [
            heading(f"Reviews for appid {appid}"),
            bullet("Rating", summary.get("review_score_desc", "—")),
            bullet("Positive", f"{pos:,} / {total:,} ({pct})"),
        ]
        reviews = data.get("reviews", [])[:limit]
        if reviews:
            lines.append("")
            for r in reviews:
                vote = "👍" if r.get("voted_up") else "👎"
                hours = format_playtime(r.get("author", {}).get("playtime_forever"))
                text = " ".join((r.get("review") or "").split())
                if len(text) > 240:
                    text = text[:240].rstrip() + "…"
                lines.append(f"- {vote} ({hours}) {text}")
        return truncate("\n".join(lines))
