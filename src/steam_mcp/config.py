"""Runtime configuration, sourced from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

CHARACTER_LIMIT = 25_000
"""Max characters a single tool response should emit before truncation.

LLM context is scarce; large Steam payloads (e.g. a 2,000-game library or a
full achievement schema) are truncated to stay within a reasonable budget.
"""

STEAM_API_BASE = "https://api.steampowered.com"
STEAM_STORE_BASE = "https://store.steampowered.com"


@dataclass(frozen=True)
class Settings:
    """Resolved server settings."""

    api_key: str | None
    timeout: float
    language: str
    country: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            api_key=_clean(os.environ.get("STEAM_API_KEY")),
            timeout=_float_env("STEAM_MCP_TIMEOUT", 20.0),
            language=_clean(os.environ.get("STEAM_MCP_LANGUAGE")) or "english",
            country=(_clean(os.environ.get("STEAM_MCP_COUNTRY")) or "US").upper(),
        )

    @property
    def has_key(self) -> bool:
        return bool(self.api_key)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default
