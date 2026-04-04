# Run Archive

This directory includes the archived competition record for the match `2026-04-04-0654-codex-vs-claude`.

Included:

- official match transcript in `turn-*`, `manifest.md`, `rules.md`, `transcript.md`, `messages.jsonl`, and `final/scoreboard.md`
- participant scratch output copied from `~/ai-battle/2026-04-04-0654-codex-vs-claude/workspaces/participant-b`
- raw ACP session logs under `acpx-sessions/` for codex participant, claude participant, and codex judge
- native adapter session logs under `native-sessions/` for codex participant, claude participant, and codex judge

Notes:

- `participant-a` and `judge` scratch directories were empty for this run
- `workspaces/participant-b/` contains Claude's scratch and verification scripts
- `transcript.md` and `messages.jsonl` were backfilled to match the newer flow archive format
- each turn directory now also includes raw `question.json`, `answer.json`, and `ruling.json` files derived from the archived official turn files
- `acpx-sessions/` contains richer prompt, tool, and stream context than the repo transcript, including extra exploration that did not become official turn files
- `native-sessions/` contains the original Codex and Claude session files copied from `~/.codex/sessions/` and `~/.claude/projects/`
- `runner/acpx-run/` was intentionally left out of git because it is runner-internal data, not core competition data
