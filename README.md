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

For each turn, messages should move in this order:

1. The runner tells the current asker to ask one question.
   The message includes the current score and the latest ruling.
2. The asker sends back one question.
3. The runner sends that question to the current answerer.
   The message includes the current score and the latest ruling.
4. The answerer sends back an answer and any artifact links or file paths.
5. The runner sends the completed question-answer pair to the judge.
   That packet includes the score before the turn.
6. The judge returns a ruling immediately.
7. The runner updates the official score.
8. The runner sends the ruling and the updated score to both participants.
9. Roles switch for the next turn.

Every ask prompt, answer prompt, and ruling message should include the current official score.

## What Each Side Receives

The current asker receives:

- notice that it is their turn to ask
- the current score
- the latest ruling

The current answerer receives:

- the question to answer
- the current score
- the latest ruling

The judge receives:

- the completed question-answer pair
- artifact links or file paths when relevant
- the score before the turn
- the scoring rules

After the judge rules, both participants receive:

- the ruling
- the short reason
- the updated score

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
