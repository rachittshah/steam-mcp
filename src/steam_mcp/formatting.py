"""Response formatting helpers shared across tools.

Goals (per MCP best practices):
* Return **high-signal, human-readable** text by default (names over numeric ids).
* Offer a ``concise`` vs ``detailed`` knob so agents control their context spend.
* Enforce a hard character budget with an explicit truncation notice, so the
  model knows results were cut rather than silently assuming completeness.
"""

from __future__ import annotations

from typing import Literal

from .config import CHARACTER_LIMIT

ResponseFormat = Literal["concise", "detailed"]


def truncate(text: str, limit: int = CHARACTER_LIMIT) -> str:
    """Truncate at a UTF-8 char budget, appending an explicit notice."""
    if len(text) <= limit:
        return text
    notice = (
        "\n\n[... response truncated to fit the context budget. Narrow your query "
        "(e.g. a specific appid, or format='concise') for complete results.]"
    )
    # For a pathologically small budget that can't even hold the notice, hard
    # cut so the guarantee len(result) <= limit still holds.
    if limit <= len(notice):
        return text[:limit]
    keep = limit - len(notice)
    return text[:keep].rstrip() + notice


def format_playtime(minutes: int | float | None) -> str:
    """Render Steam playtime (stored in minutes) as compact hours."""
    if not minutes:
        return "0h"
    hours = minutes / 60
    if hours < 10:
        return f"{hours:.1f}h"
    return f"{round(hours):,}h"


def format_unix(ts: int | None) -> str:
    """Render a unix timestamp as an ISO-8601 UTC date, or '—' if absent."""
    if not ts:
        return "—"
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def persona_state(state: int | None) -> str:
    """Map a numeric personastate to a label."""
    states = {
        0: "Offline",
        1: "Online",
        2: "Busy",
        3: "Away",
        4: "Snooze",
        5: "Looking to trade",
        6: "Looking to play",
    }
    return states.get(state or 0, "Unknown")


def community_visibility(state: int | None) -> str:
    """Map communityvisibilitystate to a label."""
    return {1: "Private", 2: "Friends only", 3: "Public"}.get(state or 0, "Unknown")


def bullet(label: str, value: object) -> str:
    """A single ``- **label:** value`` markdown line."""
    return f"- **{label}:** {value}"


def heading(text: str, level: int = 2) -> str:
    return f"{'#' * level} {text}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a compact GitHub-flavored markdown table."""
    if not rows:
        return "_(no rows)_"
    sep = "| " + " | ".join(headers) + " |"
    div = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return f"{sep}\n{div}\n{body}"
