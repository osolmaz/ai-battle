# Backing Up Runs

Use the repo for the competition record, not for `acpx` internals.

## Keep In Git

For each run, keep:

- `manifest.md`
- `rules.md`
- every `turn-*` directory
- `final/scoreboard.md`
- `ARCHIVE.md` if present
- `workspaces/` only if the scratch files are useful for reproducibility
- `acpx-sessions/` if you want the raw per-agent ACP transcripts

## Do Not Commit

Do not commit:

- `sessions/<battle-id>/runner/acpx-run/`
- `~/.acpx/flows/runs/<run-id>/`

Those files are mostly runner state, traces, projections, and artifact snapshots. They are useful for debugging `acpx`, but they add noise, absolute local paths, and a lot of churn.

## Optional Raw Session Logs

If you want richer per-agent context, copy the specific ACP session files into the run directory as:

- `sessions/<battle-id>/acpx-sessions/<role>.session.json`
- `sessions/<battle-id>/acpx-sessions/<role>.stream.ndjson`

This keeps the battle archive readable while preserving:

- full prompts
- streamed replies
- tool calls and outputs
- extra exploration that may not appear in `turn-*`

These files may contain absolute local paths and adapter-specific logging.

## Repo Backup Workflow

To keep a run in the repo efficiently:

1. Copy the competition record into `sessions/<battle-id>/`.
2. Copy only the participant scratch files you want to preserve.
3. Optionally copy selected ACP session logs into `acpx-sessions/`.
4. Do not copy the `runner/` directory.
5. Commit the session directory.

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
