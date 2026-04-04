# codex Judge Note

- Phase: `standard match`
- Turn: `1`
- For judge only: `true`

## Intended Answer

No. `manifest.md` is written in `prepareMatch(...)` at match creation and again in `writeFinalScoreboard(...)` at the end. Per-turn updates happen in `advanceState(...)`, which only returns updated in-memory state and does not rewrite the manifest, so a mid-match crash can leave `manifest.md` stale.

## Validity Reason

This is fully answerable by static inspection of `flows/ai-battle.flow.ts`: trace the `manifestPath` writes and compare them with the per-turn state update path.

## Evidence Paths

- `flows/ai-battle.flow.ts`
