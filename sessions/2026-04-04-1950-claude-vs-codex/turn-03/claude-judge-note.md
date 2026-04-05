# claude Judge Note

- Phase: `standard match`
- Turn: `3`
- For judge only: `true`

## Intended Answer

((a -> b) -> b) -> (a -> a -> b) -> b

## Validity Reason

The question is self-contained: the language fragment and typing discipline are specified, and the expression has a unique principal type up to alpha-renaming of type variables. Under HM, `b` is generalized at the `let`, so the two occurrences in `s b b` may instantiate differently. The principal type is `((a -> b) -> b) -> (a -> a -> b) -> b`.

## Comparative Edge Reason

This targets symbolic type inference and, specifically, the subtle interaction between let-generalization and repeated use of a polymorphic binding. A monomorphic reading makes `s b b` look impossible, so it is a good discriminator for precise formal reasoning rather than shallow pattern matching.

## Evidence Paths

- `(none)`
