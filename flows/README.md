# AI Battle Flow

This repo includes a runnable `acpx` flow at [ai-battle.flow.ts](ai-battle.flow.ts).

The flow does the match bookkeeping:

- reads the rules from `AGENTS.md`
- creates a unique match directory under `sessions/`
- creates isolated empty workspaces for both participants and the judge under `~/ai-battle`
- sends the rules to both participants and the judge
- runs the ask, wait, answer, judge, and ruling loop
- writes per-turn files, a standalone transcript, and a final scoreboard

The participants and judge do not run inside the battle repo. They run in empty scratch directories. The flow still writes the official transcript back into this repo.

Participant ask turns and answer turns get `30` minutes in the current implementation.

If a participant misses that limit, the flow sends one final `1`-minute message telling them to return the final JSON immediately. If they still do not return a valid result, they automatically lose the turn and the match continues.

## Agent Profiles

The flow uses three fixed `acpx` profile names:

- `participant-a`
- `participant-b`
- `judge`

Map those profile names to real ACP adapters in `.acpxrc.json`.

Example:

```json
{
  "agents": {
    "participant-a": {
      "command": "npx @zed-industries/codex-acp"
    },
    "participant-b": {
      "command": "npx -y @agentclientprotocol/claude-agent-acp"
    },
    "judge": {
      "command": "npx @zed-industries/codex-acp"
    }
  }
}
```

## Input

The flow accepts this input shape:

```json
{
  "battleRepo": "/abs/path/to/ai-battle",
  "rulesPath": "/abs/path/to/ai-battle/AGENTS.md",
  "scratchRoot": "~/ai-battle",
  "participantAName": "codex",
  "participantBName": "claude",
  "judgeName": "judge",
  "questionCount": 10,
  "suddenDeathQuestionCount": 3,
  "startingParticipant": "participant_a"
}
```

Defaults:

- `battleRepo`: current working directory
- `rulesPath`: `<battleRepo>/AGENTS.md`
- `scratchRoot`: `~/ai-battle`
- `questionCount`: `10`
- `suddenDeathQuestionCount`: `3`
- `startingParticipant`: `participant_a`

## Agent Workspaces

For each run, the flow creates a separate scratch tree outside the repo, for example:

```text
~/ai-battle/2026-04-03-1015-codex-vs-claude/
  participant-a/
  participant-b/
  judge/
```

Each of those directories starts empty.

## Files Written

Each run creates a unique directory like:

```text
sessions/2026-04-03-1015-codex-vs-claude/
```

The date-time stamp is at the beginning of the directory name and uses `YYYY-MM-DD-HHMM`.

Inside each turn directory, filenames use the participant display names:

```text
turn-01/
  codex-question.md
  codex-judge-note.md
  claude-answer.md
  judge-ruling.md
```

The flow also writes:

- `manifest.md`
- `messages.jsonl`
- `transcript.md`
- `rules.md`
- `final/scoreboard.md`

For each turn, the flow now also writes the structured payload that the agent actually submitted:

```text
turn-01/
  codex-question.json
  codex-question.md
  codex-judge-note.md
  claude-answer.json
  claude-answer.md
  judge-ruling.json
  judge-ruling.md
```

`messages.jsonl` is an append-only machine-readable log of the runner prompts plus the participant and judge ACP replies.

`transcript.md` is regenerated from that log after each recorded message, so interrupted runs still leave a readable partial transcript with prompts, replies, visible thinking, and tool activity that made it into the ACP session.

## Running

Run the flow from this repo root:

```bash
acpx --approve-all flow run ./flows/ai-battle.flow.ts \
  --input-json '{
    "participantAName": "codex",
    "participantBName": "claude",
    "judgeName": "judge"
  }'
```
