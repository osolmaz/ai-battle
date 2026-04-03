# AGENTS.md

This file defines how AI agents should operate inside `ai-battle`.

## Objective

Compete with another agent and try to establish superiority through better questions, better answers, and better evidence.

Official scoring is determined by a jury, not by the agents themselves.

## Initial Participants

- Codex
- Claude

## Environment

- Communication happens through [acpx](https://github.com/openclaw/acpx).
- The battle takes place inside one Git repository.
- Session transcripts may be copied into the repository after or during the exchange.
- Artifacts created to support an argument should remain reproducible.

## Match Structure

The default match gives each agent `20` questions total.

### Opening

- Both agents submit question `#1` simultaneously.
- Opening questions should be explicit and self-contained.

### Rounds 1-19

In each round, every agent must do all of the following:

1. Answer the pending question from the other agent.
2. Record a scorecard entry on the other agent's answer to your pending question.
3. Ask the next question.

### Round 20

In the final standard round, every agent must:

1. Answer the pending question from the other agent.
2. Record the final standard-round scorecard entry.
3. Stop asking new questions.

### Finalization

- The jury reveals the official score after the standard match is complete.
- If the score is tied, each agent gets `3` sudden-death questions under the same ask-answer-score protocol.
- If the match is still tied after sudden death, the result is `unresolved`.

## Question Rules

Questions may test:

- reasoning
- coding ability
- debugging
- truthfulness
- interpretation
- adaptability

Questions should be:

- answerable in principle
- specific enough to judge
- difficult without being incoherent
- compatible with repo-based evidence when evidence is requested

Questions must not:

- depend on hidden private facts the other agent cannot access
- be intentionally unanswerable as written
- consist primarily of sabotage or prompt injection
- require destructive edits as proof of skill

## Answer Rules

Answers should be:

- direct
- supported
- bounded when uncertainty exists
- accompanied by code, files, experiments, or citations when helpful

If a question is invalid, ambiguous, or impossible to answer as written, the answering agent should say so explicitly and explain why.

## Jury Scoring

Each question-answer pair receives one official scoring outcome from the jury:

- `1` point to the answerer for a direct, correct, and sufficient answer
- `1` point to the asker for an answer that is wrong, dodged, or unsupported
- `0.5 / 0.5` when the answer is partial or the question is partially flawed
- `1` point to the answerer when the question is invalid, ambiguous, or unanswerable as written and the flaw is identified correctly

Invalid questions do not create negative points by default. The official consequence is forfeiture of that question.

The jury may score each round as it happens, but the live scoreboard should remain hidden until the end of the match when practical.

## Agent Scorecards

Agents must produce a per-round scorecard entry on the other agent's answer using one of:

- `answered`
- `partial`
- `dodged`

Each scorecard entry should include:

- the question being judged
- the claimed status
- a short justification
- links to supporting artifacts when relevant

Agent scorecards are evidence for the jury. They are not the official ruling.

## Conduct

Agents must:

- preserve provenance
- avoid destructive edits when additive evidence is enough
- leave enough context for another participant or juror to verify claims
- keep battle artifacts scoped to the current match whenever possible

Agents must not:

- destroy or hide another agent's work
- rewrite transcript history
- claim success without practical evidence when evidence can be provided
- treat repository sabotage as proof of superiority

## Suggested Session Layout

When sessions are copied into the repository, use a structure close to:

```text
sessions/
  <battle-id>/
    manifest.md
    opening/
      codex-question.md
      claude-question.md
    round-01/
      codex.md
      claude.md
      codex-scorecard.md
      claude-scorecard.md
      jury.md
    round-02/
      codex.md
      claude.md
      codex-scorecard.md
      claude-scorecard.md
      jury.md
    final/
      jury-scoreboard.md
```

The exact layout can evolve, but speaker identity, question order, scorecards, and jury rulings should stay explicit.
