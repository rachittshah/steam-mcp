# Tool reference

_Generated from steam-mcp v0.1.0 — do not edit by hand; run `python scripts/gen_tool_docs.py`._

15 tools are available. Tools marked _(key)_ require `STEAM_API_KEY`; the rest work without one.

## `get_app_details`

Get full store details for a game/app by appid.

Returns type, description, developers/publishers, release date, price,
genres, platforms, Metacritic score, and review recommendation count.
No API key required. Use search_store first if you only have a name.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |

## `get_app_reviews`

Summarize store reviews for a game and show a sample of recent ones.

Returns the overall review label (e.g. "Very Positive"), positive/total
counts, and a sample of recent reviews with their up/down vote and the
reviewer's playtime. No API key required.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |
| `review_type` | string | no | `all` | Filter: 'all', 'positive', or 'negative'. |
| `limit` | integer | no | `8` | Number of recent reviews to show. |

## `get_current_player_count`

Get the number of players currently in a game, right now.

Returns the live concurrent player count for an app. Great for
"how many people are playing X right now?". No API key required. Use
search_store to find the appid from a game name.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |

## `get_friend_list` _(key)_

List a player's friends, newest-friended first, with names.

The friend list must be public. Names are resolved in one batch call.
Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |
| `limit` | integer | no | `30` | Max friends to enrich with names. |

## `get_game_schema` _(key)_

Get a game's achievement and stat definitions (its schema).

Returns the game's display name, the count and names of its
achievements, and any tracked stats. Use this to learn what
achievements exist before checking a player's progress. Requires an
API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |

## `get_global_achievement_percentages`

Show how rare each achievement is across all players of a game.

Returns achievements sorted from rarest to most common (global unlock
percentage). Great for "what's the rarest achievement in X?". No API
key required.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |

## `get_news_for_app`

Get the latest news / patch notes for a game.

Returns recent announcements with title, source feed, date, a short
excerpt, and a link. No API key required. Use search_store to find the
appid from a game name.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |
| `count` | integer | no | `5` | Number of news items. |

## `get_owned_games` _(key)_

List the games a player owns, with total playtime per game.

Returns a ranked table plus library-wide totals (game count and summed
hours). The profile's game details must be public. Requires an API key.

Use `sort='recent'` to answer "what have they been playing lately?" and
`limit` to control response size.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |
| `limit` | integer | no | `20` | Max games to list. |
| `sort` | string | no | `playtime` | Ordering: 'playtime' (most hours first), 'recent' (most played in last 2 weeks), or 'name' (A-Z). |

## `get_player_achievements` _(key)_

Show a player's achievement progress in one game.

Returns overall completion (unlocked / total) and a list of unlocked
achievements with dates. The profile must be public and must own the
game. Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |
| `appid` | integer | yes |  | The Steam application id (appid), e.g. 440 for Team Fortress 2. Use search_store to find an appid from a game name. |

## `get_player_bans` _(key)_

Check a player's VAC, game, economy, and community ban status.

Useful for trust/reputation questions. Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |

## `get_player_summary` _(key)_

Fetch a player's public profile summary.

Returns persona name, online state, profile visibility, account
creation date, country, and the game they're currently playing (if
public). Private profiles return limited fields. Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |

## `get_recently_played_games` _(key)_

List games a player has played in the last two weeks.

Returns each game with its 2-week and lifetime playtime. The profile
must be public. Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |
| `count` | integer | no | `10` | Number of recent games. |

## `get_steam_level` _(key)_

Get a player's Steam community level. Requires an API key.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `steam_id` | string | yes |  | A Steam account, in any form: a 17-digit SteamID64 (e.g. '76561197960287930'), a STEAM_1:0:11101 or [U:1:22202] id, a full profile URL, or a custom/vanity URL name (e.g. 'gabelogannewell'). |

## `resolve_vanity_url` _(key)_

Resolve a Steam custom (vanity) URL name to its SteamID64.

Use this when you only have a person's custom URL name and need the
numeric id that other tools consume. Requires an API key.

Returns the SteamID64 in all common formats, or a not-found message.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `vanity` | string | yes |  | The custom URL name, e.g. 'gabelogannewell' from steamcommunity.com/id/gabelogannewell. |

## `search_store`

Search the Steam store by name and return matching apps with appids.

This is the entry point for most store workflows: turn a game name the
user mentioned into the appid that get_app_details, get_app_reviews, and
the stats tools require. No API key required.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `term` | string | yes |  | Free-text game/app name to search for on the Steam store. |
| `limit` | integer | no | `10` | Max results. |
