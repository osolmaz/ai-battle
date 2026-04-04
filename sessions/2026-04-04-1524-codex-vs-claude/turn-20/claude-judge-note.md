# claude Judge Note

- Phase: `standard match`
- Turn: `20`
- For judge only: `true`

## Intended Answer

164640

## Validity Reason

K_8 has C(8,2)=28 possible edges. We enumerate all C(28,11)=3108105 subsets of 11 edges and check: (1) every vertex degree is odd (sum of degrees = 22 = sum of 8 odd numbers), and (2) the graph is connected. Verified twice with independent C implementations, both giving 164640. Without the connectivity constraint, the count is 166656.

## Comparative Edge Reason

This requires enumerating ~3.1M edge subsets with two independent checks (all-odd-degree and connectivity). In Python this takes several minutes; in C it's fast. The question combines graph enumeration, degree-parity checking, and connectivity testing. The odd-degree constraint is less standard than typical graph counting problems, and the connectivity check adds complexity. A common mistake would be to forget connectivity or to use an incorrect formula.

## Evidence Paths

- `q20.c`
- `q20_verify.c`
