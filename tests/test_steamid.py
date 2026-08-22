"""Tests for SteamID parsing and conversion.

Reference fixture: Gabe Newell's public account.
  SteamID64 : 76561197960287930
  SteamID2  : STEAM_1:0:11101
  SteamID3  : [U:1:22202]
  accountid : 22202
"""

import pytest

from steam_mcp import steamid
from steam_mcp.steamid import InvalidSteamIDError

GABEN_64 = 76561197960287930
GABEN_2 = "STEAM_1:0:11101"
GABEN_3 = "[U:1:22202]"
GABEN_ACCT = 22202


def test_account_id():
    assert steamid.account_id(GABEN_64) == GABEN_ACCT


def test_is_steam64():
    assert steamid.is_steam64(GABEN_64)
    assert steamid.is_steam64(str(GABEN_64))
    assert not steamid.is_steam64(123)
    assert not steamid.is_steam64("gabelogannewell")
    assert not steamid.is_steam64("not-a-number")


def test_steam2_roundtrip():
    assert steamid.steam2_to_steam64(GABEN_2) == GABEN_64
    assert steamid.steam64_to_steam2(GABEN_64) == GABEN_2


def test_steam3_roundtrip():
    assert steamid.steam3_to_steam64(GABEN_3) == GABEN_64
    assert steamid.steam64_to_steam3(GABEN_64) == GABEN_3


def test_steam2_case_insensitive():
    assert steamid.steam2_to_steam64("steam_1:0:11101") == GABEN_64


@pytest.mark.parametrize(
    "value",
    [
        GABEN_64,
        str(GABEN_64),
        GABEN_2,
        GABEN_3,
        "https://steamcommunity.com/profiles/76561197960287930",
    ],
)
def test_to_steam64_accepts_all_concrete_forms(value):
    assert steamid.to_steam64(value) == GABEN_64


@pytest.mark.parametrize("value", ["gabelogannewell", 42, "STEAM_9:9:9x", ""])
def test_to_steam64_rejects_non_concrete(value):
    with pytest.raises(InvalidSteamIDError):
        steamid.to_steam64(value)


def test_parse_input_concrete():
    parsed = steamid.parse_input(GABEN_2)
    assert parsed.kind == "steam64"
    assert parsed.steam64 == GABEN_64


def test_parse_input_vanity_name():
    parsed = steamid.parse_input("gabelogannewell")
    assert parsed.kind == "vanity"
    assert parsed.vanity == "gabelogannewell"


def test_parse_input_vanity_url():
    parsed = steamid.parse_input("https://steamcommunity.com/id/gabelogannewell/")
    assert parsed.kind == "vanity"
    assert parsed.vanity == "gabelogannewell"


def test_parse_input_profiles_url_is_concrete():
    parsed = steamid.parse_input("steamcommunity.com/profiles/76561197960287930")
    assert parsed.kind == "steam64"
    assert parsed.steam64 == GABEN_64


def test_parse_input_rejects_garbage():
    with pytest.raises(InvalidSteamIDError):
        steamid.parse_input("!!! not valid !!!")
