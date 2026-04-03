# codex Answer

- Phase: `standard match`
- Turn: `10`
- Asked by: `claude`

## Answer

For `participantAName = "  A!B  "`:
- `trim()` -> `"A!B"`
- `toLowerCase()` -> `"a!b"`
- `.replace(/[^a-z0-9]+/g, "-")` -> `"a-b"`
- `.replace(/^-+|-+$/g, "")` -> `"a-b"`
So `participantAFileStem = "a-b"`.

For `participantBName = "a-b"`:
- `trim()` -> `"a-b"`
- `toLowerCase()` -> `"a-b"`
- non-alphanumeric runs become `"-"`, so it stays `"a-b"`
- trimming edge hyphens changes nothing
So `participantBFileStem = "a-b"`.

That means `createUniqueMatchId(...)` builds the base pattern:
`<stamp>-a-b-vs-a-b`

Second edge case:
- `participantAName = "!!!"` -> after replacement becomes `"-"`, then edge-hyphen trim makes it `""`, so the `|| "participant"` fallback produces `"participant"`
- `participantBName = "???"` follows the same path and also becomes `"participant"`

So both file stems are `"participant"`.

The problem this creates for turn-level file naming is not immediate overwrite within one turn directory, because the suffixes differ (`-question.md`, `-answer.md`, `-judge-note.md`). The real problem is loss of identity in filenames: whether A or B is the asker, the question filename is always `participant-question.md`; likewise the answer filename is always `participant-answer.md`. So the filename no longer tells you which participant authored the artifact, and both participants collapse onto the same naming namespace.

## Flaw Claim

(none)

## Artifact Paths

- `flows/ai-battle.flow.ts`
