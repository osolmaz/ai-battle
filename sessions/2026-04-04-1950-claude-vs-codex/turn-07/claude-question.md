# claude Question

- Phase: `standard match`
- Turn: `7`
- Asker: `claude`
- Answerer: `codex`
- Score before turn: `claude 3, codex 3`

## Question

Work in a call-by-value lambda calculus with integers, `+`, `reset`, and `shift`.

Values: `v ::= n | \x. e`

Pure evaluation contexts for `shift` capture:
`E ::= [ ] | E e | v E | E + e | v + E`

Reduction rules:
1. `(\x. e) v -> e[v/x]`
2. `n1 + n2 -> n` with ordinary integer addition
3. `reset E[shift k. e] -> reset (e[(\x. reset E[x]) / k])`, where the captured `E` contains no `reset`
4. `reset v -> v`

Evaluation is left-to-right call-by-value.

What integer does this closed term reduce to?

`reset (10 + ((\x. x + 1) (shift k. ((k 2) + reset (100 + (shift h. (k (h 3))))))))`

Answer with just the integer.
