# claude Judge Note

- Phase: `standard match`
- Turn: `12`
- For judge only: `true`

## Intended Answer

1493

## Validity Reason

This is a standard Burnside's lemma application with the dihedral group D_12 (order 24). Rotation sum = 34752 (contributions from period 4, 12). Vertex-pair reflections each contribute 90 fixed colorings (only the case where one color has both fixed beads works), edge-pair reflections each contribute 90 (assign 2 pairs to each of 3 colors). Total Burnside sum = 34752 + 1080 = 35832, divided by 24 = 1493. Verified by brute-force enumeration of all 34650 colorings grouped by dihedral equivalence.

## Comparative Edge Reason

While Burnside's lemma is standard, the reflection cases require careful case analysis (vertex-pair vs edge-pair reflections, parity constraints on color distributions). A common error is miscounting reflection fixed points or forgetting the distinction between the two types of reflections for even n.

## Evidence Paths

- `q12_necklace.py`
