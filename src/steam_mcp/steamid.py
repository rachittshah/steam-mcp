"""SteamID parsing and conversion utilities.

Steam represents an account in several interchangeable textual forms:

* **SteamID64** — a 64-bit integer, e.g. ``76561197960287930``. This is what
  every Web API endpoint actually consumes.
* **SteamID2** (classic) — ``STEAM_X:Y:Z``, e.g. ``STEAM_1:0:11101``.
* **SteamID3** — ``[U:1:W]``, e.g. ``[U:1:22202]``.
* **Custom (vanity) URL** — a human-chosen name such as ``gabelogannewell``,
  which is *not* derivable arithmetically and must be resolved via the
  ``ISteamUser/ResolveVanityURL`` endpoint (see :mod:`steam_mcp.client`).

This module handles the pure, offline conversions. Vanity resolution is a
network call and lives in the client.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Base SteamID64 for an individual account (universe=public, type=individual,
# instance=desktop). accountid = steam64 - INDIVIDUAL_BASE.
INDIVIDUAL_BASE = 76561197960265728

_STEAM2_RE = re.compile(r"^STEAM_([0-5]):([01]):(\d+)$", re.IGNORECASE)
_STEAM3_RE = re.compile(r"^\[U:1:(\d+)\]$", re.IGNORECASE)
_PROFILES_URL_RE = re.compile(r"steamcommunity\.com/profiles/(\d{17})")
_VANITY_URL_RE = re.compile(r"steamcommunity\.com/id/([^/?#]+)")


class InvalidSteamIDError(ValueError):
    """Raised when a value cannot be interpreted as any SteamID form."""


@dataclass(frozen=True)
class ParsedInput:
    """Result of :func:`parse_input`.

    Exactly one of ``steam64`` / ``vanity`` is set. ``kind`` is ``"steam64"``
    when the input resolved to a concrete id offline, or ``"vanity"`` when it
    is a custom URL name that still needs a network lookup.
    """

    kind: str  # "steam64" | "vanity"
    steam64: int | None = None
    vanity: str | None = None


def is_steam64(value: int | str) -> bool:
    """Return True if ``value`` looks like a plausible individual SteamID64."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return False
    # 17-digit ids for individual accounts start at INDIVIDUAL_BASE.
    return INDIVIDUAL_BASE <= n < INDIVIDUAL_BASE + (1 << 32)


def account_id(steam64: int) -> int:
    """Return the 32-bit account id (the ``Z*2+Y`` part) of a SteamID64."""
    return int(steam64) - INDIVIDUAL_BASE


def steam2_to_steam64(steam2: str) -> int:
    """Convert ``STEAM_X:Y:Z`` to a SteamID64 integer."""
    m = _STEAM2_RE.match(steam2.strip())
    if not m:
        raise InvalidSteamIDError(f"Not a SteamID2: {steam2!r}")
    y = int(m.group(2))
    z = int(m.group(3))
    return INDIVIDUAL_BASE + z * 2 + y


def steam3_to_steam64(steam3: str) -> int:
    """Convert ``[U:1:W]`` to a SteamID64 integer."""
    m = _STEAM3_RE.match(steam3.strip())
    if not m:
        raise InvalidSteamIDError(f"Not a SteamID3: {steam3!r}")
    return INDIVIDUAL_BASE + int(m.group(1))


def steam64_to_steam2(steam64: int) -> str:
    """Convert a SteamID64 to classic ``STEAM_1:Y:Z`` form."""
    acct = account_id(steam64)
    if acct < 0:
        raise InvalidSteamIDError(f"Not an individual SteamID64: {steam64!r}")
    return f"STEAM_1:{acct & 1}:{acct >> 1}"


def steam64_to_steam3(steam64: int) -> str:
    """Convert a SteamID64 to modern ``[U:1:W]`` form."""
    acct = account_id(steam64)
    if acct < 0:
        raise InvalidSteamIDError(f"Not an individual SteamID64: {steam64!r}")
    return f"[U:1:{acct}]"


def to_steam64(value: int | str) -> int:
    """Best-effort conversion of any concrete SteamID form to a SteamID64.

    Accepts SteamID64 (int or str), ``STEAM_X:Y:Z``, ``[U:1:W]``, or a full
    ``steamcommunity.com/profiles/<id>`` URL. Does **not** resolve vanity
    names — use :func:`parse_input` and the client for those.

    Raises:
        InvalidSteamIDError: if the value is not a concrete SteamID form.
    """
    if isinstance(value, int):
        if is_steam64(value):
            return value
        raise InvalidSteamIDError(f"Integer is not a valid SteamID64: {value!r}")

    s = value.strip()
    if is_steam64(s):
        return int(s)
    if _STEAM2_RE.match(s):
        return steam2_to_steam64(s)
    if _STEAM3_RE.match(s):
        return steam3_to_steam64(s)
    url_match = _PROFILES_URL_RE.search(s)
    if url_match:
        return int(url_match.group(1))
    raise InvalidSteamIDError(f"Cannot interpret as a SteamID: {value!r}")


def parse_input(value: str) -> ParsedInput:
    """Classify arbitrary user input as a concrete id or a vanity name.

    Tools accept flexible "steam id or profile" input from the model. This
    routes it: concrete forms resolve immediately; a ``/id/<name>`` URL or a
    bare custom name is flagged as ``vanity`` so the caller can resolve it via
    the Steam API.
    """
    s = value.strip()

    # Full vanity profile URL -> extract the custom name.
    vanity_match = _VANITY_URL_RE.search(s)
    if vanity_match:
        return ParsedInput(kind="vanity", vanity=vanity_match.group(1))

    try:
        return ParsedInput(kind="steam64", steam64=to_steam64(s))
    except InvalidSteamIDError:
        pass

    # Anything else that is a plausible custom-url token is treated as vanity.
    if re.fullmatch(r"[A-Za-z0-9_.-]{2,64}", s):
        return ParsedInput(kind="vanity", vanity=s)

    raise InvalidSteamIDError(f"Cannot interpret as a SteamID or vanity name: {value!r}")
