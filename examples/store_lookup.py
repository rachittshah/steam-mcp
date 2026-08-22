#!/usr/bin/env python3
"""Minimal, key-free example of using the Steam client directly.

Usage:
    python examples/store_lookup.py "Portal 2"

Searches the Steam store for a game and prints its appid, price, Metacritic
score, and live player count — none of which require a STEAM_API_KEY. This is
the same client the MCP tools use under the hood.
"""

from __future__ import annotations

import asyncio
import sys

from steam_mcp.client import SteamClient
from steam_mcp.config import Settings


async def main(term: str) -> None:
    client = SteamClient(Settings.from_env())
    try:
        results = await client.search_store(term)
        if not results:
            print(f"No store results for {term!r}.")
            return
        top = results[0]
        appid = int(top["id"])
        details = await client.get_app_details(appid)
        players = await client.get_current_player_count(appid)

        print(f"{details.get('name')} (appid {appid})")
        print(f"  type:       {details.get('type')}")
        print(f"  developers: {', '.join(details.get('developers', [])) or '—'}")
        price = "Free" if details.get("is_free") else (
            details.get("price_overview", {}).get("final_formatted", "—")
        )
        print(f"  price:      {price}")
        print(f"  metacritic: {(details.get('metacritic') or {}).get('score', '—')}")
        print(f"  playing now:{players:,}" if players is not None else "  playing now: —")
    finally:
        await client.aclose()


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Portal 2"
    asyncio.run(main(query))
