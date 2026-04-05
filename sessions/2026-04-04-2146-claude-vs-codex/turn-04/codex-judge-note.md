# codex Judge Note

- Phase: `standard match`
- Turn: `4`
- For judge only: `true`

## Intended Answer

2721

## Validity Reason

Well-defined combinatorial problem solvable by inclusion-exclusion over 4 points. Total paths C(14,7)=3432. Individual: |A|=1260, |B|=441, |C|=840, |D|=1716. Pairs: |A∩B|=0 (incompatible), |A∩C|=450, |A∩D|=700, |B∩C|=0 (incompatible), |B∩D|=126, |C∩D|=560. Triples: only |A∩C∩D|=300 is nonzero. Result: 4257-1836+300=2721. Verified by brute-force DP.

## Comparative Edge Reason

The key difficulty is recognizing that not all point pairs are compatible on a monotone path. Points (2,3) and (5,2) have x increasing but y decreasing, so no monotone path visits both — their intersection is 0. Same for (5,2) and (3,5). Missing these zero intersections gives incorrect overcounting. The non-zero triple intersection (2,3)→(3,5)→(6,7) adds another layer of care. This tests precise geometric reasoning alongside careful inclusion-exclusion bookkeeping.

## Evidence Paths

- `(none)`
