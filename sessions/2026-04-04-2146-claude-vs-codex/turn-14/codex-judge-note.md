# codex Judge Note

- Phase: `standard match`
- Turn: `14`
- For judge only: `true`

## Intended Answer

117649/46656

## Validity Reason

Well-defined probability problem. Let E_v = expected remaining rolls after rolling value v. The recurrence E_v = 1 + (1/6)·Σ_{w=v+1}^{6} E_w gives E_v = (7/6)^(6-v). Then E[total] = 1 + (1/6)·Σ_{v=1}^{6} E_v = (7/6)^6 = 117649/46656. Since 117649 = 7^6 and 46656 = 6^6 share no common factors, the fraction is in lowest terms. Verified by Monte Carlo simulation (10M trials: 2.5217 vs exact 2.5216).

## Comparative Edge Reason

The recurrence E_v = (7/6)^(6-v) is a non-obvious pattern that emerges only after careful computation. The surprising closed form (7/6)^6 requires either recognizing this geometric pattern or doing the full telescoping. Common errors: miscounting the first roll, confusing 'remaining rolls' with 'total rolls', or setting up the wrong recurrence boundary (e.g., forgetting that after rolling 6, exactly one more roll always occurs). The large numerator/denominator (117649/46656) is hard to guess without the derivation.

## Evidence Paths

- `(none)`
