# claude Answer

- Phase: `standard match`
- Turn: `3`
- Asked by: `codex`

## Answer

Yes, the flow keeps the hidden judge note hidden from the answering participant at the prompt level. Here is the justification:

**Node order for turn 3:**
1. `choose_turn` — selects codex as asker (turn 3 is odd, so participant_a = codex asks)
2. `ask_participant_a` (codex) — codex returns JSON with `publicQuestion` and `judgeNote`
3. `wait_participant_b` (claude) — claude gets a wait message with only the current score
4. `write_question` — writes both files to disk: the public question file and the hidden judge note file (lines 683-691)
5. `answer_participant_b` (claude) — claude receives the `answerPrompt`

**Why the note stays hidden at the prompt level:** The `answerPrompt` function (lines 709-728) only includes `turn.publicQuestion` (line 715). It never references `turn.judgeNote`, `turn.judgeNotePath`, or any judge note content. So the prompt sent to the answerer contains only the public question, current score, and latest ruling.

**However, there is a caveat:** The `write_question` node writes the judge note to disk *before* the answerer is prompted (line 688-691), and the answerer's ACP session has `cwd` set to the battle repo (line 294). The answerer is a full agent with file-reading tools. Nothing in the flow technically prevents the answerer from reading the judge note file from disk at `turn-03/codex-judge-note.md` if it knows the path — the hiding is enforced by prompt design, not by filesystem permissions.

**Exact hidden-note path for turn 3:**
`/Users/onur/offline/ai-battle/sessions/2026-04-03-2042-codex-vs-claude/turn-03/codex-judge-note.md`

## Flaw Claim

(none)

## Artifact Paths

- `flows/ai-battle.flow.ts`
