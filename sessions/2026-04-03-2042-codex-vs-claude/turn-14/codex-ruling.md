# codex Ruling

- Phase: `standard match`
- Turn: `14`
- Asker: `claude`
- Answerer: `codex`
- Outcome: `answerer_point`
- Asker delta: `0`
- Answerer delta: `1`
- Score after turn: `codex 8, claude 6`

## Reason

The question is valid, and the answer correctly distinguishes what the flow visibly enforces from what it merely delegates to the ACP runtime: the code uses separate `profile`/`session.handle` values, but the flow itself does not prove end-to-end isolation if the shared adapter were buggy. It also correctly states that `judgePrompt` never exposes the participants’ adapter command.
