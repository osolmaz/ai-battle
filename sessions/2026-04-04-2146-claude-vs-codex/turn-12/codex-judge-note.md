# codex Judge Note

- Phase: `standard match`
- Turn: `12`
- For judge only: `true`

## Intended Answer

201

## Validity Reason

Well-defined number theory problem. p(x) = x^5 - 5x^3 + 4x factors as x(x^2-1)(x^2-4) = (x-2)(x-1)x(x+1)(x+2), the product of 5 consecutive integers centered at x. The product of any k consecutive integers is always divisible by k!, so p(n) is always divisible by 5! = 120 for every integer n. Therefore all 201 integers from -100 to 100 satisfy the condition. Verified computationally.

## Comparative Edge Reason

The natural instinct is to solve via CRT (120=8×3×5), checking residues modulo each prime power — a tedious multi-case analysis. The elegant path is factoring x^5-5x^3+4x = (x-2)(x-1)x(x+1)(x+2) and recognizing the '5 consecutive integers ⇒ divisible by 5!' property. The surprising answer — every single integer works — may cause the opponent to doubt their result or waste time on CRT verification. An opponent who doesn't spot the factorization may produce an incorrect CRT-based count.

## Evidence Paths

- `(none)`
