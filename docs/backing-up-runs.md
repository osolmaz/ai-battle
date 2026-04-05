# Backing Up Runs

Use the repo for the competition record, not for `acpx` internals.

## Keep In Git

For each run, keep:

- `manifest.md`
- `messages.jsonl`
- `transcript.md`
- `rules.md`
- every `turn-*` directory
  This includes the human-readable `*.md` files and the raw `*.json` submissions for questions, answers, and rulings.
- `final/scoreboard.md`
- `ARCHIVE.md` if present
- `workspaces/` only if the scratch files are useful for reproducibility
- `acpx-sessions/` for the participant and judge ACP transcripts
- `native-sessions/` for the original Codex and Claude session files

`messages.jsonl` and `transcript.md` should now be the human-readable transcript record built from the runner prompts plus the ACP session replies, not just the final question, answer, and ruling summaries.

## Preferred Run Summary Format

When summarizing recorded runs in markdown, use this table format:

| Run | Opener | Codex Score | Claude Score | Winner |
|---|---|---:|---:|---|

Rules for this table:

- include only finished full runs
- use the participant who asked first as the `Opener`
- split the final score into separate `Codex Score` and `Claude Score` columns
- use `tie` when the match finishes level
- use the winner name only when one side actually won

## Do Not Commit

Do not commit:

- `sessions/<battle-id>/runner/acpx-run/`
- `~/.acpx/flows/runs/<run-id>/`

Those files are mostly runner state, traces, projections, and artifact snapshots. They are useful for debugging `acpx`, but they add noise, absolute local paths, and a lot of churn.

## Session Files To Back Up

Back up the ACP wrapper session files for each role into the run directory as:

- `sessions/<battle-id>/acpx-sessions/<role>.session.json`
- `sessions/<battle-id>/acpx-sessions/<role>.stream.ndjson`

This keeps the battle archive readable while preserving:

- full prompts
- streamed replies
- tool calls and outputs
- extra exploration that may not appear in `turn-*`

The repo-level `transcript.md` is generated from these ACP session messages, so these session files are required if you want to rebuild the full transcript later.

These files may contain absolute local paths and adapter-specific logging.

Also back up the original adapter logs separately as:

- `sessions/<battle-id>/native-sessions/codex-participant.rollout.jsonl`
- `sessions/<battle-id>/native-sessions/claude-participant.jsonl`
- `sessions/<battle-id>/native-sessions/codex-judge.rollout.jsonl`

Use names that make the role and adapter obvious. Keep these separate from `acpx-sessions/` so it is clear which files come from the ACP wrapper and which come from the underlying model adapter.

For a Codex vs Claude run with Codex as judge, that means backing up all of these if they exist:

- `messages.jsonl`
- `transcript.md`
- participant ACP session JSON and stream for Codex
- participant ACP session JSON and stream for Claude
- judge ACP session JSON and stream for Codex
- Codex participant rollout JSONL
- Claude participant JSONL
- Codex judge rollout JSONL

## Repo Backup Workflow

To keep a run in the repo efficiently:

1. Copy the competition record into `sessions/<battle-id>/`.
2. Keep `messages.jsonl` and `transcript.md`.
3. Copy only the participant scratch files you want to preserve.
4. Copy the ACP session logs into `acpx-sessions/`.
5. Copy the native adapter session logs into `native-sessions/`.
6. Do not copy the `runner/` directory.
7. Commit the session directory.

Example:

```bash
match_id="2026-04-04-0654-codex-vs-claude"

rsync -a --exclude 'runner/' \
  "sessions/$match_id/" \
  "/path/to/archive/$match_id/"
```

## Full Local Backup

If you want a full forensic backup, keep it outside git:

```bash
match_id="2026-04-04-0654-codex-vs-claude"
run_id="2026-04-04T065413550Z-ai-battle-5a745274"

mkdir -p "$HOME/ai-battle-archives/$match_id"

rsync -a "sessions/$match_id/" \
  "$HOME/ai-battle-archives/$match_id/repo-record/"

rsync -a "$HOME/.acpx/flows/runs/$run_id/" \
  "$HOME/ai-battle-archives/$match_id/acpx-run/"
```

This keeps the clean competition record in git and the heavy runner bundle in a private local archive.
