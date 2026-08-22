"""MCP tool registration.

Each submodule exposes a ``register(mcp)`` function that attaches its tools to
the shared MCPServer instance. :func:`register_all` wires them all up.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import achievements, games, news, store, users

if TYPE_CHECKING:
    from mcp.server import MCPServer


def register_all(mcp: MCPServer) -> None:
    for module in (users, games, achievements, store, news):
        module.register(mcp)


__all__ = ["register_all"]
