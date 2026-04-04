# codex Question

- Phase: `standard match`
- Turn: `7`
- Asker: `codex`
- Answerer: `claude`
- Score before turn: `codex 4, claude 2`

## Question

In `prepareMatch` inside `flows/ai-battle.flow.ts`, assume `battleRepo = "/repo/battle"`, the process is launched from cwd `"/tmp/runner"`, and the input explicitly sets `rulesPath = "docs/custom-rules.md"`. What absolute path does the flow actually pass to `fs.readFile`, and why? Also state what path would be used instead if `rulesPath` were omitted.
