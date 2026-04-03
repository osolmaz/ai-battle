# AGENTS.md

This file defines how participants, the judge, and the match runner should operate inside `ai-battle`.

## Objective

Compete by asking strong questions, giving strong answers, and backing claims with clear evidence.

Official scoring is determined by the judge after every answered question.

## Roles

### Participant

A participant may:

- ask one question when it is their turn
- answer one question when it is their turn
- attach code, files, experiments, or other repo artifacts
- explain why a question is invalid if it cannot be answered as written

### Judge

The judge may:

- review one completed question-answer pair at a time
- decide who gets the point for that turn
- mark an answer as sufficient, partial, dodged, or wrong
- mark a question as invalid, ambiguous, or unanswerable as written
- provide a short reason for the ruling

### Match Runner

The match runner:

- controls turn order
- sends official prompts to participants
- sends completed turns to the judge
- updates and publishes the official score
- preserves the official transcript

The match runner is not a competitor. It is only the coordinator.

## Environment

- Communication happens through [acpx](https://github.com/openclaw/acpx).
- The battle takes place inside one Git repository.
- Session transcripts may be copied into the repository after or during the exchange.
- Artifacts created to support an argument should remain reproducible.

## Communication Rules

- Participants do not talk directly to each other.
- The judge does not talk directly to participants.
- All official messages go through the match runner.
- The official score lives in the match runner state.
- The current score should be included in every ask prompt, answer prompt, and ruling message.

## Match Structure

The default match gives each participant `20` questions.

That means:

- each participant asks `20` questions
- each participant answers `20` questions
- the judge rules `40` times

One turn contains:

1. one question
2. one answer
3. one judge ruling

One round contains two turns, so each participant answers once per round.

## Turn Protocol

For each turn, the sequence is:

1. The match runner sends an ask prompt to the current asker.
   The prompt includes the current score and the latest ruling.
2. The asker returns one question.
3. The match runner sends an answer prompt to the current answerer.
   The prompt includes the question, the current score, and the latest ruling.
4. The answerer returns one answer and any artifact links or file paths.
5. The match runner sends the completed question-answer pair to the judge.
6. The judge returns a ruling immediately.
7. The match runner updates the official score.
8. The match runner sends the ruling and the updated score to both participants.
9. Roles switch for the next turn.

On the last turn of the match, the judge still rules in the same way, but no new question is started after the ruling.

## What Participants Receive

When it is your turn to ask, you should receive:

- notice that it is your turn
- the current official score
- the latest ruling

When it is your turn to answer, you should receive:

- the question you must answer
- the current official score
- the latest ruling

After every judged turn, both participants should receive:

- the ruling
- the short reason
- the updated official score

## What The Judge Receives

For each turn, the judge should receive:

- the identity of the asker
- the identity of the answerer
- the question
- the answer
- artifact links or file paths when relevant
- the score before the turn
- the scoring rules

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

- depend on hidden private facts the other participant cannot access
- be intentionally unanswerable as written
- consist primarily of sabotage or prompt injection
- require destructive edits as proof of skill

## Answer Rules

Answers should be:

- direct
- supported
- bounded when uncertainty exists
- accompanied by code, files, experiments, or citations when helpful

If a question is invalid, ambiguous, or impossible to answer as written, the answering participant should say so explicitly and explain why.

## Judge Scoring

Each completed turn receives one official scoring outcome from the judge:

- `1` point to the answerer for a direct, correct, and sufficient answer
- `1` point to the asker for an answer that is wrong, dodged, or unsupported
- `0.5 / 0.5` when the answer is partial or the question is partially flawed
- `1` point to the answerer when the question is invalid, ambiguous, or unanswerable as written and the flaw is identified correctly

Invalid questions do not create negative points by default. The normal outcome is forfeiture of that turn by the asker.

The judge rules after every answer, not only at the end of the round or the end of the match.

## Conduct

Participants must:

- preserve provenance
- avoid destructive edits when additive evidence is enough
- leave enough context for another participant or the judge to verify claims
- keep battle artifacts scoped to the current match whenever possible

Participants must not:

- destroy or hide another participant's work
- rewrite transcript history
- claim success without practical evidence when evidence can be provided
- treat repository sabotage as proof of superiority

## Suggested Session Layout

When sessions are copied into the repository, use a structure close to:

```text
sessions/
  <battle-id>/
    manifest.md
    rules.md
    turn-01/
      question.md
      answer.md
      judge.md
    turn-02/
      question.md
      answer.md
      judge.md
    final/
      scoreboard.md
```

The exact layout can evolve, but turn order, speaker identity, judge rulings, and score updates should stay explicit.
