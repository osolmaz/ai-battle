# AI Battle

AI Battle is an experiment in structured competition between participant AI agents.

Participants compete by asking hard questions, giving strong answers, and showing stronger reasoning than the other side. A judge decides who gets the point after every answer.

The competition works like this:

- one participant asks a question
- the other participant answers it
- the judge decides who won that turn
- the score is updated immediately
- then the roles switch and the next turn begins
- by default, each participant asks `10` questions, so a standard match has `20` turns total

Over time, each side has to prove two things: that it can ask clean, challenging questions, and that it can answer difficult questions well. The match is meant to reward both offensive skill and defensive skill, not just one or the other.

Each participant gets up to `30` minutes for each ask turn and each answer turn.

If a participant misses that limit, the match runner sends one final `1`-minute message telling them to return the final JSON immediately. If they still do not return a valid result, they automatically lose that turn and the match continues.

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

The default match gives each participant `10` questions.

That produces:

- `20` total turns
- `10` questions asked by each participant
- `10` answers given by each participant

One turn contains exactly three actions:

1. one participant asks a question
2. the other participant answers it
3. the judge rules on that answer

One round contains two turns, so each participant answers once per round.

If a participant does not return a valid ask or answer within `30` minutes, the match runner sends a final `1`-minute retry. If there is still no valid result, that participant automatically loses the turn.

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

## What Each Side Receives

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

## Scoring

Each completed turn is scored by the judge.

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

The runnable `acpx` flow for this repo lives at [flows/ai-battle.flow.ts](flows/ai-battle.flow.ts). See [flows/README.md](flows/README.md) for setup and run instructions.
