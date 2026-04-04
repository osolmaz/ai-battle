# claude Question

- Phase: `standard match`
- Turn: `10`
- Asker: `claude`
- Answerer: `codex`
- Score before turn: `codex 5, claude 4`

## Question

In `flows/ai-battle.flow.ts`, consider calling `prepareMatch` with `participantAName = "  A!B  "` and `participantBName = "a-b"`. Trace through `sanitizeNameForPath` (lines 1054-1062) for each name and determine their resulting file stems. Then, given those file stems, what is the `base` string that `createUniqueMatchId` (line 517) constructs (ignore the timestamp portion — just give the pattern as `<stamp>-???`)? Finally, consider a second edge case: `participantAName = "!!!"` and `participantBName = "???"`. What file stems does `sanitizeNameForPath` produce for each, and what problem does this create for the turn-level file naming scheme (where question files are named `${fileStemForRole(state, askerRole)}-question.md`)?
