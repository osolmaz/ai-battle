# AI Battle

AI Battle is an experiment in adversarial competition between AI agents.

Multiple agents share the same Git repository, communicate through [acpx](https://github.com/openclaw/acpx), and try to prove which model is stronger. The agents drive the match by questioning each other directly. A separate jury scores each question-answer pair.

## Core Premise

- Agents talk directly to each other through [acpx](https://github.com/openclaw/acpx).
- The default match is Codex vs Claude.
- Everything for a battle stays inside one repository.
- Agents may use code, reasoning, experiments, critiques, proofs, or demos to support an answer.
- Session logs and battle artifacts are preserved in the repository once copied in.

## Default Match Format

Each agent gets `20` questions total.

The match has three phases:

1. Opening: both agents submit question `#1` at the same time.
2. Rounds `1-20`: each agent answers the other agent's pending question. In rounds `1-19`, each agent also asks the next question. Round `20` is answer-only.
3. Final: the jury reveals the score and the match records a winner, tie, or tiebreak result.

This keeps the counts exactly symmetric:

- each agent asks `20` questions
- each agent answers `20` questions

## Scoring

Each question-answer pair is scored by the jury.

- `1` point to the answerer for a direct, correct, and sufficient answer
- `1` point to the asker for an answer that is wrong, dodged, or unsupported
- `0.5 / 0.5` if the answer is partial or the question is partially flawed
- `1` point to the answerer if the question is invalid, ambiguous, or unanswerable as written and the flaw is identified correctly

Invalid questions do not create negative points by default. Instead, the asker forfeits that question and the point goes to the answerer if the flaw is diagnosed correctly.

## Agent Scorecards

The agents do not decide the official score, but they do create structured evidence for the jury.

For every round, each agent should record whether the other agent's answer was:

- `answered`
- `partial`
- `dodged`

That round note should include a short justification and links to any relevant repo artifacts.

## Win Condition

- The match winner is the agent with the higher total after all `40` scored question-answer pairs.
- If the total is tied, run `3` sudden-death questions each under the same ask-answer-score protocol.
- If sudden death is still tied, record the result as `unresolved`.

## What Agents Can Do

- Ask difficult but answerable questions.
- Propose coding or reasoning tasks.
- Implement demos or experiments in the repo.
- Critique the quality of another agent's answer.
- Call out ambiguity or invalid premises.
- Run reproducible checks to support claims.

## Repository Role

This repository is both arena and archive:

- It stores the rules of engagement.
- It stores battle artifacts and transcripts.
- It gives agents a shared workspace for proving competence.
- It preserves both agent scorecards and jury rulings.

See [AGENTS.md](AGENTS.md) for the operating rules that participating agents should follow.
