"""Shared runtime state and helpers for tool implementations.

Tools resolve a lazily-created :class:`SteamClient` via :func:`get_client`, so
the server works under stdio without an explicit lifespan. Tests inject a mock
client with :func:`set_client`.
"""

from __future__ import annotations

from .client import SteamClient
from .config import Settings
from .errors import SteamAPIError
from .steamid import InvalidSteamIDError, parse_input

_client: SteamClient | None = None


def get_client() -> SteamClient:
    global _client
    if _client is None:
        _client = SteamClient(Settings.from_env())
    return _client


def set_client(client: SteamClient | None) -> None:
    """Override the shared client (used in tests)."""
    global _client
    _client = client


async def resolve_steamid(client: SteamClient, user_input: str) -> int:
    """Turn flexible user input into a concrete SteamID64.

    Accepts a SteamID64/2/3, a profile URL, or a custom (vanity) name/URL. For
    vanity input, calls ``ResolveVanityURL`` (requires an API key).

    Raises:
        SteamAPIError: if the vanity name cannot be resolved.
        InvalidSteamIDError: if the input is not interpretable at all.
    """
    parsed = parse_input(user_input)
    if parsed.kind == "steam64" and parsed.steam64 is not None:
        return parsed.steam64

    vanity = parsed.vanity or user_input
    steam64 = await client.resolve_vanity_url(vanity)
    if steam64 is None:
        raise SteamAPIError(
            f"could not resolve vanity name {vanity!r} to a SteamID",
            hint="Confirm the custom URL name, or pass a numeric SteamID64 directly.",
        )
    return steam64


__all__ = [
    "InvalidSteamIDError",
    "SteamAPIError",
    "get_client",
    "resolve_steamid",
    "set_client",
]
