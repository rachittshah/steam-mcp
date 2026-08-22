"""End-to-end tool tests: drive tools through MCPServer.call_tool with mocked HTTP."""

import httpx
import pytest
import respx

from steam_mcp.client import SteamClient
from steam_mcp.config import Settings
from steam_mcp.runtime import set_client
from steam_mcp.server import build_server


@pytest.fixture
def server():
    return build_server()


@pytest.fixture
def use_mock_client():
    client = SteamClient(Settings(api_key="TESTKEY", timeout=5.0, language="english", country="US"))
    set_client(client)
    yield client
    set_client(None)


def text_of(result) -> str:
    return "\n".join(getattr(b, "text", "") for b in result.content)


@respx.mock
async def test_get_app_details_tool(server, use_mock_client):
    respx.get(url__regex=r".*appdetails.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "620": {
                    "success": True,
                    "data": {
                        "name": "Portal 2",
                        "steam_appid": 620,
                        "type": "game",
                        "developers": ["Valve"],
                        "is_free": False,
                        "price_overview": {"final_formatted": "$9.99", "discount_percent": 0},
                        "short_description": "Great &amp; fun game",
                    },
                }
            },
        )
    )
    result = await server.call_tool("get_app_details", {"appid": 620})
    out = text_of(result)
    assert "Portal 2" in out
    assert "$9.99" in out
    # HTML entities are unescaped in the description.
    assert "Great & fun game" in out


@respx.mock
async def test_get_owned_games_tool_sorts_and_totals(server, use_mock_client):
    respx.get(url__regex=r".*GetOwnedGames.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "game_count": 2,
                    "games": [
                        {"appid": 440, "name": "TF2", "playtime_forever": 6000},
                        {"appid": 570, "name": "Dota 2", "playtime_forever": 12000},
                    ],
                }
            },
        )
    )
    result = await server.call_tool(
        "get_owned_games", {"steam_id": "76561197960287930", "limit": 5}
    )
    out = text_of(result)
    assert "2 games" in out
    # Dota 2 has more playtime, so it should appear before TF2 (default sort=playtime).
    assert out.index("Dota 2") < out.index("TF2")


@respx.mock
async def test_search_store_tool(server, use_mock_client):
    respx.get(url__regex=r".*storesearch.*").mock(
        return_value=httpx.Response(
            200,
            json={"items": [{"id": 620, "name": "Portal 2", "price": {"final": 999}}]},
        )
    )
    result = await server.call_tool("search_store", {"term": "portal"})
    out = text_of(result)
    assert "Portal 2" in out
    assert "620" in out
    assert "9.99" in out


async def test_player_tool_without_key_returns_actionable_message(server):
    # No key configured -> tool should not raise; it returns a helpful string.
    set_client(SteamClient(Settings(api_key=None, timeout=5.0, language="english", country="US")))
    try:
        result = await server.call_tool("get_steam_level", {"steam_id": "76561197960287930"})
        out = text_of(result)
        assert "STEAM_API_KEY" in out
        assert "steamcommunity.com/dev/apikey" in out
    finally:
        set_client(None)


async def test_invalid_steamid_returns_actionable_message(server):
    set_client(
        SteamClient(Settings(api_key="TESTKEY", timeout=5.0, language="english", country="US"))
    )
    try:
        result = await server.call_tool("get_player_summary", {"steam_id": "!!!bad!!!"})
        out = text_of(result)
        assert "Invalid SteamID" in out or "SteamID" in out
    finally:
        set_client(None)
