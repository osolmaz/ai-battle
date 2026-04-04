# Run Archive

This directory includes the archived competition record for the match `2026-04-04-1524-codex-vs-claude`.

Included:

- official match transcript in `turn-*`, `manifest.md`, `rules.md`, `transcript.md`, `messages.jsonl`, and `final/scoreboard.md`
- participant scratch output copied from `~/ai-battle/2026-04-04-1524-codex-vs-claude/participant-b`
- raw ACP session logs under `acpx-sessions/` for codex participant, claude participant, and codex judge
- native adapter session logs under `native-sessions/` for codex participant, claude participant, and codex judge

Notes:

- `participant-a` and `judge` scratch directories were empty for this run
- `workspaces/participant-b/` contains Claude's scratch and verification scripts
- compiled ELF binaries from the scratch workspace were intentionally left out; only text/source artifacts were copied into git
- `transcript.md` and `messages.jsonl` already match the newer flow archive format and include the runner prompts plus the ACP session replies in hearing order
- each turn directory includes raw `question.json`, `answer.json`, and `ruling.json` files alongside the markdown turn files
- `acpx-sessions/` is the source for the richer prompt, tool, and reply context shown in `transcript.md`
- `native-sessions/` contains the original Codex and Claude session files copied from `~/.codex/sessions/` and `~/.claude/projects/`
- `runner/acpx-run/` was intentionally left out of git because it is runner-internal data, not core competition data
