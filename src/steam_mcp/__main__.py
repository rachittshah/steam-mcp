"""CLI entry point: ``steam-mcp`` runs the server over stdio."""

from __future__ import annotations

import sys

from .server import mcp


def main() -> None:
    """Run the MCP server on the stdio transport."""
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] in {"stdio", "sse", "streamable-http"}:
        transport = sys.argv[1]
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
