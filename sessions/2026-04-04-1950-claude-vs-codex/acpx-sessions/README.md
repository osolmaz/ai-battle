# ACP Sessions

This directory contains the raw ACP session logs copied from `~/.acpx/sessions/` for the archived match `2026-04-04-1950-claude-vs-codex`.

Files:

- `codex-participant.session.json`
- `codex-participant.stream.ndjson`
- `claude-participant.session.json`
- `claude-participant.stream.ndjson`
- `codex-judge.session.json`
- `codex-judge.stream.ndjson`

Original session IDs:

- codex participant: `019d5a0b-e9e2-7761-81bc-68a7889c223e`
- claude participant: `1f5e13f1-a2a2-4825-a789-62441cb04aca`
- codex judge: `019d5a0c-1187-7b42-b0f6-b3ce669150dd`

These logs are richer than the official match transcript. They include full prompts, wait/ruling messages, streamed outputs, tool calls, and extra exploration that may not appear in the `turn-*` files.

They may also contain absolute local paths and adapter-specific logging details.
