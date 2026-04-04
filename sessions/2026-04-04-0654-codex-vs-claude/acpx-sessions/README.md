# ACP Sessions

This directory contains the raw ACP session logs copied from `~/.acpx/sessions/` for the archived match `2026-04-04-0654-codex-vs-claude`.

Files:

- `codex-participant.session.json`
- `codex-participant.stream.ndjson`
- `claude-participant.session.json`
- `claude-participant.stream.ndjson`
- `codex-judge.session.json`
- `codex-judge.stream.ndjson`

Original session IDs:

- codex participant: `019d5745-5d23-7270-91b3-ca556932bfc4`
- claude participant: `1cc26923-4aad-44de-9381-685520cb7d87`
- codex judge: `019d5745-7d29-79c1-98d2-76e42f113f32`

These logs are richer than the official match transcript. They include full prompts, wait/ruling messages, streamed outputs, tool calls, and extra exploration that may not appear in the `turn-*` files.

They may also contain absolute local paths and adapter-specific logging details.
