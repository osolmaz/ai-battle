# codex Judge Note

- Phase: `standard match`
- Turn: `7`
- For judge only: `true`

## Intended Answer

With explicit `rulesPath = "docs/custom-rules.md"`, the code does `path.resolve(input.rulesPath ?? path.join(battleRepo, "AGENTS.md"))`, so it resolves relative to the process cwd, not `battleRepo`. The actual path read is `/tmp/runner/docs/custom-rules.md`. If `rulesPath` is omitted, the fallback expression is `path.join(battleRepo, "AGENTS.md")`, so the path becomes `/repo/battle/AGENTS.md`.

## Validity Reason

This is deterministically answerable from `prepareMatch(...)` plus standard Node `path.resolve` behavior. The inputs are fully specified, and there is a single correct path in each case.

## Evidence Paths

- `flows/ai-battle.flow.ts`
