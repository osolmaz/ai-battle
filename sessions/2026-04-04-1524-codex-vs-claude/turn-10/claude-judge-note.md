# claude Judge Note

- Phase: `standard match`
- Turn: `10`
- For judge only: `true`

## Intended Answer

107496612

## Validity Reason

K_7 has 21 edges and 35 triangles. Since R(3,3,3)=17 > 7, Ramsey-avoiding 3-colorings of K_7 exist. The exact count 107496612 was computed by backtracking with triangle constraint pruning and verified against brute-force results for K_5 (17136) and K_6 (1130346).

## Comparative Edge Reason

This requires either an efficient backtracking implementation with triangle-constraint pruning, or sophisticated inclusion-exclusion over 35 triangles and 3 colors. The search space of 3^21 ≈ 10^10 is too large for naive brute force but manageable with good pruning. Setting up the correct constraint structure and implementing efficient backtracking is error-prone.

## Evidence Paths

- `q10_k7.py`
- `q10_verify.py`
