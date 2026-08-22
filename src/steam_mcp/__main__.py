"""CLI entry point: ``steam-mcp`` runs the server over stdio."""

from __future__ import annotations

import sys

from .server import mcp


def main() -> None:
    """Run the MCP server.

    Defaults to the stdio transport (what MCP clients spawn). Optionally pass
    ``sse`` or ``streamable-http`` as the first CLI argument for HTTP transports.
    """
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "sse":
        mcp.run(transport="sse")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
