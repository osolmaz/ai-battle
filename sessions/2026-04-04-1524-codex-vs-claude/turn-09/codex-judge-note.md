# codex Judge Note

- Phase: `standard match`
- Turn: `9`
- For judge only: `true`

## Intended Answer

958206171

## Validity Reason

The objects are finite and completely specified, so the count is uniquely defined. A correct solution can be obtained by Burnside's lemma on the dihedral group of order 240, together with a transfer-matrix / automaton count over ordered triples of distinct recent colors and the running sum modulo 11. For reflections, every fixed coloring is impossible because reflection forces an equal-color pair at cyclic distance at most 3, violating the local constraint.

## Comparative Edge Reason

This favors me because the efficient route mixes symmetry reduction with a nontrivial cyclic boundary DP. The natural solution is a carefully coded automaton over the last three colors plus residue mod 11, evaluated across the divisors of 120; it is exact and checkable, but easy to mishandle without strong implementation discipline.

## Evidence Paths

- `(none)`
