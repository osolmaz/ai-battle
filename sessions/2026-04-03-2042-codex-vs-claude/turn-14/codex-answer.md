# codex Answer

- Phase: `standard match`
- Turn: `14`
- Asked by: `claude`

## Answer

The flow does not, by itself, guarantee session isolation in a strong end-to-end sense.

What the flow does provide:
- `participant-a` and `judge` use different ACP `profile` names in the node definitions.
- They also use different `session.handle` values: `"participant-a"` and `"judge"`.

That is the only explicit isolation mechanism visible in this repo: the flow asks the ACP layer to treat them as separate sessions.

What the flow does not provide:
- No extra in-repo guard proves that the adapter or ACP runtime actually isolates state when two profiles use the same underlying command.
- Since `.acpxrc.json` maps both `participant-a` and `judge` to `npx @zed-industries/codex-acp@^0.10.0`, any true protection against cross-session leakage depends on the ACP runtime/adapter honoring profile/session boundaries correctly.
- If the adapter were buggy and shared state across handles or profiles, this flow has no additional mechanism to stop that.

So the bounded answer is: the design requests isolation through distinct profile names and session handles, but it does not independently guarantee it; actual leakage prevention is delegated to the ACP implementation.

On the second part: no, `judgePrompt(...)` never shows the judge which ACP adapter command the participants are using. The adapter commands exist only in `.acpxrc.json`; the judge brief and `judge_now` prompt include names, rules, scores, question/answer data, etc., but not the adapter command strings.

## Flaw Claim

(none)

## Artifact Paths

- `.acpxrc.json`
- `flows/ai-battle.flow.ts`
