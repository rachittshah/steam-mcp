"""Error types and LLM-friendly error formatting.

Tool errors are returned to the model as plain strings (not exceptions) so the
agent can read them and self-correct. Each message states *what* went wrong and
*what to do next*, per MCP tool-design guidance.
"""

from __future__ import annotations


class SteamMCPError(Exception):
    """Base class for all steam-mcp errors."""


class ConfigError(SteamMCPError):
    """Missing or invalid configuration (e.g. no API key)."""


class SteamAPIError(SteamMCPError):
    """A Steam Web API / Store API request failed.

    Attributes:
        status: HTTP status code, if the request completed.
        hint: An actionable, agent-facing suggestion for recovery.
    """

    def __init__(self, message: str, *, status: int | None = None, hint: str | None = None):
        super().__init__(message)
        self.status = status
        self.hint = hint

    def to_agent_message(self) -> str:
        parts = [f"Steam API error: {self}"]
        if self.status is not None:
            parts.append(f"(HTTP {self.status})")
        if self.hint:
            parts.append(f"Suggestion: {self.hint}")
        return " ".join(parts)


def missing_key_message(tool: str) -> str:
    """Standard actionable message for tools that require an API key."""
    return (
        f"The tool '{tool}' needs a Steam Web API key, but STEAM_API_KEY is not set. "
        "Ask the user to create a free key at https://steamcommunity.com/dev/apikey and "
        "set it in the server's environment. Store tools (get_app_details, get_app_reviews, "
        "search_store) work without a key."
    )
