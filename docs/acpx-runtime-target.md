# ACPX Runtime Target

Date: `2026-04-06`
Status: design note

This doc describes the cleaner target architecture for `acpx` runtime use in `ai-battle`.

It is not a description of the current implementation.

## The Issue

Right now [ai-battle.flow.ts](/home/bob/repos/ai-battle/flows/ai-battle.flow.ts) does too much runtime work itself.

It has to:

- load the embedded runtime dynamically
- manage persistent session reuse
- deal with different timeout classes
- translate runtime events into prompt results
- keep track of session record paths for transcript sync

That is too much flow-level plumbing.

## The Target

The target is:

- `acpx` exposes a stable embedded runtime API for external repos
- timeout is passed per turn, not at runtime construction
- prompt completion is session-authoritative by default
- `ai-battle` uses a small adapter module
- the flow file mostly contains battle rules and turn orchestration

## Desired ACPX API

The import should be normal:

```ts
import {
  createAcpRuntime,
  createAgentRegistry,
  createFileSessionStore,
} from "acpx/runtime";
```

The runtime should be long-lived:

```ts
const runtime = createAcpRuntime({
  cwd: process.cwd(),
  sessionStore: createFileSessionStore({ stateDir }),
  agentRegistry: createAgentRegistry(),
  permissionMode: "approve-all",
});
```

The timeout should live on the turn:

```ts
for await (const event of runtime.runTurn({
  handle,
  text: prompt,
  mode: "prompt",
  requestId,
  timeoutMs: 30 * 60_000,
  signal,
})) {
  // consume events
}
```

That is the minimum good shape.

## Better ACPX API

The better version is a stable session object:

```ts
const session = await runtime.ensureSession({
  sessionKey: "battle-participant-a",
  agent: "codex",
  mode: "persistent",
  cwd: workspaceDir,
});

const result = await session.prompt({
  text: prompt,
  timeoutMs: 30 * 60_000,
  signal,
});
```

That gives a cleaner ownership model:

- runtime owns backend integration
- session owns persistence and connection reuse
- prompt owns deadline, cancellation, and result semantics

## Required Prompt Rule

The runtime should define one rule clearly:

- if a reply for the prompt is visible in session state, that reply wins over a raw prompt-RPC timeout

That rule should live in `acpx`, not in each flow.

## Desired AI Battle Shape

`ai-battle` should use a thin adapter, for example:

- `lib/acpx-battle-runtime.ts`

That adapter would own:

- runtime creation
- participant and judge session lookup
- prompt execution
- notice execution
- cancellation
- structured JSON parsing
- session record path lookup

Then the flow reads like battle logic:

```ts
const participant = battleRuntime.participant(state, "participant_a");

await participant.sendNotice({
  promptType: "rules briefing",
  prompt: briefingPrompt,
  timeoutMs: BRIEFING_TIMEOUT_MS,
});

const ask = await participant.promptJson<AskResponse>({
  promptType: "asking turn",
  prompt: askPrompt(selection),
  timeoutMs: PARTICIPANT_TURN_TIMEOUT_MS,
});
```

And:

```ts
const judge = battleRuntime.judge(state);

const ruling = await judge.promptJson<JudgeResponse>({
  promptType: "judge turn",
  prompt: judgePrompt(turn),
  timeoutMs: JUDGE_TIMEOUT_MS,
});
```

That leaves [ai-battle.flow.ts](/home/bob/repos/ai-battle/flows/ai-battle.flow.ts) focused on:

- turn order
- prompts
- retries
- scoring
- manifest and transcript updates

## Holy Grail

The best end state is:

1. `acpx` exposes a documented and stable runtime import.
2. A persistent session is a stable object.
3. Timeout is per turn.
4. Prompt completion is session-authoritative by default.
5. Structured prompt helpers live in reusable library code.
6. `ai-battle` becomes mostly battle orchestration plus file output.

At that point, `ai-battle` no longer needs to know about:

- `process.argv[1]`
- runtime-manager grouping
- timeout-group routing
- low-level event adaptation
- prompt cancellation plumbing
- manual session-record-path recovery

## Incremental Path

The practical path is:

1. Move timeout onto the public runtime turn call.
2. Keep `acpx/runtime` as a first-class external import surface.
3. Add a thin runtime adapter inside `ai-battle`.
4. Move the current prompt and session wiring out of the flow file.
5. Keep the flow file focused on battle behavior.
