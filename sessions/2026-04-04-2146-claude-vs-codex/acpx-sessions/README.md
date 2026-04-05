# ACP Sessions

This directory contains the raw ACP session logs copied from `~/.acpx/sessions/` for the archived match `2026-04-04-2146-claude-vs-codex`.

Files:

- `codex-participant.session.json`
- `codex-participant.stream.ndjson`
- `claude-participant.session.json`
- `claude-participant.stream.ndjson`
- `codex-judge.session.json`
- `codex-judge.stream.ndjson`

Original session IDs:

- codex participant: `019d5a76-6f32-7501-872b-51584fa73120`
- claude participant: `3cc126ee-95b2-45bc-be37-2298e2ef9769`
- codex judge: `019d5a76-940d-7fe1-99c6-e1bf31588ce3`

These logs are richer than the official match transcript. They include full prompts, wait/ruling messages, streamed outputs, tool calls, and extra exploration that may not appear in the `turn-*` files.

They may also contain absolute local paths and adapter-specific logging details.
