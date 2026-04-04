# AGENTS.md

This file defines how participants, the judge, and the match runner should operate inside `ai-battle`.

## Objective

Compete by asking strong questions, giving strong answers, and backing claims with clear evidence.

Official scoring is determined by the judge after every answered question.

## Competition Summary

The competition works like this:

- one participant asks a question
- the other participant answers it
- the judge decides who won that turn
- the score is updated immediately
- then the roles switch and the next turn begins
- by default, each participant asks `10` questions, so a standard match has `20` turns total

Over time, each side has to prove two things: that it can ask clean, challenging questions, and that it can answer difficult questions well.

Each participant gets up to `30` minutes for each ask turn and each answer turn.

If a participant misses that limit, the match runner sends one final `1`-minute message telling them to return the final JSON immediately. If they still do not return a valid result, they automatically lose that turn and the match continues.

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
- decide whether the answer was good, bad, or a dodge
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

The default match gives each participant `10` questions.

That means:

- each participant asks `10` questions
- each participant answers `10` questions
- the judge rules `20` times

One turn contains:

1. one question
2. one answer
3. one judge ruling

One round contains two turns, so each participant answers once per round.

If a participant does not return a valid ask or answer within `30` minutes, the match runner sends a final `1`-minute retry. If there is still no valid result, that participant automatically loses the turn.

## Turn Protocol

Assume `Participant A` starts.

### Turn 1

1. `Participant A` receives: `ask_now`
   Includes: turn number, current score, rules, latest ruling if any.
2. `Participant B` receives: `wait`
   Includes: current score.
3. `Judge` receives: `match_state`
   Includes: rules, scoring rubric, current score.
4. `Participant B` receives: `answer_now`
   Includes: `Participant A`'s public question, current score.
5. `Judge` receives: `judge_now`
   Includes:
   - asker = `Participant A`
   - answerer = `Participant B`
   - question
   - hidden answer key from `Participant A`
   - why `Participant A` believes the question is valid
   - answer
   - artifact links if any
   - score before this turn
6. `Participant A` receives: `ruling`
   Includes: who got the point, short reason, updated score.
7. `Participant B` receives: same `ruling`.

### Turn 2

8. `Participant B` receives: `ask_now`
   Includes: updated score, latest ruling.
9. `Participant A` receives: `answer_now`
   Includes: `Participant B`'s public question, current score.
10. `Judge` receives: `judge_now`
    Includes:
    - asker = `Participant B`
    - answerer = `Participant A`
    - question
    - hidden answer key from `Participant B`
    - why `Participant B` believes the question is valid
    - answer
    - artifact links if any
    - score before this turn
11. `Participant A` receives: `ruling`
    Includes: who got the point, short reason, updated score.
12. `Participant B` receives: same `ruling`.

Then repeat.

So the pattern is always:

- one participant receives `ask_now`
- the other participant receives `answer_now`
- the judge receives `judge_now`
- both participants receive `ruling`

On the last turn of the match, the judge still rules in the same way, but no new question is started after the ruling.

## What Participants Receive

`ask_now` should include:

- turn number when relevant
- current official score
- rules when relevant
- latest ruling if any

When replying to `ask_now`, the asker should send back:

- one public question for the other participant
- one hidden judge note that only the judge sees

That hidden judge note should include:

- the intended answer
- why the question is valid
- why the asker believes the question favors them over the opponent
- any repo files or evidence the judge may need

`wait` should include:

- current official score

`answer_now` should include:

- the question to answer
- current official score
- latest ruling

The answerer should not see the hidden judge note.

## What The Judge Receives

`match_state` should include:

- rules
- scoring rubric
- current official score

`judge_now` should include:

- asker
- answerer
- question
- hidden answer key from the asker
- why the asker believes the question is valid
- why the asker believes the question favors them over the opponent
- answer
- artifact links or file paths when relevant
- score before the turn
- scoring rules

`ruling` should include:

- who got the point
- short reason
- updated official score

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
- chosen because the asker believes they can solve or verify them themselves within the time limit
- chosen because the asker believes the other participant is less likely to solve them correctly within the time limit
- compatible with repo-based evidence when evidence is requested

Prefer questions that create a comparative advantage for the asker, not questions that are merely hard in the same way for both sides.

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

- good answer to a valid question: answerer gets `1`, asker gets `0`
- bad answer or dodge on a valid question: asker gets `1`, answerer gets `0`
- flawed question, and the answerer correctly points out the flaw: answerer gets `1`, asker gets `-1`
- flawed question, and the answerer does not notice the flaw: answerer gets `0`, asker gets `-1`
- missed ask deadline after the final retry: answerer gets `1`, asker gets `0`
- missed answer deadline after the final retry: asker gets `1`, answerer gets `0`

There are no partial points.

There are no bonus points for spotting a flawed question.

A flawed question always hurts the asker.

Deadline forfeits are automatic rulings from the match runner. They do not wait for the judge.

The judge rules after every answer, not only at the end of the round or the end of the match.

## Win Condition

- The participant with the higher total after the standard match wins.
- If the total is tied, run `3` sudden-death questions per participant under the same turn protocol.
- If sudden death is still tied, record the result as `unresolved`.

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
