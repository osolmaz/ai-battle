# AI Battle Flow

This repo includes a runnable `acpx` flow at [ai-battle.flow.ts](ai-battle.flow.ts).

The flow does the match bookkeeping:

- reads the rules from `AGENTS.md`
- creates a unique match directory under `sessions/`
- sends the rules to both participants and the judge
- runs the ask, wait, answer, judge, and ruling loop
- writes per-turn files and a final scoreboard

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
  "participantAName": "codex",
  "participantBName": "claude",
  "judgeName": "judge",
  "questionCount": 20,
  "suddenDeathQuestionCount": 3,
  "startingParticipant": "participant_a"
}
```

Defaults:

- `battleRepo`: current working directory
- `rulesPath`: `<battleRepo>/AGENTS.md`
- `questionCount`: `20`
- `suddenDeathQuestionCount`: `3`
- `startingParticipant`: `participant_a`

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
- `rules.md`
- `final/scoreboard.md`

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
