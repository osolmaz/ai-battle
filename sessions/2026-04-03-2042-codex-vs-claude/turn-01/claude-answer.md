# claude Answer

- Phase: `standard match`
- Turn: `1`
- Asked by: `codex`

## Answer

No. The flow does NOT rewrite manifest.md after each turn. There are exactly two places that write manifest.md: (1) `prepareMatch` (line 506) writes the initial manifest when the match directory is first created, and (2) `writeFinalScoreboard` (line 932) rewrites it at the very end of the match. The function that advances match state between turns without touching disk is `advanceState` (line 848) — it is a pure `compute` node that returns an updated in-memory `MatchState` object (new scores, next turn number, updated history) but never calls `fs.writeFile` on the manifest. Therefore, if the flow crashed immediately after turn 7, the manifest on disk would still reflect the initial state from `prepareMatch`, not the results of turns 1–7.

## Flaw Claim

(none)

## Artifact Paths

- `flows/ai-battle.flow.ts`
