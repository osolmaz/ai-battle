# claude Judge Note

- Phase: `standard match`
- Turn: `10`
- For judge only: `true`

## Intended Answer

Case 1: sanitizeNameForPath("  A!B  "): trim()→"A!B", toLowerCase()→"a!b", replace(/[^a-z0-9]+/g, "-")→"a-b", replace(/^-+|-+$/g, "")→"a-b". Result: "a-b". sanitizeNameForPath("a-b"): trim()→"a-b", toLowerCase()→"a-b", replace(/[^a-z0-9]+/g, "-")→"a-b", replace(/^-+|-+$/g, "")→"a-b". Result: "a-b". Both produce "a-b". The base in createUniqueMatchId becomes `<stamp>-a-b-vs-a-b`.

Case 2: sanitizeNameForPath("!!!"): trim()→"!!!", toLowerCase()→"!!!", replace(/[^a-z0-9]+/g, "-")→"-", replace(/^-+|-+$/g, "")→"". Empty string triggers the || fallback → "participant". Same for "???": also becomes "participant". Both file stems are "participant". The problem: when both participants have the same file stem, turn files collide. For example, on a turn where participant_a asks, the question file would be "participant-question.md", and when participant_b asks, it would also be "participant-question.md" — same filename in different turn directories. More critically, within the same turn the question file (asker's stem) and answer file (answerer's stem) would produce "participant-question.md" and "participant-answer.md", which are still distinct because the suffix differs. However, the judge note files would be "participant-judge-note.md" for both askers. The real issue is that there is no disambiguation — you cannot tell from the filenames alone which participant is which.

## Validity Reason

This is answerable by tracing sanitizeNameForPath with concrete inputs through each regex step, then examining how fileStemForRole is used in writeQuestion/writeAnswer. It tests understanding of the sanitization pipeline and its downstream consequences.

## Evidence Paths

- `flows/ai-battle.flow.ts`
