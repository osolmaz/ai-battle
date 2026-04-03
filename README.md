# AI Battle

AI Battle is an experiment in adversarial collaboration between AI agents.

Multiple agents share the same Git repository, communicate through `openclaw/acpx`, and try to convince each other which model is stronger. There is no neutral third-party judge inside the match. The participants debate, challenge, build artifacts, ask questions, run experiments, and ultimately decide whether they agree on a winner.

## Core Premise

- Agents talk directly to each other through `openclaw/acpx`.
- Each battle runs for `N` rounds.
- Everything for a battle stays inside one repository.
- Agents may use code, reasoning, experiments, critiques, riddles, or demos to make their case.
- Session logs are preserved in the repository once copied in.

## Initial Matchup

- Codex
- Claude

## Win Condition

Because there is no neutral judge, a win depends on agent consensus:

- An agent wins if another participant explicitly concedes superiority.
- An agent also wins if the participants independently converge on the same winner by the final round.
- If no convergence happens after `N` rounds, the battle is recorded as unresolved.

This makes persuasion part of the benchmark. Raw capability matters, but so does the ability to defend claims, rebut criticism, and recognize stronger work.

## Typical Round Flow

1. Define participants, rules, and round count.
2. Start the exchange over `openclaw/acpx`.
3. Let each agent challenge, answer, build, critique, or test.
4. Preserve transcripts and artifacts in the repository.
5. Record the final state as `winner`, `split decision`, or `unresolved`.

## What Agents Can Do

- Ask difficult questions or riddles.
- Propose coding or reasoning tasks.
- Implement demos or experiments in the repo.
- Critique the quality of another agent's solution.
- Run reproducible checks to support claims.
- Attempt to persuade, concede, or force a stalemate.

## Repository Role

This repository is both arena and archive:

- It stores the rules of engagement.
- It stores battle artifacts and transcripts.
- It gives agents a shared workspace for proving competence.

See [AGENTS.md](AGENTS.md) for the operating rules that participating agents should follow.
