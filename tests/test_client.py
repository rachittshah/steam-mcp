"""Tests for the Steam API client, with HTTP mocked via respx."""

import httpx
import pytest
import respx

from steam_mcp.client import SteamClient
from steam_mcp.config import Settings
from steam_mcp.errors import ConfigError, SteamAPIError


def make_client(api_key: str | None = "TESTKEY") -> SteamClient:
    return SteamClient(Settings(api_key=api_key, timeout=5.0, language="english", country="US"))


@pytest.fixture
async def client():
    c = make_client()
    yield c
    await c.aclose()


@respx.mock
async def test_resolve_vanity_url_success(client):
    respx.get(url__regex=r".*ResolveVanityURL.*").mock(
        return_value=httpx.Response(
            200, json={"response": {"success": 1, "steamid": "76561197960287930"}}
        )
    )
    assert await client.resolve_vanity_url("gabelogannewell") == 76561197960287930


@respx.mock
async def test_resolve_vanity_url_not_found(client):
    respx.get(url__regex=r".*ResolveVanityURL.*").mock(
        return_value=httpx.Response(200, json={"response": {"success": 42}})
    )
    assert await client.resolve_vanity_url("nope") is None


@respx.mock
async def test_get_player_summaries(client):
    respx.get(url__regex=r".*GetPlayerSummaries.*").mock(
        return_value=httpx.Response(
            200,
            json={"response": {"players": [{"steamid": "1", "personaname": "Gabe"}]}},
        )
    )
    players = await client.get_player_summaries([1])
    assert players[0]["personaname"] == "Gabe"


@respx.mock
async def test_get_owned_games(client):
    respx.get(url__regex=r".*GetOwnedGames.*").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "game_count": 1,
                    "games": [{"appid": 440, "name": "TF2", "playtime_forever": 120}],
                }
            },
        )
    )
    data = await client.get_owned_games(76561197960287930)
    assert data["game_count"] == 1
    assert data["games"][0]["name"] == "TF2"


@respx.mock
async def test_unauthorized_raises_with_hint(client):
    respx.get(url__regex=r".*GetPlayerSummaries.*").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(SteamAPIError) as exc:
        await client.get_player_summaries([1])
    assert exc.value.status == 403
    assert exc.value.hint


@respx.mock
async def test_rate_limited_raises(client):
    respx.get(url__regex=r".*GetPlayerSummaries.*").mock(
        return_value=httpx.Response(429, text="Too Many Requests")
    )
    with pytest.raises(SteamAPIError) as exc:
        await client.get_player_summaries([1])
    assert exc.value.status == 429


@respx.mock
async def test_server_error_raises(client):
    respx.get(url__regex=r".*GetPlayerSummaries.*").mock(
        return_value=httpx.Response(503, text="down")
    )
    with pytest.raises(SteamAPIError) as exc:
        await client.get_player_summaries([1])
    assert exc.value.status == 503


async def test_missing_key_raises_config_error():
    c = make_client(api_key=None)
    try:
        with pytest.raises(ConfigError):
            await c.get_player_summaries([1])
    finally:
        await c.aclose()


@respx.mock
async def test_key_free_endpoint_works_without_key():
    c = make_client(api_key=None)
    try:
        respx.get(url__regex=r".*GetGlobalAchievementPercentagesForApp.*").mock(
            return_value=httpx.Response(
                200,
                json={"achievementpercentages": {"achievements": [{"name": "A", "percent": 12.5}]}},
            )
        )
        out = await c.get_global_achievement_percentages(440)
        assert out[0]["name"] == "A"
    finally:
        await c.aclose()


@respx.mock
async def test_get_app_details_success(client):
    respx.get(url__regex=r".*appdetails.*").mock(
        return_value=httpx.Response(
            200,
            json={"440": {"success": True, "data": {"name": "TF2", "steam_appid": 440}}},
        )
    )
    d = await client.get_app_details(440)
    assert d["name"] == "TF2"


@respx.mock
async def test_get_app_details_not_found_raises(client):
    respx.get(url__regex=r".*appdetails.*").mock(
        return_value=httpx.Response(200, json={"1": {"success": False}})
    )
    with pytest.raises(SteamAPIError) as exc:
        await client.get_app_details(1)
    assert "search_store" in (exc.value.hint or "")


@respx.mock
async def test_search_store(client):
    respx.get(url__regex=r".*storesearch.*").mock(
        return_value=httpx.Response(200, json={"items": [{"id": 620, "name": "Portal 2"}]})
    )
    items = await client.search_store("portal")
    assert items[0]["id"] == 620


@respx.mock
async def test_current_player_count(client):
    respx.get(url__regex=r".*GetNumberOfCurrentPlayers.*").mock(
        return_value=httpx.Response(200, json={"response": {"player_count": 12345, "result": 1}})
    )
    assert await client.get_current_player_count(730) == 12345
