# claude Question

- Phase: `standard match`
- Turn: `3`
- Asker: `claude`
- Answerer: `codex`
- Score before turn: `claude 1, codex 1`

## Question

Work in standard Hindley-Milner type inference with let-polymorphism, no recursive `let`, and only variables, lambda abstraction, application, and `let`. Types use only `->`, which associates to the right. What is the principal type, up to renaming of type variables, of:

`let b = \f. \g. \x. f (g x) in let s = \f. \g. \x. f x (g x) in s b b`

Answer with just the type.
