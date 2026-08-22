"""Shared helpers for tool modules: uniform error handling."""

from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from ..errors import ConfigError, SteamAPIError, SteamMCPError
from ..steamid import InvalidSteamIDError

P = ParamSpec("P")
T = TypeVar("T")


def tool_errors(func: Callable[P, Awaitable[str]]) -> Callable[P, Awaitable[str]]:
    """Convert exceptions into actionable, agent-facing strings.

    Tools should never raise to the transport; the model reads the returned
    string and self-corrects. Signature is preserved for MCPServer introspection.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        try:
            return await func(*args, **kwargs)
        except SteamAPIError as exc:
            return exc.to_agent_message()
        except ConfigError as exc:
            return (
                f"Configuration error: {exc}. This tool needs STEAM_API_KEY set. "
                "Create a free key at https://steamcommunity.com/dev/apikey."
            )
        except InvalidSteamIDError as exc:
            return (
                f"Invalid SteamID input: {exc}. Pass a 17-digit SteamID64, a "
                "STEAM_X:Y:Z / [U:1:W] id, a profile URL, or a custom URL name."
            )
        except SteamMCPError as exc:
            return f"Error: {exc}"

    return wrapper
