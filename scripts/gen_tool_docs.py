#!/usr/bin/env python3
"""Generate docs/tools.md from the live server's registered tools.

Run: ``python scripts/gen_tool_docs.py`` (writes docs/tools.md).

Keeping the tool reference generated from the source of truth (the registered
tool schemas) means the docs never drift from the actual tool signatures.
"""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any

from steam_mcp import __version__
from steam_mcp.server import build_server

DOCS = Path(__file__).resolve().parent.parent / "docs" / "tools.md"


def _param_rows(schema: dict[str, Any]) -> list[str]:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    rows = []
    for name, spec in props.items():
        typ = spec.get("type") or _any_of_type(spec) or "—"
        req = "yes" if name in required else "no"
        default = spec.get("default", "")
        default_s = "" if default in (None, "") else f"`{default}`"
        desc = (spec.get("description") or "").replace("\n", " ").strip()
        rows.append(f"| `{name}` | {typ} | {req} | {default_s} | {desc} |")
    return rows


def _any_of_type(spec: dict[str, Any]) -> str | None:
    options = spec.get("anyOf") or spec.get("oneOf")
    if not options:
        return None
    return " \\| ".join(o.get("type", "?") for o in options)


async def render() -> str:
    mcp = build_server()
    tools = sorted(await mcp.list_tools(), key=lambda t: t.name)
    out: list[str] = [
        "# Tool reference",
        "",
        f"_Generated from steam-mcp v{__version__} — do not edit by hand; run "
        "`python scripts/gen_tool_docs.py`._",
        "",
        f"{len(tools)} tools are available. Tools marked _(key)_ require "
        "`STEAM_API_KEY`; the rest work without one.",
        "",
    ]
    for t in tools:
        desc = inspect.cleandoc(t.description or "")
        normalized = " ".join(desc.lower().split())
        tag = " _(key)_" if "requires an api key" in normalized else ""
        out.append(f"## `{t.name}`{tag}")
        out.append("")
        out.append(desc)
        out.append("")
        rows = _param_rows(t.input_schema)
        if rows:
            out.append("| Parameter | Type | Required | Default | Description |")
            out.append("| --- | --- | --- | --- | --- |")
            out.extend(rows)
        else:
            out.append("_No parameters._")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    content = asyncio.run(render())
    DOCS.parent.mkdir(parents=True, exist_ok=True)
    DOCS.write_text(content, encoding="utf-8")
    print(f"Wrote {DOCS} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
