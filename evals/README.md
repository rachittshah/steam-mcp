# Evaluations

`steam_eval.xml` is a set of realistic, verifiable questions an MCP-capable agent
should be able to answer using only this server's tools. It follows the
question/answer format from the MCP server evaluation guidelines: each question
is independent, read-only, has a single stable answer, and is verifiable by
string comparison.

Answers were checked against the live Steam APIs and chosen to be stable over
time (permanent appids, fixed Metacritic scores and release dates, and a
well-known account's immutable SteamID).

- 8 of 10 questions need **no** API key (store search + app details).
- 2 questions (`resolve_vanity_url`) require `STEAM_API_KEY`.

To evaluate, connect the server to an agent, pose each `<question>`, and compare
the agent's final answer to the `<answer>` (case-insensitive substring match is
appropriate for the string answers).
