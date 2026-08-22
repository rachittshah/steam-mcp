"""Async client for the Steam Web API and the Steam storefront API.

Two surfaces are wrapped:

* **Web API** (``api.steampowered.com``) — official, mostly key-gated. Returns
  ``{"response": {...}}`` envelopes.
* **Storefront API** (``store.steampowered.com``) — undocumented but stable and
  key-free: app details, reviews, and search.

The client is transport-agnostic (plain httpx) so tests can mock it with respx.
All methods are async and raise :class:`SteamAPIError` with an actionable hint
on failure.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import STEAM_API_BASE, STEAM_STORE_BASE, Settings
from .errors import ConfigError, SteamAPIError
from .steamid import to_steam64

_USER_AGENT = "steam-mcp (+https://github.com/rachittshah/steam-mcp)"


class SteamClient:
    """Thin async wrapper over Steam's Web and storefront APIs."""

    def __init__(self, settings: Settings, http: httpx.AsyncClient | None = None):
        self._settings = settings
        self._http = http or httpx.AsyncClient(
            timeout=settings.timeout,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    @property
    def settings(self) -> Settings:
        return self._settings

    # ---- low-level request helpers -------------------------------------

    def _require_key(self) -> str:
        if not self._settings.api_key:
            raise ConfigError("STEAM_API_KEY is not set")
        return self._settings.api_key

    async def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        clean = {k: v for k, v in params.items() if v is not None}
        try:
            resp = await self._http.get(url, params=clean)
        except httpx.TimeoutException as exc:
            raise SteamAPIError(
                "request timed out",
                hint="Steam may be slow; retry, or raise STEAM_MCP_TIMEOUT.",
            ) from exc
        except httpx.HTTPError as exc:
            raise SteamAPIError(f"network error: {exc}") from exc

        if resp.status_code == 401 or resp.status_code == 403:
            raise SteamAPIError(
                "unauthorized",
                status=resp.status_code,
                hint="Check STEAM_API_KEY, or the target profile may be private.",
            )
        if resp.status_code == 429:
            raise SteamAPIError(
                "rate limited",
                status=429,
                hint="You are being rate limited by Steam; wait and retry.",
            )
        if resp.status_code >= 500:
            raise SteamAPIError(
                "Steam server error",
                status=resp.status_code,
                hint="Transient upstream failure; retry shortly.",
            )
        if resp.status_code >= 400:
            raise SteamAPIError("request failed", status=resp.status_code)

        try:
            data: dict[str, Any] = resp.json()
        except ValueError as exc:
            raise SteamAPIError("Steam returned a non-JSON response") from exc
        return data

    async def _api(
        self, interface: str, method: str, version: int, params: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"{STEAM_API_BASE}/{interface}/{method}/v{version}/"
        params = {"key": self._require_key(), **params}
        data = await self._get_json(url, params)
        return data.get("response", data)

    async def _store(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        return await self._get_json(f"{STEAM_STORE_BASE}/{path}", params)

    # ---- ISteamUser ----------------------------------------------------

    async def resolve_vanity_url(self, vanity: str) -> int | None:
        resp = await self._api("ISteamUser", "ResolveVanityURL", 1, {"vanityurl": vanity})
        if resp.get("success") == 1 and resp.get("steamid"):
            return int(resp["steamid"])
        return None

    async def get_player_summaries(self, steamids: list[int]) -> list[dict[str, Any]]:
        resp = await self._api(
            "ISteamUser",
            "GetPlayerSummaries",
            2,
            {"steamids": ",".join(str(s) for s in steamids)},
        )
        return list(resp.get("players", []))

    async def get_player_bans(self, steamids: list[int]) -> list[dict[str, Any]]:
        resp = await self._api(
            "ISteamUser",
            "GetPlayerBans",
            1,
            {"steamids": ",".join(str(s) for s in steamids)},
        )
        return list(resp.get("players", []))

    async def get_friend_list(self, steam64: int) -> list[dict[str, Any]]:
        resp = await self._api(
            "ISteamUser",
            "GetFriendList",
            1,
            {"steamid": steam64, "relationship": "friend"},
        )
        return list(resp.get("friendslist", {}).get("friends", []))

    # ---- IPlayerService ------------------------------------------------

    async def get_owned_games(
        self,
        steam64: int,
        *,
        include_appinfo: bool = True,
        include_free: bool = True,
    ) -> dict[str, Any]:
        return await self._api(
            "IPlayerService",
            "GetOwnedGames",
            1,
            {
                "steamid": steam64,
                "include_appinfo": int(include_appinfo),
                "include_played_free_games": int(include_free),
            },
        )

    async def get_recently_played_games(
        self, steam64: int, count: int | None = None
    ) -> dict[str, Any]:
        return await self._api(
            "IPlayerService",
            "GetRecentlyPlayedGames",
            1,
            {"steamid": steam64, "count": count},
        )

    async def get_steam_level(self, steam64: int) -> int | None:
        resp = await self._api("IPlayerService", "GetSteamLevel", 1, {"steamid": steam64})
        level = resp.get("player_level")
        return int(level) if level is not None else None

    async def get_badges(self, steam64: int) -> dict[str, Any]:
        return await self._api("IPlayerService", "GetBadges", 1, {"steamid": steam64})

    # ---- ISteamUserStats ----------------------------------------------

    async def get_player_achievements(
        self, steam64: int, appid: int, language: str | None = None
    ) -> dict[str, Any]:
        return await self._api(
            "ISteamUserStats",
            "GetPlayerAchievements",
            1,
            {"steamid": steam64, "appid": appid, "l": language or self._settings.language},
        )

    async def get_user_stats_for_game(self, steam64: int, appid: int) -> dict[str, Any]:
        return await self._api(
            "ISteamUserStats",
            "GetUserStatsForGame",
            2,
            {"steamid": steam64, "appid": appid},
        )

    async def get_schema_for_game(self, appid: int, language: str | None = None) -> dict[str, Any]:
        return await self._api(
            "ISteamUserStats",
            "GetSchemaForGame",
            2,
            {"appid": appid, "l": language or self._settings.language},
        )

    async def get_global_achievement_percentages(self, appid: int) -> list[dict[str, Any]]:
        resp = await self._api(
            "ISteamUserStats",
            "GetGlobalAchievementPercentagesForApp",
            2,
            {"gameid": appid},
        )
        return list(resp.get("achievementpercentages", {}).get("achievements", []))

    # ---- ISteamNews ----------------------------------------------------

    async def get_news_for_app(
        self, appid: int, count: int = 5, maxlength: int = 600
    ) -> list[dict[str, Any]]:
        resp = await self._api(
            "ISteamNews",
            "GetNewsForApp",
            2,
            {"appid": appid, "count": count, "maxlength": maxlength},
        )
        return list(resp.get("appnews", {}).get("newsitems", []))

    # ---- Storefront (no key needed) -----------------------------------

    async def get_app_details(self, appid: int) -> dict[str, Any]:
        data = await self._store(
            "api/appdetails",
            {
                "appids": appid,
                "cc": self._settings.country,
                "l": self._settings.language,
            },
        )
        entry = data.get(str(appid), {})
        if not entry.get("success"):
            raise SteamAPIError(
                f"no store data for appid {appid}",
                hint="The appid may be wrong, delisted, or region-locked. "
                "Use search_store to find the correct appid.",
            )
        return dict(entry.get("data", {}))

    async def get_app_reviews(
        self,
        appid: int,
        *,
        review_type: str = "all",
        num_per_page: int = 20,
        purchase_type: str = "all",
    ) -> dict[str, Any]:
        return await self._store(
            f"appreviews/{appid}",
            {
                "json": 1,
                "filter": "recent",
                "review_type": review_type,
                "purchase_type": purchase_type,
                "num_per_page": num_per_page,
                "language": self._settings.language,
            },
        )

    async def search_store(self, term: str) -> list[dict[str, Any]]:
        data = await self._store(
            "api/storesearch",
            {"term": term, "cc": self._settings.country, "l": self._settings.language},
        )
        return list(data.get("items", []))


def normalize_steam64(value: int | str) -> int:
    """Convenience re-export so tools import a single helper."""
    return to_steam64(value)
