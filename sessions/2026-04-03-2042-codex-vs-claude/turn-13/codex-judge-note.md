# codex Judge Note

- Phase: `standard match`
- Turn: `13`
- For judge only: `true`

## Intended Answer

Turn 1: B asks, A answers, `answerer_point` => A=1 B=0. Turn 2: A asks, B answers, `answerer_point` => A=1 B=1, so `advanceState` enters sudden death with `phase = "sudden_death"`, `currentTurn = 3`, `turnLimit = 6`. Turn 3: B asks, A answers, `flawed_caught` => A=2 B=0. Turn 4: A asks, B answers, `flawed_missed` => A=1 B=0. Turn 5: B asks, A answers, `asker_point` => A=1 B=1. Turn 6: A asks, B answers, `answerer_point` => A=1 B=2. After turn 6 `advanceState` gives scores A=1/B=2, `phase = "sudden_death"`, `currentTurn = 7`, `turnLimit = 6`. `finalResult(state)` is `"claude"`. `chooseTurn(...)` sees `currentTurn > turnLimit` and returns `route = "write_final_scoreboard"`, `askerRole = "participant_a"`, `answererRole = "participant_b"`, `turnDir` basename `turn-07`. `renderScoreboard(state)` writes `Standard turns played: 2` and `Sudden-death turns played: 4`.

## Validity Reason

This is fully determined by `scoreDeltasForOutcome`, `roleForTurn`, `advanceState`, `chooseTurn`, `finalResult`, `formatTurnDir`, and `renderScoreboard` in `flows/ai-battle.flow.ts`. The starting conditions and all outcomes are explicit, so there is a single correct result.

## Evidence Paths

- `flows/ai-battle.flow.ts`
