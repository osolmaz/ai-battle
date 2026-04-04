# ACP Sessions

This directory contains the raw ACP session logs copied from `~/.acpx/sessions/` for the archived match `2026-04-04-1524-codex-vs-claude`.

Files:

- `codex-participant.session.json`
- `codex-participant.stream.ndjson`
- `claude-participant.session.json`
- `claude-participant.stream.ndjson`
- `codex-judge.session.json`
- `codex-judge.stream.ndjson`

Original session IDs:

- codex participant: `019d5918-3ece-73b3-ae84-df1e1af7ae5e`
- claude participant: `3617d8ba-53df-454e-a8b9-88ff626f5b63`
- codex judge: `019d5918-6a65-7a10-9d62-bb62ca92de21`

These logs are richer than the official match transcript. They include full prompts, wait/ruling messages, streamed outputs, tool calls, and extra exploration that may not appear in the `turn-*` files.

They may also contain absolute local paths and adapter-specific logging details.
