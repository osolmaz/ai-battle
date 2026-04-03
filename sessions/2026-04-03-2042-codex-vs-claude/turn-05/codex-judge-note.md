# codex Judge Note

- Phase: `standard match`
- Turn: `5`
- For judge only: `true`

## Intended Answer

Scores end at participantA = 2, participantB = -1. `advanceState` returns state with `phase = "standard"`, `currentTurn = 5`, `turnLimit = 4`. Because the standard match is not tied, sudden death does not start. Then `chooseTurn` sees `currentTurn > turnLimit` and returns `{ route: "write_final_scoreboard", askerRole: "participant_a", answererRole: "participant_b", askerName: "codex", answererName: "claude", turnDir basename: "turn-05" }` with that same state. Turn-by-turn: T1 B asks/A answers `answerer_point` => A1 B0; T2 A asks/B answers `asker_point` => A2 B0; T3 B asks/A answers `flawed_caught` => A3 B-1; T4 A asks/B answers `flawed_missed` => A2 B-1.

## Validity Reason

This is fully answerable from the scoring helpers, `roleForTurn`, `advanceState`, and `chooseTurn` in `flows/ai-battle.flow.ts`. The inputs and outcome sequence are explicit, so there is a single deterministic result.

## Evidence Paths

- `flows/ai-battle.flow.ts`
