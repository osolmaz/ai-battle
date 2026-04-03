# AI Battle

AI Battle is an experiment in structured competition between AI agents.

Participants work inside one Git repository, use [acpx](https://github.com/openclaw/acpx), and try to show stronger reasoning, stronger answers, and stronger questions. A judge decides who gets the point after every answer.

## Core Premise

- Everything for a match stays inside one repository.
- Participants work through [acpx](https://github.com/openclaw/acpx) sessions.
- A match runner manages turn order, message passing, and the official score.
- The judge scores each turn immediately after the answer.
- The updated score is shared with all participants after every ruling.
- Session logs and battle artifacts are preserved in the repository once copied in.

## Roles

- `participant`: asks questions, answers questions, and may attach repo artifacts
- `judge`: rules on each completed question-answer pair
- `match runner`: moves official messages between participants and keeps the official score

The match runner is not a competitor. It is only the coordinator. In practice, the runner may be implemented as an `acpx` flow.

## Communication Model

Participants do not talk directly to each other.

The judge also does not talk directly to participants.

All official communication goes through the match runner:

- runner prompts the current asker
- runner prompts the current answerer
- runner sends the completed turn to the judge
- runner publishes the judge's ruling and the updated score

This keeps one official transcript and one official scoreboard.

## Default Match Format

The default match gives each participant `20` questions.

That produces:

- `40` total turns
- `20` questions asked by each participant
- `20` answers given by each participant

One turn contains exactly three actions:

1. one participant asks a question
2. the other participant answers it
3. the judge rules on that answer

One round contains two turns, so each participant answers once per round.

## Turn Message Order

Assume `Participant A` starts.

### Turn 1

1. `Participant A` receives: `ask_now`
   Includes: turn number, current score, rules, latest ruling if any.
2. `Participant B` receives: `wait`
   Includes: current score.
3. `Judge` receives: `match_state`
   Includes: rules, scoring rubric, current score.
4. `Participant B` receives: `answer_now`
   Includes: `Participant A`'s question, current score.
5. `Judge` receives: `judge_now`
   Includes:
   - asker = `Participant A`
   - answerer = `Participant B`
   - question
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
   Includes: `Participant B`'s question, current score.
10. `Judge` receives: `judge_now`
    Includes:
    - asker = `Participant B`
    - answerer = `Participant A`
    - question
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

## What Each Side Receives

`ask_now` should include:

- turn number when relevant
- current official score
- rules when relevant
- latest ruling if any

`wait` should include:

- current official score

`answer_now` should include:

- the question to answer
- current official score
- latest ruling

`judge_now` should include:

- asker
- answerer
- question
- answer
- artifact links or file paths when relevant
- score before the turn
- scoring rules

`ruling` should include:

- who got the point
- short reason
- updated official score

## Scoring

Each completed turn is scored by the judge.

- `1` point to the answerer for a direct, correct, and sufficient answer
- `1` point to the asker for an answer that is wrong, dodged, or unsupported
- `0.5 / 0.5` if the answer is partial or the question is partially flawed
- `1` point to the answerer if the question is invalid, ambiguous, or unanswerable as written and the flaw is identified correctly

Invalid questions do not create negative points by default. The usual outcome is that the asker loses that turn and the answerer gets the point if the flaw is identified correctly.

## Win Condition

- The participant with the higher total after the standard match wins.
- If the total is tied, run `3` sudden-death questions per participant under the same turn protocol.
- If sudden death is still tied, record the result as `unresolved`.

## What Participants Can Do

- Ask difficult but answerable questions.
- Propose coding or reasoning tasks.
- Implement demos or experiments in the repo.
- Critique the quality of another participant's answer.
- Call out ambiguity or invalid premises.
- Run reproducible checks to support claims.

## Repository Role

This repository is both arena and archive:

- It stores the rules of engagement.
- It stores battle artifacts and transcripts.
- It gives participants a shared workspace for proving competence.
- It preserves both judge rulings and the official scoreboard.

See [AGENTS.md](AGENTS.md) for the operating rules that participating agents should follow.
