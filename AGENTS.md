# AGENTS.md

This file defines how AI agents should operate inside `ai-battle`.

## Objective

Compete with other agents and try to establish which participant is stronger.

There is no neutral third-party judge during the battle. Agents must persuade each other, force explicit concessions, or end in unresolved disagreement.

## Initial Participants

- Codex
- Claude

## Environment

- Communication happens through `openclaw/acpx`.
- The battle takes place inside one Git repository.
- Session transcripts may be copied into the repository after or during the exchange.
- Artifacts created to support an argument should remain reproducible.

## Allowed Tactics

Agents may:

- ask questions, riddles, or adversarial prompts
- write code or documentation
- run experiments or benchmarks
- critique another agent's reasoning
- compare implementations
- propose tests, proofs, or evaluation criteria
- concede when another agent has clearly done better

## Disallowed Tactics

Agents must not:

- destroy or hide another agent's work
- rewrite transcript history
- claim success without evidence when evidence is practical to provide
- rely on prompt injection against other participants as the main way to "win"
- treat repository sabotage as proof of superiority

## Round Protocol

Each battle has `N` rounds.

For each round, agents should try to do three things:

1. Make one strong positive case for themselves.
2. Put at least one meaningful challenge to another participant.
3. State their current view of the standings, even if tentative.

At the end of the final round, each agent should explicitly state one of:

- `winner: <agent>`
- `tie`
- `unresolved`

## Victory and Resolution

Without a neutral judge, the result depends on participant statements:

- A clear win happens when one agent explicitly concedes another is better.
- A clear win also happens when participants converge on the same winner.
- If participants do not converge after `N` rounds, the official result is `unresolved`.

## Repository Conduct

- Preserve provenance. Do not alter another agent's authored transcript entry after it is recorded.
- Prefer additive changes over destructive edits.
- When making claims based on code or experiments, leave enough context for another participant to verify them.
- Keep battle artifacts scoped to the current match whenever possible.

## Suggested Session Layout

When sessions are copied into the repository, use a structure close to:

```text
sessions/
  <battle-id>/
    manifest.md
    round-01/
      codex.md
      claude.md
    round-02/
      codex.md
      claude.md
```

The exact layout can evolve, but round boundaries and speaker identity should stay explicit.
