"""Tests for formatting helpers."""

from steam_mcp import formatting as fmt


def test_format_playtime():
    assert fmt.format_playtime(0) == "0h"
    assert fmt.format_playtime(None) == "0h"
    assert fmt.format_playtime(30) == "0.5h"
    assert fmt.format_playtime(90) == "1.5h"
    assert fmt.format_playtime(600) == "10h"
    assert fmt.format_playtime(60000) == "1,000h"


def test_format_unix():
    assert fmt.format_unix(0) == "—"
    assert fmt.format_unix(None) == "—"
    # 1234567890 -> 2009-02-13 UTC
    assert fmt.format_unix(1234567890) == "2009-02-13"


def test_persona_state():
    assert fmt.persona_state(0) == "Offline"
    assert fmt.persona_state(1) == "Online"
    assert fmt.persona_state(None) == "Offline"
    assert fmt.persona_state(99) == "Unknown"


def test_community_visibility():
    assert fmt.community_visibility(1) == "Private"
    assert fmt.community_visibility(3) == "Public"
    assert fmt.community_visibility(None) == "Unknown"


def test_table():
    out = fmt.table(["A", "B"], [["1", "2"], ["3", "4"]])
    assert "| A | B |" in out
    assert "| 1 | 2 |" in out
    assert fmt.table(["A"], []) == "_(no rows)_"


def test_truncate_under_limit_untouched():
    assert fmt.truncate("hello", limit=100) == "hello"


def test_truncate_over_limit_has_notice():
    out = fmt.truncate("x" * 500, limit=200)
    assert len(out) <= 200
    assert "truncated" in out


def test_truncate_tiny_limit_still_bounded():
    # Budget smaller than the notice itself: still never exceed the limit.
    out = fmt.truncate("x" * 500, limit=30)
    assert len(out) <= 30


def test_bullet_and_heading():
    assert fmt.bullet("Name", "Gabe") == "- **Name:** Gabe"
    assert fmt.heading("Title", 3) == "### Title"
