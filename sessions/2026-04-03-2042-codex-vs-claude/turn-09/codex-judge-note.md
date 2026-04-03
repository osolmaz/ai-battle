# codex Judge Note

- Phase: `standard match`
- Turn: `9`
- For judge only: `true`

## Intended Answer

Turn 1: A asks, `asker_point` => scores A=1, B=0. Turn 2: B asks, `answerer_point` => A=2, B=0. After `advanceState` on turn 2: `state.currentTurn = 3`, `state.turnLimit = 2`, `phase = "standard"`, scores A=2/B=0. `chooseTurn` sees `currentTurn > turnLimit` and returns `route = "write_final_scoreboard"` with `turnDir` basename `turn-03`. `finalResult(state)` returns `"codex"`. `renderManifest(state)` writes `- Current turn: \`2\`` because it uses `Math.min(state.currentTurn, state.turnLimit)`. The difference exists because `chooseTurn` uses raw `currentTurn` (3, meaning past the last playable turn) while `renderManifest` clamps display to the turn limit (2).

## Validity Reason

This is fully determined by `scoreDeltasForOutcome`, `advanceState`, `chooseTurn`, `finalResult`, `formatTurnDir`, and `renderManifest` in `flows/ai-battle.flow.ts`. The inputs and outcomes are explicit, so there is a single correct result.

## Evidence Paths

- `flows/ai-battle.flow.ts`
