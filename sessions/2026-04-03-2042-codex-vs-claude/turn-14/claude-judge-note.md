# claude Judge Note

- Phase: `standard match`
- Turn: `14`
- For judge only: `true`

## Intended Answer

The flow uses three distinct session handles: 'participant-a', 'participant-b', and 'judge' (lines 168-178). In acpx, session isolation is determined by the session handle — each unique handle gets its own independent conversation/context, even if the underlying ACP adapter command is the same binary. The judge and participant-a both use `npx @zed-industries/codex-acp@^0.10.0` per `.acpxrc.json`, but they have different session handles ('judge' vs 'participant-a'), so they are separate sessions with separate conversation histories. The flow guarantees isolation at the session level: the judge only receives what `judgeBriefingPrompt` and `judgePrompt` send, and participant-a only receives what the participant prompts send. There is no mechanism in the flow for cross-session state leakage — the match runner (flow) is the sole intermediary.

As for the second part: No, `judgePrompt` (lines 760-799) never shows the judge which ACP adapter command the participants use. It only shows the asker name, answerer name, question, answer, judge note, scores, and scoring rules. The `.acpxrc.json` configuration is not referenced or exposed in any prompt function.

## Validity Reason

This question is answerable by examining .acpxrc.json (which both participants can read from the repo), the session handle constants (lines 168-178), and the judgePrompt function (lines 760-799). It tests understanding of how acpx session isolation works based on the handle mechanism visible in the code.

## Evidence Paths

- `flows/ai-battle.flow.ts`
- `.acpxrc.json`
